"""
نافذة إضافة وثيقة جديدة
Add Document Dialog

نافذة حوار لإضافة وثيقة جديدة مع دعم المسح الضوئي واستخراج OCR
"""

import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QLabel, QPushButton, QComboBox, QSpinBox,
    QTextEdit, QDialogButtonBox, QFileDialog, QMessageBox,
    QProgressDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ..constants import COLORS, ICONS, APP_SETTINGS, FONT_SIZES, DIMENSIONS
from ..ui_styles import SCANNER_STATUS_STYLES, BUTTON_STYLES
from .utils import choose_year_folder
from .attachment_details_dialog import AttachmentDetailsDialog


# التحقق من توفر مكتبة السكانر (Windows فقط)
SCANNER_AVAILABLE = False
SCANNER_COUNT = 0
try:
    import win32com.client
    SCANNER_AVAILABLE = True
    try:
        _wia_manager = win32com.client.Dispatch("WIA.DeviceManager")
        SCANNER_COUNT = _wia_manager.DeviceInfos.Count
    except:
        SCANNER_COUNT = 0
except ImportError:
    SCANNER_AVAILABLE = False
    SCANNER_COUNT = 0


class AddDocumentDialog(QDialog):
    """
    نافذة حوار لإضافة وثيقة جديدة
    
    تتيح هذه النافذة:
    - إدخال معلومات الوثيقة يدوياً
    - مسح الوثيقة من السكانر
    - استخراج المعلومات تلقائياً باستخدام OCR
    - اختيار مجلد السنة
    """
    
    def __init__(self, parent=None, db=None, image_manager=None):
        """
        تهيئة النافذة
        
        Args:
            parent: النافذة الأب
            db: مدير قاعدة البيانات
            image_manager: مدير الصور
        """
        super().__init__(parent)
        self.setWindowTitle('إضافة وثيقة جديدة')
        self.setGeometry(100, 100, 600, 500)
        
        self.db = db
        self.image_manager = image_manager
        self.scanned_image_path = None
        self.scanned_images = []
        self.attachment_details_dict = {}
        self.selected_year_folder = None
        
        self._init_ui()
        self.apply_dialog_styles()

    def apply_dialog_styles(self):
        """Apply dialog-level styles to match the light theme"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS.BACKGROUND_LIGHT};
                color: {COLORS.TEXT_PRIMARY};
                font-size: {FONT_SIZES.BODY}px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton {{
                background-color: {COLORS.ACCENT};
                color: {COLORS.TEXT_WHITE};
                border: 1px solid {COLORS.BORDER};
                border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
                padding: {DIMENSIONS.PADDING_SMALL}px {DIMENSIONS.PADDING_MEDIUM}px;
                min-height: {DIMENSIONS.BUTTON_HEIGHT}px;
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {COLORS.BACKGROUND_WHITE};
                color: {COLORS.TEXT_PRIMARY};
                border: 1px solid {COLORS.BORDER};
                border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
            }}
        """)
    
    def _init_ui(self):
        """إنشاء واجهة المستخدم"""
        layout = QFormLayout()
        try:
            layout.setSpacing(DIMENSIONS.PADDING_MEDIUM)
            layout.setContentsMargins(
                DIMENSIONS.MARGIN_MEDIUM, DIMENSIONS.MARGIN_MEDIUM,
                DIMENSIONS.MARGIN_MEDIUM, DIMENSIONS.MARGIN_MEDIUM
            )
        except Exception:
            pass
        
        # حقول الإدخال الأساسية
        self._create_basic_fields(layout)
        
        # مجلد السنة
        self._create_year_folder_field(layout)
        
        # أزرار المسح
        self._create_scan_buttons(layout)
        
        # أزرار الحوار
        self._create_dialog_buttons(layout)
        
        self.setLayout(layout)
    
    def _create_basic_fields(self, layout):
        """إنشاء حقول الإدخال الأساسية"""
        # اسم الوثيقة
        self.doc_name = QLineEdit()
        layout.addRow('اسم الوثيقة:', self.doc_name)
        
        # التاريخ
        self.doc_date = QLineEdit()
        self.doc_date.setPlaceholderText('مثال: 23-3-2025')
        layout.addRow('تاريخ الوثيقة:', self.doc_date)
        
        # العنوان
        self.doc_title = QLineEdit()
        layout.addRow('عنوان الوثيقة:', self.doc_title)
        
        # جهة الإصدار
        self.issuing_dept = QComboBox()
        self.issuing_dept.addItems(APP_SETTINGS.DEFAULT_DEPARTMENTS)
        layout.addRow('جهة الإصدار:', self.issuing_dept)
        
        # تصنيف الوثيقة
        self.doc_classification = QLineEdit()
        layout.addRow('تصنيف الوثيقة:', self.doc_classification)
        
        # الفقرة القانونية
        self.legal_paragraph = QTextEdit()
        self.legal_paragraph.setMaximumHeight(100)
        layout.addRow('الفقرة القانونية:', self.legal_paragraph)
        
        # عدد الوجوه
        self.sides = QSpinBox()
        self.sides.setMinimum(1)
        self.sides.setMaximum(2)
        self.sides.setValue(1)
        layout.addRow('عدد الوجوه:', self.sides)
        
        # عدد الصور الممسوحة
        self.images_label = QLabel('عدد الصور الممسوحة: 0')
        layout.addRow(self.images_label)
        
        # حالة السكانر
        self.scanner_status_label = QLabel()
        self._update_scanner_status()
        layout.addRow(self.scanner_status_label)
    
    def _create_year_folder_field(self, layout):
        """إنشاء حقل اختيار مجلد السنة"""
        year_widget = QWidget()
        year_widget_layout = QHBoxLayout()
        year_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        self.year_folder_edit = QLineEdit()
        self.year_folder_edit.setReadOnly(True)
        self.year_folder_edit.setPlaceholderText('لم يتم اختيار مجلد السنة')
        year_widget_layout.addWidget(self.year_folder_edit)
        
        year_select_btn = QPushButton(f'{ICONS.FOLDER} اختيار مجلد السنة')
        year_select_btn.clicked.connect(self._on_choose_year_folder)
        year_widget_layout.addWidget(year_select_btn)
        
        year_widget.setLayout(year_widget_layout)
        layout.addRow('مجلد السنة:', year_widget)
    
    def _create_scan_buttons(self, layout):
        """إنشاء أزرار المسح"""
        scan_layout = QHBoxLayout()
        
        # مسح صورة واحدة
        scan_one_btn = QPushButton(f'{ICONS.SCAN_SINGLE} مسح صورة واحدة')
        scan_one_btn.clicked.connect(self.scan_manual)
        scan_layout.addWidget(scan_one_btn)
        
        # مسح مرفقات متعددة
        scan_multiple_btn = QPushButton(f'{ICONS.SCAN_MULTIPLE} مسح مرفقات متعددة')
        scan_multiple_btn.clicked.connect(self.scan_multiple)
        scan_layout.addWidget(scan_multiple_btn)
        
        layout.addRow(scan_layout)
        
        # استخراج تلقائي
        ocr_btn = QPushButton(f'{ICONS.SEARCH} استخراج تلقائي من الصور (بطيء)')
        ocr_btn.clicked.connect(self.scan_and_extract)
        layout.addRow(ocr_btn)
    
    def _create_dialog_buttons(self, layout):
        """إنشاء أزرار الحوار"""
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def _update_scanner_status(self):
        """تحديث حالة السكانر في الواجهة"""
        global SCANNER_AVAILABLE, SCANNER_COUNT
        
        if SCANNER_AVAILABLE:
            try:
                _wia_manager = win32com.client.Dispatch("WIA.DeviceManager")
                SCANNER_COUNT = _wia_manager.DeviceInfos.Count
            except:
                SCANNER_COUNT = 0
        
        if not SCANNER_AVAILABLE:
            self.scanner_status_label.setText(
                f'{ICONS.WARNING} حالة السكانر: مكتبة pywin32 غير مثبتة - استخدم اختيار الصور من الحاسب'
            )
            self.scanner_status_label.setStyleSheet(SCANNER_STATUS_STYLES['unavailable'])
        elif SCANNER_COUNT == 0:
            self.scanner_status_label.setText(
                f'{ICONS.WARNING} حالة السكانر: لا يوجد سكانر متصل - قم بتوصيل السكانر أو اختر صورة من الحاسب'
            )
            self.scanner_status_label.setStyleSheet(SCANNER_STATUS_STYLES['disconnected'])
        else:
            self.scanner_status_label.setText(
                f'{ICONS.SUCCESS} حالة السكانر: متصل ({SCANNER_COUNT} جهاز)'
            )
            self.scanner_status_label.setStyleSheet(SCANNER_STATUS_STYLES['connected'])
    
    def select_year_folder(self):
        """استخدم الدالة المساعدة الموحدة لاختيار مجلد السنة"""
        try:
            return choose_year_folder(self)
        except Exception:
            return None
    
    def _on_choose_year_folder(self):
        """مستدعى عند الضغط على زر اختيار مجلد السنة"""
        path = self.select_year_folder()
        if path:
            self.selected_year_folder = path
            self.year_folder_edit.setText(path)
    
    def _get_year_folder(self):
        """الحصول على مجلد السنة المختار أو طلبه"""
        year_folder = self.selected_year_folder
        if not year_folder:
            try:
                txt = self.year_folder_edit.text().strip()
                if txt and txt != 'لم يتم اختيار مجلد السنة':
                    year_folder = txt
            except Exception:
                pass
        
        if not year_folder:
            year_folder = self.select_year_folder()
            if year_folder:
                self.selected_year_folder = year_folder
                self.year_folder_edit.setText(year_folder)
        
        return year_folder
    
    def _update_images_count(self):
        """تحديث عدد الصور الممسوحة"""
        count = len(self.scanned_images)
        self.images_label.setText(f'عدد الصور الممسوحة: {count}')
    
    # =========================================================================
    # وظائف المسح الضوئي
    # =========================================================================
    
    def scan_manual(self):
        """مسح من السكانر مع إدخال يدوي (سريع)"""
        global SCANNER_AVAILABLE, SCANNER_COUNT
        
        if not SCANNER_AVAILABLE:
            reply = QMessageBox.question(
                self, 'السكانر غير متاح',
                f'{ICONS.WARNING} مكتبة السكانر (pywin32) غير مثبتة\n\n'
                'لتثبيتها، قم بتشغيل الأمر التالي:\n'
                'pip install pywin32\n\n'
                'هل تريد اختيار صورة من الحاسب بدلاً من المسح؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._select_image_file()
            return
        
        self._update_scanner_status()
        if SCANNER_COUNT == 0:
            reply = QMessageBox.question(
                self, 'السكانر غير متصل',
                f'{ICONS.WARNING} لا يوجد سكانر متصل بالحاسب\n\n'
                'تأكد من:\n'
                '• توصيل السكانر بالحاسب\n'
                '• تشغيل السكانر\n'
                '• تثبيت برنامج تشغيل السكانر\n\n'
                'هل تريد اختيار صورة من الحاسب بدلاً من المسح؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._select_image_file()
            return
        
        try:
            year_folder = self._get_year_folder()
            if not year_folder:
                return
            
            QMessageBox.information(
                self, 'جاري المسح',
                'سيتم فتح نافذة السكانر\n\nضع الوثيقة واضغط Scan'
            )
            
            wia = win32com.client.Dispatch("WIA.CommonDialog")
            image = wia.ShowAcquireImage()
            
            if not image:
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f'scanned_{timestamp}.jpg')
            
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            image.SaveFile(temp_file)
            
            self.scanned_image_path = temp_file
            self.scanned_images = [temp_file]
            self._update_images_count()
            
            QMessageBox.information(
                self, f'تم المسح {ICONS.SUCCESS}',
                'تم مسح الوثيقة بنجاح!\n\nأدخل المعلومات يدوياً في الحقول أدناه'
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 'خطأ',
                f'خطأ في المسح الضوئي:\n{str(e)}\n\nتأكد من:\n• توصيل السكانر\n• تثبيت برنامج السكانر'
            )
    
    def _select_image_file(self):
        """اختيار صورة من الحاسب كبديل للسكانر"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'اختر صورة الوثيقة',
            '', 'صور (*.jpg *.jpeg *.png *.tiff *.bmp);;جميع الملفات (*)'
        )
        
        if file_path:
            year_folder = self._get_year_folder()
            if not year_folder:
                QMessageBox.warning(self, 'تنبيه', 'يجب اختيار أو إنشاء مجلد سنة')
                return
            
            basename = os.path.basename(file_path)
            dest_path = os.path.join(year_folder, basename)
            shutil.copy2(file_path, dest_path)
            
            self.scanned_image_path = dest_path
            self.scanned_images = [dest_path]
            self._update_images_count()
            
            QMessageBox.information(
                self, f'تم {ICONS.SUCCESS}',
                f'تم اختيار الصورة بنجاح!\n\nتم نقلها إلى مجلد السنة: {year_folder}'
            )
    
    def _select_multiple_image_files(self):
        """اختيار عدة صور من الحاسب"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 'اختر صور الوثائق',
            '', 'صور (*.jpg *.jpeg *.png *.tiff *.bmp);;جميع الملفات (*)'
        )
        
        if files:
            year_folder = self._get_year_folder()
            if not year_folder:
                QMessageBox.warning(self, 'تنبيه', 'يجب اختيار أو إنشاء مجلد سنة')
                return
            
            dest_files = []
            for f in files:
                try:
                    basename = os.path.basename(f)
                    dest = os.path.join(year_folder, basename)
                    
                    if os.path.exists(dest):
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                        name, ext = os.path.splitext(basename)
                        dest = os.path.join(year_folder, f"{name}_{timestamp}{ext}")
                    
                    shutil.copy2(f, dest)
                    dest_files.append(dest)
                except Exception as e:
                    print(f"خطأ في نسخ الملف {f}: {e}")
            
            if dest_files:
                self.scanned_images = dest_files
                self.scanned_image_path = dest_files[0] if dest_files else None
                self._update_images_count()
                
                if len(dest_files) > 1:
                    self._handle_scanned_documents(len(dest_files))
                else:
                    QMessageBox.information(
                        self, f'تم {ICONS.SUCCESS}',
                        'تم اختيار الصورة ونقلها لمجلد السنة بنجاح!'
                    )
            else:
                QMessageBox.warning(self, 'تنبيه', 'لم يتم نسخ أي ملفات')
    
    def scan_multiple(self):
        """مسح تلقائي لجميع الأوراق دفعة واحدة"""
        global SCANNER_AVAILABLE, SCANNER_COUNT
        
        if not SCANNER_AVAILABLE:
            reply = QMessageBox.question(
                self, 'السكانر غير متاح',
                f'{ICONS.WARNING} مكتبة السكانر (pywin32) غير مثبتة\n\n'
                'هل تريد اختيار عدة صور من الحاسب بدلاً من المسح؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._select_multiple_image_files()
            return
        
        self._update_scanner_status()
        if SCANNER_COUNT == 0:
            reply = QMessageBox.question(
                self, 'السكانر غير متصل',
                f'{ICONS.WARNING} لا يوجد سكانر متصل بالحاسب\n\n'
                'هل تريد اختيار عدة صور من الحاسب بدلاً من المسح؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._select_multiple_image_files()
            return
        
        try:
            reply = QMessageBox.question(
                self, 'مسح تلقائي جماعي',
                f'{ICONS.REFRESH} مسح تلقائي مستمر لجميع الأوراق\n\n'
                f'{ICONS.CONFIRM} ضع جميع الأوراق في وحدة التغذية (ADF)\n'
                f'{ICONS.CONFIRM} أو رتبها جاهزة للمسح المتتالي\n\n'
                'سيتم مسح جميع الأوراق تلقائياً بدون توقف\n\n'
                'هل تريد البدء؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            year_folder = self._get_year_folder()
            if not year_folder:
                QMessageBox.information(
                    self, 'ملغى', 
                    'تم إلغاء المسح - يجب اختيار مجلد السنة للمتابعة'
                )
                return
            
            # محاولة استخدام المسح التلقائي أولاً
            try:
                scan_count = self._scan_automatic_feeder()
                if scan_count > 0:
                    self._handle_scanned_documents(scan_count)
                    return
            except Exception as e:
                print(f"المسح التلقائي فشل: {e}")
            
            # إذا فشل المسح التلقائي، استخدم المسح المتتالي السريع
            self._scan_continuous_manual()
            
        except Exception as e:
            QMessageBox.critical(
                self, 'خطأ',
                f'خطأ في المسح الضوئي:\n{str(e)}'
            )
    
    def _scan_automatic_feeder(self):
        """مسح تلقائي باستخدام وحدة التغذية التلقائية (ADF)"""
        wia = win32com.client.Dispatch("WIA.DeviceManager")
        
        if wia.DeviceInfos.Count == 0:
            raise Exception("لا يوجد سكانر متصل")
        
        device_info = wia.DeviceInfos.Item(1)
        device = device_info.Connect()
        
        try:
            for prop in device.Properties:
                if "Document Handling Select" in str(prop.Name):
                    prop.Value = 1  # FEEDER
                    break
        except:
            pass
        
        scan_count = len(self.scanned_images)
        temp_dir = tempfile.gettempdir()
        
        QMessageBox.information(
            self, 'جاري المسح...',
            f'{ICONS.LOADING} المسح التلقائي بدأ\n\nسيتم مسح جميع الأوراق تلقائياً'
        )
        
        while True:
            try:
                item = device.Items[1]
                image = item.Transfer("{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                temp_file = os.path.join(temp_dir, f'auto_scan_{scan_count+1}_{timestamp}.jpg')
                
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                image.SaveFile(temp_file)
                self.scanned_images.append(temp_file)
                scan_count += 1
                self._update_images_count()
                
            except Exception as e:
                if scan_count > 0:
                    reply = QMessageBox.question(
                        self, f'{ICONS.WARNING} انتهى المسح أو حدث خطأ',
                        f'{ICONS.SUCCESS} تم مسح {scan_count} ورقة\n\n'
                        'هل تريد إضافة المزيد من الأوراق والاستمرار؟',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            device = device_info.Connect()
                            continue
                        except:
                            break
                    else:
                        break
                else:
                    break
        
        return scan_count
    
    def _scan_continuous_manual(self):
        """مسح متتالي سريع بدون نوافذ متكررة"""
        QMessageBox.information(
            self, 'مسح متتالي',
            f'{ICONS.FILE} مسح متتالي سريع\n\n'
            'ضع جميع الأوراق جاهزة\n'
            'اضغط Cancel عند الانتهاء من آخر ورقة'
        )
        
        wia = win32com.client.Dispatch("WIA.CommonDialog")
        scan_count = len(self.scanned_images)
        temp_dir = tempfile.gettempdir()
        consecutive_errors = 0
        
        while True:
            try:
                image = wia.ShowAcquireImage()
                
                if not image:
                    break
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                temp_file = os.path.join(temp_dir, f'scanned_{scan_count+1}_{timestamp}.jpg')
                
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                
                image.SaveFile(temp_file)
                self.scanned_images.append(temp_file)
                scan_count += 1
                self._update_images_count()
                consecutive_errors = 0
                
            except Exception as e:
                consecutive_errors += 1
                
                if scan_count > 0:
                    reply = QMessageBox.question(
                        self, f'{ICONS.WARNING} خطأ في السكانر',
                        f'حدث خطأ في السكانر\n\n'
                        f'{ICONS.SUCCESS} تم مسح {scan_count} ورقة بنجاح\n\n'
                        'هل تريد الاستئناف؟',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            wia = win32com.client.Dispatch("WIA.CommonDialog")
                            consecutive_errors = 0
                            continue
                        except:
                            break
                    else:
                        break
                else:
                    if consecutive_errors >= 2:
                        raise e
                    
                    reply = QMessageBox.question(
                        self, 'خطأ في السكانر',
                        f'حدث خطأ: {str(e)}\n\nهل تريد المحاولة مرة أخرى؟',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply != QMessageBox.StandardButton.Yes:
                        raise e
                    
                    try:
                        wia = win32com.client.Dispatch("WIA.CommonDialog")
                        continue
                    except:
                        raise e
        
        if scan_count > 0:
            self._handle_scanned_documents(scan_count)
    
    def _handle_scanned_documents(self, scan_count):
        """معالجة الوثائق الممسوحة"""
        self.scanned_image_path = self.scanned_images[0]
        
        if scan_count > 1:
            reply = QMessageBox.question(
                self, 'معلومات المرفقات',
                f'{ICONS.SUCCESS} تم مسح {scan_count} وثيقة/مرفق بنجاح!\n\n'
                f'• الورقة الأولى: الوثيقة الرئيسية\n'
                f'• {scan_count - 1} ورقة: مرفقات\n\n'
                'هل تريد إدخال معلومات منفصلة لكل مرفق؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._collect_attachment_details()
            else:
                QMessageBox.information(
                    self, f'تم {ICONS.SUCCESS}',
                    f'تم مسح {scan_count} صفحة (1 رئيسية + {scan_count-1} مرفق)\n\n'
                    'أدخل معلومات الوثيقة الرئيسية في الحقول أدناه'
                )
        else:
            QMessageBox.information(
                self, f'تم المسح {ICONS.SUCCESS}',
                'تم مسح الوثيقة الرئيسية\n\nأدخل المعلومات في الحقول أدناه'
            )
    
    def _collect_attachment_details(self):
        """جمع معلومات تفصيلية لجميع المرفقات"""
        dialog = AttachmentDetailsDialog(
            self, 
            self.scanned_images, 
            start_index=1
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            all_data = dialog.get_all_data()
            self.attachment_details_dict = dict(all_data)
            
            valid_count = len([
                v for v in all_data.values() 
                if v and any(str(x).strip() for x in v.values() if x)
            ])
            
            QMessageBox.information(
                self, f'تم {ICONS.SUCCESS}',
                f'تم إدخال معلومات {valid_count} مرفق بنجاح\n\n'
                'أدخل معلومات الوثيقة الرئيسية في الحقول أدناه'
            )
        else:
            self.attachment_details_dict = {}
            QMessageBox.information(
                self, 'تم',
                'سيتم استخدام معلومات الوثيقة الرئيسية لجميع المرفقات'
            )
    
    # =========================================================================
    # وظائف OCR
    # =========================================================================
    
    def scan_and_extract(self):
        """مسح من السكانر واستخراج المعلومات تلقائياً (بطيء)"""
        global SCANNER_AVAILABLE, SCANNER_COUNT
        
        if not SCANNER_AVAILABLE:
            reply = QMessageBox.question(
                self, 'السكانر غير متاح',
                f'{ICONS.WARNING} مكتبة السكانر (pywin32) غير مثبتة\n\n'
                'هل تريد اختيار صورة من الحاسب لاستخراج المعلومات منها؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.extract_from_image()
            return
        
        self._update_scanner_status()
        if SCANNER_COUNT == 0:
            reply = QMessageBox.question(
                self, 'السكانر غير متصل',
                f'{ICONS.WARNING} لا يوجد سكانر متصل بالحاسب\n\n'
                'هل تريد اختيار صورة من الحاسب لاستخراج المعلومات منها؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.extract_from_image()
            return
        
        try:
            reply = QMessageBox.warning(
                self, 'تحذير',
                'الاستخراج التلقائي قد يستغرق 1-2 دقيقة!\n\nهل تريد المتابعة؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            year_folder = self._get_year_folder()
            if not year_folder:
                return
            
            QMessageBox.information(
                self, 'جاري المسح',
                'سيتم فتح نافذة السكانر\n\nضع الوثيقة في السكانر واضغط Scan'
            )
            
            wia = win32com.client.Dispatch("WIA.CommonDialog")
            image = wia.ShowAcquireImage()
            
            if not image:
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f'scanned_{timestamp}.jpg')
            
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            image.SaveFile(temp_file)
            
            if not os.path.exists(temp_file):
                raise Exception("فشل حفظ الصورة الممسوحة")
            
            self._process_scanned_image(temp_file)
            
        except Exception as e:
            QMessageBox.critical(
                self, 'خطأ',
                f'خطأ في المسح الضوئي:\n{str(e)}'
            )
    
    def extract_from_image(self):
        """استخراج المعلومات من ملف صورة موجود"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'اختر صورة الوثيقة',
            '', 'صور (*.jpg *.jpeg *.png *.tiff *.bmp);;جميع الملفات (*)'
        )
        
        if file_path:
            self._process_scanned_image(file_path)
    
    def _process_scanned_image(self, image_path):
        """معالجة الصورة الممسوحة واستخراج المعلومات"""
        
        class OCRWorker(QThread):
            finished = pyqtSignal(object)
            failed = pyqtSignal(str)
            
            def __init__(self, img_path):
                super().__init__()
                self.img_path = img_path
            
            def run(self):
                try:
                    from ..ocr_extractor import OCRExtractor
                    extractor = OCRExtractor()
                    info = extractor.extract_document_info(self.img_path)
                    self.finished.emit(info)
                except Exception as e:
                    self.failed.emit(str(e))
        
        progress = QProgressDialog('جاري استخراج المعلومات...', 'إلغاء', 0, 0, self)
        progress.setWindowTitle('استخراج المضمون')
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        worker = OCRWorker(image_path)
        
        def on_finished(info):
            progress.close()
            try:
                if info and (info.get('doc_number') or info.get('doc_date')):
                    self._fill_fields(info)
                    self._save_with_image(image_path, info)
                else:
                    QMessageBox.warning(
                        self, 'تنبيه', 
                        'لم يتم استخراج معلومات. أدخلها يدوياً'
                    )
                    self.scanned_image_path = image_path
            except Exception as e:
                QMessageBox.critical(
                    self, 'خطأ', 
                    f'خطأ في معالجة نتيجة الاستخراج: {str(e)}'
                )
        
        def on_failed(err):
            progress.close()
            QMessageBox.critical(
                self, 'خطأ', 
                f'خطأ في الاستخراج: {err}\n\nأدخل المعلومات يدوياً'
            )
            self.scanned_image_path = image_path
        
        worker.finished.connect(on_finished)
        worker.failed.connect(on_failed)
        
        self._ocr_worker = worker
        worker.start()
    
    def _fill_fields(self, info):
        """ملء الحقول بالمعلومات المستخرجة"""
        if info.get('doc_number'):
            self.doc_name.setText(info['doc_number'])
        if info.get('doc_date'):
            self.doc_date.setText(info['doc_date'])
        if info.get('doc_title'):
            self.doc_title.setText(info['doc_title'])
        if info.get('issuing_dept'):
            index = self.issuing_dept.findText(info['issuing_dept'])
            if index >= 0:
                self.issuing_dept.setCurrentIndex(index)
    
    def _save_with_image(self, image_path, info):
        """حفظ الوثيقة والصورة تلقائياً"""
        if not self.db or not self.image_manager:
            return
        
        try:
            doc_name = info.get('doc_number', '')
            if info.get('doc_date'):
                doc_name += f" في {info['doc_date']}"
            
            doc_id = self.db.add_document(
                doc_name,
                info.get('doc_date', ''),
                info.get('doc_title', ''),
                info.get('issuing_dept', ''),
                '', ''
            )
            
            if image_path and os.path.exists(image_path):
                year_folder = self.selected_year_folder
                if not year_folder:
                    year_folder = self.select_year_folder()
                
                if not year_folder:
                    QMessageBox.warning(
                        self, 'تنبيه', 
                        'يجب اختيار أو إنشاء مجلد سنة لحفظ الصورة'
                    )
                    return
                
                incoming_dir = os.path.join(year_folder, '_incoming')
                os.makedirs(incoming_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                basename = os.path.basename(image_path)
                temp_name = f"{timestamp}_{basename}"
                temp_dest = os.path.join(incoming_dir, temp_name)
                shutil.copy2(image_path, temp_dest)
                
                try:
                    year_name = Path(year_folder).name
                except Exception:
                    year_name = None
                
                saved_path = self.image_manager.save_image(
                    temp_dest, doc_id, 1, year=year_name
                )
                
                self.db.add_image(doc_id, saved_path, basename, 1, None, 1, None)
                
                try:
                    os.remove(temp_dest)
                except Exception:
                    pass
            
            QMessageBox.information(
                self, f'تم الحفظ {ICONS.SUCCESS}',
                f'تم حفظ الوثيقة:\n• {doc_name}\n\nيمكنك البحث عنها وطباعتها'
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'خطأ في الحفظ: {str(e)}')
    
    # =========================================================================
    # وظائف الحصول على البيانات
    # =========================================================================
    
    def get_data(self):
        """الحصول على البيانات المدخلة"""
        dept = self.issuing_dept.currentText()
        if dept == APP_SETTINGS.DEFAULT_DEPARTMENTS[0]:
            dept = ''
        
        return {
            'doc_name': self.doc_name.text(),
            'doc_date': self.doc_date.text(),
            'doc_title': self.doc_title.text(),
            'issuing_dept': dept,
            'doc_classification': self.doc_classification.text(),
            'legal_paragraph': self.legal_paragraph.toPlainText(),
            'sides': self.sides.value(),
            'scanned_image': self.scanned_image_path,
            'scanned_images': self.scanned_images,
            'attachment_details_dict': self.attachment_details_dict,
            'selected_year_folder': self.selected_year_folder
        }
