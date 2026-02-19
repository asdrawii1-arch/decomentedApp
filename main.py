import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, QFileDialog,
    QDialog, QDialogButtonBox, QComboBox, QSpinBox, QMessageBox,
    QTabWidget, QGroupBox, QFormLayout, QTextEdit, QListWidget,
    QListWidgetItem, QProgressBar, QProgressDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtWidgets import QApplication
# test
# إضافة المسارات
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

# التحقق من توفر مكتبة السكانر
SCANNER_AVAILABLE = False
SCANNER_COUNT = 0
try:
    import win32com.client
    SCANNER_AVAILABLE = True
    # التحقق من عدد السكانرات المتصلة
    try:
        _wia_manager = win32com.client.Dispatch("WIA.DeviceManager")
        SCANNER_COUNT = _wia_manager.DeviceInfos.Count
    except:
        SCANNER_COUNT = 0
except ImportError:
    SCANNER_AVAILABLE = False
    SCANNER_COUNT = 0

from database.db_manager import DatabaseManager
from app.filename_parser import FilenameParser, ImageSequenceHandler
from app.ui_styles import MAIN_STYLESHEET
from app.constants import COLORS, FONT_SIZES, DIMENSIONS, ICONS
from app.image_manager import ImageManager
from app.document_viewer import DocumentViewerWindow
from app.helpers import ValidationHelper, DateHelper, ExportHelper, DatabaseBackupHelper

# استيراد نوافذ الحوار من الوحدة الجديدة
from app.dialogs import (
    AddDocumentDialog,
    AttachmentDetailsDialog,
    ImportImagesDialog,
    DestructionFormDialog
)
from app.dialogs.utils import choose_year_folder

# استيراد OCR اختياري
try:
    from app.ocr_extractor import OCRExtractor
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[WARNING] مكتبة easyocr غير مثبتة - ميزة استخراج المضمون غير متاحة")


# =========================================================================
# النافذة الرئيسية
# Main Window
# =========================================================================
class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager('documents.db')
        self.image_manager = ImageManager('documents')
        self.setWindowTitle('برنامج أرشفة الكتب الرسمية')
        self.setGeometry(0, 0, 1200, 700)
        
        # تطبيق الأسلوب
        self.setStyleSheet(MAIN_STYLESHEET)
        
        self.init_ui()
        self.load_documents()
    
    def init_ui(self):
        """إنشاء واجهة المستخدم"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('البحث:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('ابحث حسب الرقم أو التاريخ أو الجهة...')
        self.search_input.textChanged.connect(self.search_documents)
        search_layout.addWidget(self.search_input)
        
        # حقل البحث
        search_field_label = QLabel('البحث في:')
        search_layout.addWidget(search_field_label)
        self.search_field = QComboBox()
        self.search_field.addItems(['اسم الوثيقة', 'المضمون', 'التاريخ', 'الجهة', 'التصنيف'])
        self.search_field.currentTextChanged.connect(self.search_documents)
        search_layout.addWidget(self.search_field)
        
        main_layout.addLayout(search_layout)
        
        # شريط الأدوات
        toolbar_layout = QHBoxLayout()
        
        add_btn = QPushButton('➕ إضافة وثيقة')
        add_btn.clicked.connect(self.add_document)
        toolbar_layout.addWidget(add_btn)
        
        import_btn = QPushButton('📁 استيراد صور')
        import_btn.clicked.connect(self.import_images)
        toolbar_layout.addWidget(import_btn)
        
        view_btn = QPushButton('👁️ عرض الوثيقة')
        view_btn.clicked.connect(self.view_document)
        toolbar_layout.addWidget(view_btn)
        
        delete_btn = QPushButton('🗑️ حذف')
        delete_btn.clicked.connect(self.delete_document)
        toolbar_layout.addWidget(delete_btn)
        
        destruction_form_btn = QPushButton('📋 استمارة إتلاف')
        destruction_form_btn.clicked.connect(self.open_destruction_form)
        toolbar_layout.addWidget(destruction_form_btn)
        
        toolbar_layout.addStretch()
        
        select_all_btn = QPushButton('✓ تحديد الكل')
        select_all_btn.clicked.connect(self.select_all_documents)
        toolbar_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton('✗ إلغاء التحديد')
        deselect_all_btn.clicked.connect(self.deselect_all_documents)
        toolbar_layout.addWidget(deselect_all_btn)
        
        delete_selected_btn = QPushButton('🗑️ حذف المحددة')
        delete_selected_btn.clicked.connect(self.delete_selected_documents)
        toolbar_layout.addWidget(delete_selected_btn)
        
        refresh_btn = QPushButton('🔄 تحديث')
        refresh_btn.clicked.connect(self.load_documents)
        toolbar_layout.addWidget(refresh_btn)
        main_layout.addLayout(toolbar_layout)

        # محتوى رئيسي: قائمة السنوات على اليسار والجدول على اليمين
        content_layout = QHBoxLayout()

        # قائمة السنوات
        self.years_list = QListWidget()
        self.years_list.setMaximumWidth(220)
        self.years_list.itemClicked.connect(self.on_year_selected)
        content_layout.addWidget(self.years_list)

        # جدول الوثائق
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(8)
        self.documents_table.setHorizontalHeaderLabels([
            '☑', 'رقم الوثيقة', 'التاريخ', 'المضمون', 'جهة الإصدار', 'التصنيف', 'المادة القانونية', 'عدد الصور'
        ])
        self.documents_table.setColumnWidth(0, 40)  # Checkbox column
        self.documents_table.setColumnWidth(1, 100)
        self.documents_table.setColumnWidth(2, 100)
        self.documents_table.setColumnWidth(3, 200)
        self.documents_table.setColumnWidth(4, 150)
        self.documents_table.setColumnWidth(5, 100)
        self.documents_table.setColumnWidth(6, 180)
        self.documents_table.setColumnWidth(7, 80)
        self.documents_table.setAlternatingRowColors(True)
        self.documents_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.documents_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.documents_table.selectionModel().selectionChanged.connect(self.on_row_selection_changed)
        
        # ضع الجدول داخل تخطيط عمودي (للسماح بعناصر إضافية إن لزم)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.documents_table)
        content_layout.addLayout(right_layout)

        main_layout.addLayout(content_layout)

        central_widget.setLayout(main_layout)
    
    def load_documents(self, year_filter=None):
        """تحميل قائمة الوثائق. إذا تم تمرير `year_filter` (مثل '2025')، يعرض الوثائق المرتبطة بتلك السنة فقط."""
        # تحديث قائمة السنوات
        self.refresh_years()

        self.documents_table.setRowCount(0)
        documents = self.db.get_all_documents()

        # إذا تم تحديد سنة، احصل على معرفات الوثائق التي تحتوي صورها في مجلد تلك السنة
        filter_ids = None
        if year_filter:
            filter_ids = set(self.db.get_document_ids_by_image_year(year_filter))
        
        # Disable updates for better performance
        self.documents_table.setUpdatesEnabled(False)
        
        for idx, doc in enumerate(documents):
            # إذا يوجد فلتر سنة وتوثيقة غير موجودة ضمن تلك السنة، تجاهلها
            if filter_ids is not None and doc[0] not in filter_ids:
                continue
            row = self.documents_table.rowCount()
            self.documents_table.insertRow(row)
            
            # Checkbox column
            checkbox = QCheckBox()
            checkbox.setStyleSheet('margin-left: 10px;')
            checkbox.stateChanged.connect(lambda state, row=row: self.on_checkbox_changed(row, state))
            self.documents_table.setCellWidget(row, 0, checkbox)
            
            # رقم الوثيقة (من اسم الوثيقة)
            doc_name = doc[1] or ''
            # استخراج الرقم من اسم الوثيقة (مثل: "65 في 23-3-2025" -> "65")
            doc_number = doc_name.split()[0] if doc_name else ''
            item = QTableWidgetItem(doc_number)
            item.setData(Qt.ItemDataRole.UserRole, doc[0])  # احفظ معرف الوثيقة
            self.documents_table.setItem(row, 1, item)
            
            # التاريخ
            self.documents_table.setItem(row, 2, QTableWidgetItem(doc[2] or ''))
            
            # المضمون (العنوان)
            self.documents_table.setItem(row, 3, QTableWidgetItem(doc[3] or ''))
            
            # جهة الإصدار
            self.documents_table.setItem(row, 4, QTableWidgetItem(doc[4] or ''))
            
            # التصنيف
            self.documents_table.setItem(row, 5, QTableWidgetItem(doc[5] or ''))
            
            # المادة القانونية
            self.documents_table.setItem(row, 6, QTableWidgetItem(doc[6] or ''))
            
            # عدد الصور
            images = self.db.get_document_images(doc[0])
            self.documents_table.setItem(row, 7, QTableWidgetItem(str(len(images))))
            
            # Process events every 50 rows to keep UI responsive
            if idx % 50 == 0:
                QApplication.processEvents()
        
        # Re-enable updates
        self.documents_table.setUpdatesEnabled(True)

    def refresh_years(self):
        """تحديث قائمة السنوات من مجلد `documents/`"""
        from pathlib import Path
        import os
        docs_dir = Path(self.image_manager.storage_dir)
        self.years_list.clear()
        # إضافة خيار عرض الكل
        all_item = QListWidgetItem('الكل')
        self.years_list.addItem(all_item)
        if docs_dir.exists():
            for d in sorted(docs_dir.iterdir()):
                if d.is_dir() and d.name.isdigit():
                    item = QListWidgetItem(d.name)
                    self.years_list.addItem(item)

    def on_year_selected(self, item):
        text = item.text()
        if text == 'الكل':
            self.load_documents(None)
        else:
            self.load_documents(text)
    
    def add_document(self):
        """إضافة وثيقة جديدة"""
        dialog = AddDocumentDialog(self, self.db, self.image_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            if not data['doc_name']:
                QMessageBox.warning(self, 'خطأ', 'يجب إدخال اسم الوثيقة')
                return
            
            doc_id = self.db.add_document(
                data['doc_name'],
                data['doc_date'],
                data['doc_title'],
                data['issuing_dept'],
                data['doc_classification'],
                data['legal_paragraph']
            )
            
            # حفظ جميع الصور الممسوحة مع الوثيقة الرئيسية
            scanned_images = data.get('scanned_images', [])
            # attachment_details_dict هو قاموس بمفاتيح 1, 2, 3, ...
            # حيث المفتاح 1 = المرفق الأول (الصورة الثانية، فهرس 1 في scanned_images)
            attachment_details_dict = data.get('attachment_details_dict', {})
            
            print(f"[DEBUG] add_document: عدد الصور = {len(scanned_images)}")
            print(f"[DEBUG] add_document: attachment_details_dict = {attachment_details_dict}")
            print(f"[DEBUG] add_document: مفاتيح القاموس = {list(attachment_details_dict.keys())}")
            
            if scanned_images:
                saved_count = 0
                # استخلاص مجلد السنة إن اختاره المستخدم في الحوار
                selected_year = None
                year_folder = data.get('selected_year_folder')
                try:
                    from pathlib import Path
                    selected_year = Path(year_folder).name if year_folder else None
                except Exception:
                    selected_year = None

                # enumerate(scanned_images, 0) -> idx يبدأ من 0
                # scanned_images[0] = الصورة الأولى = الوثيقة الرئيسية
                # scanned_images[1] = الصورة الثانية = المرفق الأول -> attachment_details_dict[1]
                # scanned_images[2] = الصورة الثالثة = المرفق الثاني -> attachment_details_dict[2]
                
                for idx, image_path in enumerate(scanned_images):
                    if os.path.exists(image_path):
                        try:
                            notes_text = None
                            
                            print(f"[DEBUG] معالجة الصورة idx={idx}")
                            
                            # الصورة الأولى (idx=0) هي الوثيقة الرئيسية - تستخدم بيانات الوثيقة الرئيسية
                            # الصورة الثانية (idx=1) هي المرفق الأول - بياناتها في attachment_details_dict[1]
                            # الصورة الثالثة (idx=2) هي المرفق الثاني - بياناتها في attachment_details_dict[2]
                            
                            if idx == 0:
                                # الوثيقة الرئيسية - استخدم بيانات data
                                print(f"[DEBUG] idx=0: الوثيقة الرئيسية")
                                merged_data = {
                                    'doc_name': data['doc_name'],
                                    'doc_date': data['doc_date'],
                                    'doc_title': data['doc_title'],
                                    'issuing_dept': data.get('issuing_dept', ''),
                                    'doc_classification': data.get('doc_classification', ''),
                                    'notes': ''
                                }
                            else:
                                # هذا مرفق - ابحث عن بياناته في القاموس
                                attachment_info = attachment_details_dict.get(idx, {})
                                print(f"[DEBUG] idx={idx}: المرفق {idx}, attachment_info = {attachment_info}")
                                
                                # تحقق هل هناك بيانات مخصصة
                                has_custom_data = False
                                if attachment_info and isinstance(attachment_info, dict):
                                    has_custom_data = any(
                                        v is not None and str(v).strip() != '' and v != 'اختر جهة الإصدار'
                                        for v in attachment_info.values()
                                    )
                                
                                print(f"[DEBUG] has_custom_data للمرفق {idx}: {has_custom_data}")
                                
                                if has_custom_data:
                                    # المرفق له بيانات مخصصة - استخدمها
                                    merged_data = {
                                        'doc_name': attachment_info.get('doc_name') or data['doc_name'],
                                        'doc_date': attachment_info.get('doc_date') or data['doc_date'],
                                        'doc_title': attachment_info.get('doc_title') or data['doc_title'],
                                        'issuing_dept': attachment_info.get('issuing_dept') or data.get('issuing_dept', ''),
                                        'doc_classification': attachment_info.get('doc_classification') or data.get('doc_classification', ''),
                                        'notes': attachment_info.get('notes', '')
                                    }
                                    print(f"[DEBUG] استخدام بيانات مخصصة للمرفق {idx}")
                                else:
                                    # المرفق ليس له بيانات مخصصة - استخدم بيانات الوثيقة الرئيسية
                                    merged_data = {
                                        'doc_name': data['doc_name'],
                                        'doc_date': data['doc_date'],
                                        'doc_title': data['doc_title'],
                                        'issuing_dept': data.get('issuing_dept', ''),
                                        'doc_classification': data.get('doc_classification', ''),
                                        'notes': ''
                                    }
                                    print(f"[DEBUG] استخدام بيانات الوثيقة الرئيسية للمرفق {idx}")
                            
                            print(f"[DEBUG] البيانات النهائية للصورة {idx}: {merged_data}")
                            
                            # إنشاء نص الملاحظات
                            notes_parts = []
                            if merged_data.get('doc_name'):
                                notes_parts.append(f"رقم: {merged_data['doc_name']}")
                            if merged_data.get('doc_date'):
                                notes_parts.append(f"تاريخ: {merged_data['doc_date']}")
                            if merged_data.get('doc_title'):
                                notes_parts.append(f"مضمون: {merged_data['doc_title']}")
                            if merged_data.get('issuing_dept'):
                                notes_parts.append(f"جهة: {merged_data['issuing_dept']}")
                            if merged_data.get('doc_classification'):
                                notes_parts.append(f"تصنيف: {merged_data['doc_classification']}")
                            if merged_data.get('notes'):
                                notes_parts.append(f"ملاحظات: {merged_data['notes']}")
                            
                            if notes_parts:
                                notes_text = " | ".join(notes_parts)
                            
                            # حفظ الصورة
                            saved_path = self.image_manager.save_image(
                                image_path,
                                doc_id,
                                idx + 1,  # page_number يبدأ من 1
                                year=selected_year
                            )
                            
                            print(f"[DEBUG] ✅ حفظ الصورة {idx} بـ notes: {notes_text}")
                            
                            # حفظ في قاعدة البيانات
                            self.db.add_image(
                                doc_id,
                                saved_path,
                                os.path.basename(image_path),
                                idx + 1,  # page_number يبدأ من 1
                                None,
                                1,
                                notes_text
                            )
                            
                            saved_count += 1
                                
                        except Exception as e:
                            print(f"خطأ في حفظ الصورة {idx}: {str(e)}")
                
                if saved_count > 0:
                    msg = f'تم الحفظ بنجاح!\n\n'
                    msg += f'الوثيقة الرئيسية مع {saved_count} صورة/مرفق'
                    QMessageBox.information(self, 'نجح ✅', msg)
                else:
                    QMessageBox.warning(self, 'تحذير', 'تم حفظ الوثيقة لكن لم يتم حفظ أي صورة')
            elif data.get('scanned_image') and os.path.exists(data['scanned_image']):
                # حفظ صورة واحدة فقط (للتوافق مع الكود القديم)
                try:
                    # استخلاص السنة ولوحة المستخدم
                    selected_year = None
                    year_folder = data.get('selected_year_folder')
                    try:
                        from pathlib import Path
                        selected_year = Path(year_folder).name if year_folder else None
                    except Exception:
                        selected_year = None

                    saved_path = self.image_manager.save_image(
                        data['scanned_image'],
                        doc_id,
                        1,
                        year=selected_year
                    )
                    
                    self.db.add_image(
                        doc_id,
                        saved_path,
                        os.path.basename(data['scanned_image']),
                        1,
                        None,
                        1,
                        None
                    )
                    
                    QMessageBox.information(self, 'نجح', 'تم إضافة الوثيقة والصورة بنجاح ✅')
                except Exception as e:
                    QMessageBox.warning(self, 'تحذير', f'تم حفظ الوثيقة لكن حدث خطأ في حفظ الصورة:\n{str(e)}')
            else:
                QMessageBox.information(self, 'نجح', 'تم إضافة الوثيقة بنجاح')
            
            self.load_documents()
    
    def import_images(self):
        """استيراد الصور"""
        dialog = ImportImagesDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            files = dialog.get_files()
            if not files:
                return
            
            # سؤال المستخدم عن استخراج المضمون من الصور (فقط إذا كان OCR متاحاً)
            extract_title = False
            ocr = None
            
            if OCR_AVAILABLE:
                # محاولة تهيئة OCR أولاً للتحقق من توفره
                try:
                    test_ocr = OCRExtractor()
                    if test_ocr.reader:
                        extract_title = QMessageBox.question(
                            self, 'استخراج المضمون',
                            '🔍 هل تريد استخراج المضمون (الموضوع) تلقائياً من الصور؟\n\n'
                            '• نعم: سيتم قراءة النص من الصور والبحث عن كلمة "الموضوع"\n'
                            '• لا: سيتم الاستيراد بدون استخراج المضمون\n\n'
                            '⚠️ ملاحظة: قد يستغرق الاستخراج وقتاً أطول',
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        ) == QMessageBox.StandardButton.Yes
                        
                        if extract_title:
                            ocr = test_ocr
                    else:
                        # Tesseract غير مثبت - عرض رسالة للمستخدم
                        QMessageBox.information(
                            self, 'ميزة استخراج المضمون',
                            '📝 لتفعيل ميزة استخراج المضمون تلقائياً:\n\n'
                            '1. حمّل Tesseract OCR من:\n'
                            '   https://github.com/UB-Mannheim/tesseract/wiki\n\n'
                            '2. ثبته واختر اللغة العربية أثناء التثبيت\n\n'
                            '3. أعد تشغيل البرنامج\n\n'
                            'سيتم الاستيراد بدون استخراج المضمون حالياً.'
                        )
                except Exception as e:
                    print(f"[OCR] خطأ في التحقق من OCR: {str(e)}")
            
            # تحليل الملفات واستخراج البيانات
            documents_to_add = {}
            unrecognized = []
            
            for file_path in files:
                filename = os.path.basename(file_path)
                parsed = FilenameParser.parse_filename(filename)
                
                # تحقق إذا كان حرف "ص" أو "و" في اسم الملف
                default_dept = None
                if 'ص' in filename or 'صادر' in filename:
                    default_dept = 'شعبة أمن الأفراد عنة'
                elif 'و' in filename or 'وارد' in filename:
                    default_dept = 'قسم أمن الأفراد الأنبار'
                
                if parsed['is_valid']:
                    # استخدم الرقم والتاريخ والجهة كمعرّف فريد
                    doc_key = f"{parsed['number']}_{parsed['date']}_{parsed['department']}"
                    
                    # إذا كانت هذه أول مرة نرى هذا المفتاح، أنشئ وثيقة جديدة
                    if doc_key not in documents_to_add:
                        documents_to_add[doc_key] = {
                            'data': {
                                'doc_name': f"{parsed['number']} في {parsed['date']}",
                                'doc_date': parsed['date'],
                                'doc_title': '',
                                'issuing_dept': parsed['department'],
                                'doc_classification': '',
                                'legal_paragraph': ''
                            },
                            'images': []
                        }
                    
                    # أضف الصورة للوثيقة
                    documents_to_add[doc_key]['images'].append({
                        'path': file_path,
                        'filename': filename,
                        'sequence': parsed.get('sequence')
                    })
                else:
                    # الملفات التي لم يتم التعرف على صيغتها
                    # لكن إذا كانت تحتوي على ص أو و، أضفها بجهة الإصدار الافتراضية
                    if default_dept:
                        unrecognized.append((filename, default_dept))
                    else:
                        unrecognized.append((filename, None))
            
            # إذا كانت هناك ملفات غير معترف بها، اسأل المستخدم
            if unrecognized:
                only_with_dept = [f for f, d in unrecognized if d is not None]
                without_dept = [f for f, d in unrecognized if d is None]
                
                msg = f"عدد الملفات غير المعترف بصيغتها: {len(unrecognized)}\n\n"
                
                if only_with_dept:
                    msg += f"ملفات ستُضاف بجهة الإصدار: {only_with_dept[0].split()[0] if 'ص' in only_with_dept[0] else 'قسم أمن الأفراد الأنبار'} ({len(only_with_dept)})\n"
                
                if without_dept:
                    msg += f"ملفات بدون جهة إصدار ({len(without_dept)})\n\n"
                    msg += "هل تريد إضافة جميع الملفات؟\n\n"
                    msg += "أول 10 ملفات:\n"
                    for f, _ in unrecognized[:10]:
                        msg += f"• {f}\n"
                
                reply = QMessageBox.question(self, 'ملفات غير معترف بها', msg)
                
                if reply == QMessageBox.StandardButton.Yes:
                    # أنشئ وثائق للملفات غير المعترف بها
                    
                    # 1. ملفات بجهة الإصدار المحددة
                    dept_groups = {}
                    for filename, dept in unrecognized:
                        if dept:
                            if dept not in dept_groups:
                                dept_groups[dept] = []
                            dept_groups[dept].append(filename)
                    
                    for dept, filenames in dept_groups.items():
                        doc_key = f"unrecognized_{dept}"
                        documents_to_add[doc_key] = {
                            'data': {
                                'doc_name': f'ملفات مستورة عن {dept}',
                                'doc_date': '',
                                'doc_title': '',
                                'issuing_dept': dept,
                                'doc_classification': '',
                                'legal_paragraph': ''
                            },
                            'images': []
                        }
                        
                        for filename in filenames:
                            for file_path in files:
                                if os.path.basename(file_path) == filename:
                                    documents_to_add[doc_key]['images'].append({
                                        'path': file_path,
                                        'filename': filename,
                                        'sequence': None
                                    })
                                    break
                    
                    # 2. ملفات بدون جهة إصدار
                    no_dept_files = [f for f, d in unrecognized if d is None]
                    if no_dept_files:
                        doc_key = 'unrecognized_files_no_dept'
                        documents_to_add[doc_key] = {
                            'data': {
                                'doc_name': 'ملفات مستورة (بدون معلومات)',
                                'doc_date': '',
                                'doc_title': '',
                                'issuing_dept': '',
                                'doc_classification': '',
                                'legal_paragraph': ''
                            },
                            'images': []
                        }
                        
                        for filename in no_dept_files:
                            for file_path in files:
                                if os.path.basename(file_path) == filename:
                                    documents_to_add[doc_key]['images'].append({
                                        'path': file_path,
                                        'filename': filename,
                                        'sequence': None
                                    })
                                    break
            
            # حفظ الوثائق والصور في قاعدة البيانات
            # Calculate total images for progress
            total_images = sum(len(doc_info['images']) for doc_info in documents_to_add.values())
            
            # Create progress dialog
            progress_text = 'جاري استيراد الصور...'
            if extract_title:
                progress_text = 'جاري استيراد الصور واستخراج المضمون...'
                # If the import is very large, ask user whether to run OCR (slow)
                LARGE_IMPORT_THRESHOLD = 200
                if total_images > LARGE_IMPORT_THRESHOLD:
                    reply = QMessageBox.question(
                        self,
                        'مجلد كبير',
                        f'المجلد يحتوي على {total_images} صورة. تشغيل استخراج المضمون عبر Tesseract قد يستغرق وقتاً طويلاً.\n\nهل تريد المتابعة مع استخراج المضمون (أبطأ) أم استيراد بدون OCR (أسرع)?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                    )
                    if reply == QMessageBox.StandardButton.Cancel:
                        return
                    if reply == QMessageBox.StandardButton.No:
                        extract_title = False
                        progress_text = 'جاري استيراد الصور (بدون استخراج المضمون)...'
                    else:
                        extract_title = True
                        progress_text = 'جاري استيراد الصور واستخراج المضمون...'

            progress = QProgressDialog(progress_text, 'إلغاء', 0, total_images, self)
            progress.setWindowTitle('استيراد الصور')
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.show()
            
            imported_count = 0
            current_progress = 0
            extracted_titles_count = 0
            
            for doc_key, doc_info in documents_to_add.items():
                if progress.wasCanceled():
                    break
                    
                if not doc_info['images']:
                    continue
                
                # استخراج المضمون من الصور إذا طُلب ذلك (البحث في جميع الصور حتى نجد الموضوع)
                doc_title = doc_info['data']['doc_title']
                if extract_title and ocr and not doc_title and doc_info['images']:
                    progress.setLabelText(f'جاري استخراج المضمون من الصور...')
                    QApplication.processEvents()
                    
                    # البحث في جميع الصور حتى نجد الموضوع
                    for img_idx, img_info in enumerate(doc_info['images']):
                        try:
                            image_path = img_info['path']
                            print(f"[OCR] محاولة استخراج المضمون من الصورة {img_idx + 1}...")
                            
                            extracted_info = ocr.extract_document_info(image_path)
                            if extracted_info and extracted_info.get('doc_title'):
                                doc_title = extracted_info['doc_title']
                                doc_info['data']['doc_title'] = doc_title
                                extracted_titles_count += 1
                                print(f"[OCR] تم استخراج المضمون من الصورة {img_idx + 1}: {doc_title[:50]}...")
                                break  # توقف بعد إيجاد الموضوع
                        except Exception as e:
                            print(f"[OCR ERROR] خطأ في الصورة {img_idx + 1}: {str(e)}")
                            continue
                # استخراج رقم الوثيقة من الاسم (الجزء قبل كلمة "في")
                splittedChars = ['في', 'td', 'فيس' , 'فس'] # use this array instead of only 'في' to avoid OCR errors
                doc_name_parts = []
                for splitChar in splittedChars:
                    if splitChar in doc_info['data']['doc_name']:
                        doc_name_parts = doc_info['data']['doc_name'].split(f' {splitChar} ')
                        break
                doc_number = doc_name_parts[0].strip() if doc_name_parts else ''
                doc_date = doc_info['data']['doc_date']
                
                print(f"[DEBUG] البحث عن وثيقة: رقم={doc_number}, تاريخ={doc_date}, اسم={doc_info['data']['doc_name']}")
                
                # تحقق من وجود الوثيقة بنفس الرقم والتاريخ
                existing = None
                if doc_number and doc_date:
                    existing = self.db.find_document_by_number_and_date(doc_number, doc_date)
                    print(f"[DEBUG] نتيجة البحث: {len(existing) if existing else 0} وثيقة")
                
                if existing:
                    doc_id = existing[0][0]
                    print(f"[DEBUG] تم إيجاد وثيقة موجودة: ID={doc_id}")
                    # تحديث المضمون إذا تم استخراجه
                    if doc_title:
                        self.db.update_document(doc_id, doc_title=doc_title)
                else:
                    # أنشئ وثيقة جديدة
                    print(f"[DEBUG] إنشاء وثيقة جديدة...")
                    doc_id = self.db.add_document(
                        doc_info['data']['doc_name'],
                        doc_info['data']['doc_date'],
                        doc_info['data']['doc_title'],
                        doc_info['data']['issuing_dept'],
                        doc_info['data']['doc_classification'],
                        doc_info['data']['legal_paragraph']
                    )
                    print(f"[DEBUG] تم إنشاء وثيقة جديدة: ID={doc_id}")
                
                # الحصول على عدد الصور الموجودة مسبقاً في الوثيقة
                existing_images = self.db.get_document_images(doc_id)
                start_img_idx = len(existing_images) + 1  # البدء من بعد آخر صورة
                
                # حفظ الصور
                for img_idx, img_info in enumerate(doc_info['images'], start_img_idx):
                    if progress.wasCanceled():
                        break
                    
                    current_progress += 1
                    progress.setValue(current_progress)
                    progress.setLabelText(f'جاري استيراد الصورة {current_progress} من {total_images}...')
                    QApplication.processEvents()  # Keep UI responsive
                    
                    try:
                        # حفظ الصورة في المجلد
                        saved_path = self.image_manager.save_image(
                            img_info['path'],
                            doc_id,
                            img_idx
                        )
                        
                        # أضف معلومات الصورة في قاعدة البيانات
                        self.db.add_image(
                            doc_id,
                            saved_path,
                            img_info['filename'],
                            img_idx,
                            img_info['sequence'],
                            1,
                            None
                        )
                        
                        imported_count += 1
                    
                    except Exception as e:
                        print(f"[ERROR] خطأ في حفظ الصورة {img_info['filename']}: {str(e)}")
            
            progress.setValue(total_images)
            progress.close()
            
            # الرسالة النهائية
            msg = f"✅ تم استيراد {imported_count} صورة بنجاح\n"
            msg += f"في {len(documents_to_add)} وثيقة"
            
            if extract_title and extracted_titles_count > 0:
                msg += f"\n\n📝 تم استخراج المضمون من {extracted_titles_count} وثيقة"
            
            if unrecognized:
                msg += f"\n\n⚠️ تم تخطي {len(unrecognized)} ملف"
            
            QMessageBox.information(self, 'نجح', msg)
            self.load_documents()
    
    def view_document(self):
        """عرض تفاصيل الوثيقة والصور"""
        current_row = self.documents_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'تنبيه', 'يجب اختيار وثيقة أولاً')
            return
        
        # احصل على معرف الوثيقة من البيانات المخزنة في الصف (column 1 now)
        doc_id_item = self.documents_table.item(current_row, 1)
        if not doc_id_item or not doc_id_item.data(Qt.ItemDataRole.UserRole):
            QMessageBox.warning(self, 'خطأ', 'لم يتم العثور على معرف الوثيقة')
            return
        
        doc_id = doc_id_item.data(Qt.ItemDataRole.UserRole)
        doc = self.db.get_document_by_id(doc_id)
        
        if doc:
            # الحصول على الصور
            images = self.db.get_document_images(doc_id)
            
            if not images:
                QMessageBox.warning(
                    self, 'تنبيه',
                    'لا توجد صور لهذه الوثيقة\n\nأرجو استيراد الصور أولاً'
                )
                return
            
            # استخراج مسارات الصور
            # جمع بيانات الصور مع معلومات المرفقات
            # هيكل جدول images: (0:id, 1:document_id, 2:image_path, 3:original_filename, 
            #                    4:page_number, 5:image_number, 6:sides, 7:created_date, 8:notes)
            images_data = []
            for img in images:
                img_path = img[2]  # العمود 2 هو image_path
                if os.path.exists(img_path):
                    notes_value = img[8] if len(img) > 8 else None  # العمود 8 هو notes
                    print(f"[DEBUG] img[8] (notes) = {notes_value}")
                    images_data.append({
                        'path': img_path,
                        'page_number': img[4] if len(img) > 4 else 0,
                        'notes': notes_value
                    })
            
            image_paths = [img['path'] for img in images_data]
            
            print(f"\n[MAIN] فتح عارض الوثائق:")
            print(f"  • معرف الوثيقة: {doc_id}")
            print(f"  • اسم الوثيقة: {doc[1]}")
            print(f"  • عدد الصور المسجلة: {len(images)}")
            print(f"  • عدد الصور الموجودة: {len(image_paths)}")
            for i, img_d in enumerate(images_data):
                print(f"  • صورة {i+1}: notes = {img_d.get('notes', 'لا يوجد')[:50] if img_d.get('notes') else 'لا يوجد'}...")
            if image_paths:
                print(f"  • أول صورة: {image_paths[0]}")
                print(f"  • آخر صورة: {image_paths[-1]}")
            
            if not image_paths:
                QMessageBox.warning(
                    self, 'خطأ',
                    'لا يمكن العثور على ملفات الصور\nقد تم حذفها من الحاسب'
                )
                return
            
            # فتح نافذة العرض مع بيانات الصور الكاملة
            try:
                viewer = DocumentViewerWindow(doc_id, doc, images_data, self)
                viewer.show()
                self.viewer_windows = getattr(self, 'viewer_windows', [])
                self.viewer_windows.append(viewer)
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'خطأ في فتح العارض: {str(e)}')
    
    def delete_document(self):
        """حذف وثيقة"""
        current_row = self.documents_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'تنبيه', 'يجب اختيار وثيقة أولاً')
            return
        
        # احصل على معرف الوثيقة من UserRole (column 1 now)
        doc_id_item = self.documents_table.item(current_row, 1)
        if not doc_id_item or not doc_id_item.data(Qt.ItemDataRole.UserRole):
            QMessageBox.warning(self, 'خطأ', 'لم يتم العثور على معرف الوثيقة')
            return
        
        doc_id = doc_id_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, 'تأكيد الحذف',
            'هل أنت متأكد من حذف هذه الوثيقة؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_document(doc_id)
            QMessageBox.information(self, 'نجح', 'تم حذف الوثيقة')
            self.load_documents()
    
    def open_destruction_form(self):
        """فتح نافذة استمارة إتلاف الوثائق"""
        # الحصول على الوثائق المحددة
        selected_docs = []
        for row in range(self.documents_table.rowCount()):
            checkbox = self.documents_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                doc_id_item = self.documents_table.item(row, 1)
                if doc_id_item:
                    doc_id = doc_id_item.data(Qt.ItemDataRole.UserRole)
                    if doc_id:
                        doc = self.db.get_document_by_id(doc_id)
                        if doc:
                            selected_docs.append(doc)
        
        # فتح النافذة
        dialog = DestructionFormDialog(self, self.db, selected_docs)
        dialog.exec()
    
    def select_all_documents(self):
        """تحديد جميع الوثائق"""
        # تحديد جميع الصفوف في الجدول
        self.documents_table.selectAll()
        
        # تحديد جميع checkboxes
        for row in range(self.documents_table.rowCount()):
            checkbox = self.documents_table.cellWidget(row, 0)
            if checkbox:
                checkbox.blockSignals(True)  # منع إرسال signals تجنباً للتداخل
                checkbox.setChecked(True)
                checkbox.blockSignals(False)
    
    def deselect_all_documents(self):
        """إلغاء تحديد جميع الوثائق"""
        # إلغاء تحديد جميع الصفوف في الجدول
        self.documents_table.clearSelection()
        
        # إلغاء تحديد جميع checkboxes
        for row in range(self.documents_table.rowCount()):
            checkbox = self.documents_table.cellWidget(row, 0)
            if checkbox:
                checkbox.blockSignals(True)  # منع إرسال signals تجنباً للتداخل
                checkbox.setChecked(False)
                checkbox.blockSignals(False)
    
    def delete_selected_documents(self):
        """حذف جميع الوثائق المحددة"""
        # Get checked rows
        checked_rows = []
        for row in range(self.documents_table.rowCount()):
            checkbox = self.documents_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                checked_rows.append(row)
        
        if not checked_rows:
            QMessageBox.warning(self, 'تنبيه', 'يجب تحديد وثائق أولاً')
            return
        
        count = len(checked_rows)
        reply = QMessageBox.question(
            self,
            'تأكيد الحذف',
            f'هل أنت متأكد من حذف {count} وثيقة؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get doc IDs from checked rows
            doc_ids = []
            for row in checked_rows:
                doc_id_item = self.documents_table.item(row, 1)  # Column 1 now has doc number
                if doc_id_item:
                    doc_id = doc_id_item.data(Qt.ItemDataRole.UserRole)
                    if doc_id:
                        doc_ids.append(doc_id)
            
            # Create progress dialog
            progress = QProgressDialog('جاري حذف الوثائق...', 'إلغاء', 0, len(doc_ids), self)
            progress.setWindowTitle('حذف الوثائق')
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.show()
            
            # Delete from database with progress
            deleted_count = 0
            for i, doc_id in enumerate(doc_ids):
                if progress.wasCanceled():
                    break
                progress.setValue(i)
                progress.setLabelText(f'جاري حذف الوثيقة {i + 1} من {len(doc_ids)}...')
                QApplication.processEvents()  # Keep UI responsive
                
                try:
                    self.db.delete_document(doc_id)
                    deleted_count += 1
                except Exception as e:
                    print(f'خطأ في حذف الوثيقة {doc_id}: {e}')
            
            progress.setValue(len(doc_ids))
            progress.close()
            
            # Reload table
            self.load_documents()
            QMessageBox.information(self, 'نجح', f'تم حذف {deleted_count} وثيقة بنجاح')
    
    def search_documents(self):
        """البحث عن الوثائق والمرفقات"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_documents()
            return
        
        # تحديد حقل البحث
        field_map = {
            'اسم الوثيقة': 'doc_name',
            'المضمون': 'doc_title',
            'التاريخ': 'doc_date',
            'الجهة': 'issuing_dept',
            'التصنيف': 'doc_classification'
        }
        
        search_field = field_map.get(self.search_field.currentText(), 'doc_name')
        
        self.documents_table.setRowCount(0)
        
        # استخدام البحث الجديد الذي يشمل المرفقات
        results_dict = self.db.search_documents_and_attachments(search_term, search_field)
        
        # Disable updates for better performance
        self.documents_table.setUpdatesEnabled(False)
        
        for idx, (key, result_data) in enumerate(results_dict.items()):
            doc = result_data['doc']
            source = result_data['source']
            attachment_info = result_data['attachment_info']
            
            row = self.documents_table.rowCount()
            self.documents_table.insertRow(row)
            
            # Checkbox column
            checkbox = QCheckBox()
            checkbox.setStyleSheet('margin-left: 10px;')
            checkbox.stateChanged.connect(lambda state, row=row: self.on_checkbox_changed(row, state))
            self.documents_table.setCellWidget(row, 0, checkbox)
            
            # رقم الوثيقة/المرفق
            if source == 'attachment' and attachment_info:
                # استخراج المعلومات من ملاحظات المرفق
                doc_number = result_data['doc_number']
                # إضافة علامة للمرفق
                display_number = f"📎 {doc_number}" if doc_number else ''
            else:
                doc_name = doc[1] or ''
                doc_number = doc_name.split()[0] if doc_name else ''
                display_number = doc_number
            
            item = QTableWidgetItem(display_number)
            item.setData(Qt.ItemDataRole.UserRole, doc[0])  # احفظ معرف الوثيقة
            self.documents_table.setItem(row, 1, item)
            
            # التاريخ
            if source == 'attachment' and attachment_info:
                # استخراج التاريخ من ملاحظات المرفق
                import re
                date_match = re.search(r'تاريخ:\s*([^\|]+)', attachment_info)
                date_val = date_match.group(1).strip() if date_match else (doc[2] or '')
            else:
                date_val = doc[2] or ''
            self.documents_table.setItem(row, 2, QTableWidgetItem(date_val))
            
            # المضمون
            if source == 'attachment' and attachment_info:
                title_match = re.search(r'مضمون:\s*([^\|]+)', attachment_info)
                title_val = title_match.group(1).strip() if title_match else (doc[3] or '')
            else:
                title_val = doc[3] or ''
            self.documents_table.setItem(row, 3, QTableWidgetItem(title_val))
            
            # الجهة
            if source == 'attachment' and attachment_info:
                dept_match = re.search(r'جهة:\s*([^\|]+)', attachment_info)
                dept_val = dept_match.group(1).strip() if dept_match else (doc[4] or '')
            else:
                dept_val = doc[4] or ''
            self.documents_table.setItem(row, 4, QTableWidgetItem(dept_val))
            
            # التصنيف
            if source == 'attachment' and attachment_info:
                class_match = re.search(r'تصنيف:\s*([^\|]+)', attachment_info)
                class_val = class_match.group(1).strip() if class_match else (doc[5] or '')
            else:
                class_val = doc[5] or ''
            self.documents_table.setItem(row, 5, QTableWidgetItem(class_val))
            
            # المادة القانونية
            self.documents_table.setItem(row, 6, QTableWidgetItem(doc[6] or ''))
            
            # عدد الصور
            images = self.db.get_document_images(doc[0])
            self.documents_table.setItem(row, 7, QTableWidgetItem(str(len(images))))
            
            # Process events every 50 rows
            if idx % 50 == 0:
                QApplication.processEvents()
        
        # Re-enable updates
        self.documents_table.setUpdatesEnabled(True)
    
    def on_checkbox_changed(self, row, state):
        """التحكم في checkboxes - دعم التحديد المتعدد"""
        # تحديث تحديد الصف في الجدول وفقاً لحالة checkbox
        if state == Qt.CheckState.Checked.value:
            # إضافة الصف للتحديد
            self.documents_table.selectRow(row)
        else:
            # إزالة تحديد الصف المحدد
            selection_model = self.documents_table.selectionModel()
            index = self.documents_table.model().index(row, 0)
            selection_model.select(index, selection_model.SelectionFlag.Deselect | selection_model.SelectionFlag.Rows)
    
    def on_row_selection_changed(self, selected, deselected):
        """عند تحديد صف جديد، تحديث checkbox المطابق"""
        # تحديث checkboxes للصفوف المحددة
        selected_rows = self.documents_table.selectionModel().selectedRows()
        
        # أولاً، امسح جميع checkboxes
        for row in range(self.documents_table.rowCount()):
            checkbox = self.documents_table.cellWidget(row, 0)
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)
        
        # ثم، حدد checkboxes للصفوف المختارة
        for index in selected_rows:
            row = index.row()
            checkbox = self.documents_table.cellWidget(row, 0)
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
