"""
نافذة استيراد الصور
Import Images Dialog

نافذة حوار لاستيراد صور الوثائق من الحاسب أو مجلد كامل
"""

import os
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QDialogButtonBox,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt

from ..constants import ICONS, APP_SETTINGS, COLORS, FONT_SIZES, DIMENSIONS
from ..filename_parser import FilenameParser, ImageSequenceHandler
from .utils import choose_year_folder


class ImportImagesDialog(QDialog):
    """
    نافذة حوار لاستيراد الصور
    
    تتيح هذه النافذة:
    - اختيار صور فردية
    - اختيار مجلد كامل
    - معاينة الملفات المختارة
    - تحليل أسماء الملفات
    """
    
    def __init__(self, parent=None):
        """
        تهيئة النافذة
        
        Args:
            parent: النافذة الأب
        """
        super().__init__(parent)
        self.setWindowTitle('🎨 استيراد الصور والوثائق')
        
        # حجم النافذة المحسّن والمتناسق
        if parent:
            parent_geom = parent.geometry()
            self.setGeometry(
                parent_geom.x() + 100,
                parent_geom.y() + 80,
                850, 650
            )
        else:
            self.setGeometry(250, 120, 850, 650)
        
        self.setMinimumSize(750, 550)
        self.selected_files = []
        self._init_ui()
        self.apply_dialog_styles()

    def apply_dialog_styles(self):
        """تطبيق الأنماط الحضارية الجميلة والأنيقة"""
        self.setStyleSheet(f"""
            /* النافذة الرئيسية مع خلفية عصرية */
            QDialog {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f8fafc,
                    stop: 0.3 {COLORS.BACKGROUND_WHITE},
                    stop: 0.7 #f1f5f9,
                    stop: 1 {COLORS.BACKGROUND_LIGHT});
                color: {COLORS.TEXT_PRIMARY};
                font-size: {FONT_SIZES.BODY}px;
                font-family: 'Segoe UI', 'Tahoma', 'Cairo', Arial, sans-serif;
                border-radius: 15px;
                border: 2px solid {COLORS.BORDER};
            }}
            
            /* العناوين والتسميات الجميلة */
            QLabel {{
                color: {COLORS.TEXT_PRIMARY};
                font-weight: 500;
                padding: 8px 6px;
            }}
            
            QLabel[class="title"] {{
                font-size: 15px;
                font-weight: 700;
                color: white;
                padding: 10px 16px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #6366f1,
                    stop: 0.3 {COLORS.ACCENT},
                    stop: 0.7 #8b5cf6,
                    stop: 1 #a855f7);
                border-radius: 8px;
                margin: 2px 0;
                border: 1px solid #4f46e5;
            }}
            
            QLabel[class="section-header"] {{
                font-size: 14px;
                font-weight: 600;
                color: {COLORS.ACCENT};
                padding: 10px 8px 8px 8px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(99, 102, 241, 0.1),
                    stop: 1 rgba(139, 92, 246, 0.1));
                border-bottom: 2px solid {COLORS.ACCENT};
                border-radius: 6px 6px 0 0;
                margin-top: 12px;
            }}
            
            /* أزرار عصرية وجميلة */
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #6366f1,
                    stop: 0.5 {COLORS.ACCENT},
                    stop: 1 #4f46e5);
                color: white;
                border: 2px solid #4f46e5;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
                margin: 3px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #8b5cf6,
                    stop: 0.5 #7c3aed,
                    stop: 1 #6d28d9);
                border-color: #6d28d9;
                color: white;
            }}
            
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5b21b6,
                    stop: 1 #4c1d95);
                border-color: #4c1d95;
            }}
            
            /* أزرار مخصصة جميلة */
            QPushButton[class="primary"] {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #10b981,
                    stop: 0.3 {COLORS.SUCCESS},
                    stop: 0.7 #059669,
                    stop: 1 #047857);
                border: 2px solid #059669;
                font-size: 14px;
                min-height: 22px;
                padding: 14px 20px;
                font-weight: 700;
            }}
            
            QPushButton[class="primary"]:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #34d399,
                    stop: 0.5 #10b981,
                    stop: 1 #059669);
                border-color: #065f46;
            }}
            
            QPushButton[class="secondary"] {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #64748b,
                    stop: 1 #475569);
                border: 2px solid #475569;
                font-size: 12px;
                padding: 8px 14px;
                min-height: 18px;
            }}
            
            QPushButton[class="secondary"]:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #94a3b8,
                    stop: 1 #64748b);
            }}
            
            QPushButton[class="danger"] {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f87171,
                    stop: 0.5 {COLORS.ERROR},
                    stop: 1 #dc2626);
                border: 2px solid #dc2626;
            }}
            
            QPushButton[class="danger"]:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #fca5a5,
                    stop: 0.5 #f87171,
                    stop: 1 #ef4444);
            }}
            
            /* قائمة الملفات الجميلة والمرتبة */
            QListWidget {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {COLORS.BACKGROUND_WHITE},
                    stop: 0.5 #fefefe,
                    stop: 1 #fafbfc);
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 12px;
                font-size: 13px;
                selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #6366f1,
                    stop: 1 #8b5cf6);
                alternate-background-color: #f8fafc;
                gridline-color: #e2e8f0;
            }}
            
            QListWidget::item {{
                padding: 14px 12px;
                border-bottom: 1px solid #f1f5f9;
                border-radius: 8px;
                margin: 3px 2px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {COLORS.BACKGROUND_WHITE},
                    stop: 1 #fefefe);
                border-left: 3px solid transparent;
            }}
            
            QListWidget::item:selected {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #6366f1,
                    stop: 0.5 {COLORS.ACCENT},
                    stop: 1 #8b5cf6);
                color: white;
                font-weight: 600;
                border-left: 3px solid #fbbf24;
                border-radius: 8px;
            }}
            
            QListWidget::item:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #f0f9ff,
                    stop: 0.5 #e0f2fe,
                    stop: 1 #f1f5f9);
                border: 1px solid {COLORS.ACCENT};
                border-left: 3px solid {COLORS.ACCENT};
            }}
            
            /* مربع النص الجميل */
            QTextEdit {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {COLORS.BACKGROUND_WHITE},
                    stop: 0.3 #fefefe,
                    stop: 0.7 #f8fafc,
                    stop: 1 #f1f5f9);
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
                font-size: 13px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                line-height: 1.5;
                color: #374151;
            }}
            
            QTextEdit:focus {{
                border-color: {COLORS.ACCENT};
                background: {COLORS.BACKGROUND_WHITE};
            }}
            
            /* مربع الحوار الجميل */
            QDialogButtonBox {{
                padding: 16px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {COLORS.BACKGROUND_WHITE},
                    stop: 1 #f8fafc);
                border-top: 1px solid #e2e8f0;
                border-radius: 0 0 12px 12px;
            }}
            
            QDialogButtonBox QPushButton {{
                min-width: 130px;
                min-height: 40px;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 24px;
                margin: 4px 8px;
            }}
        """)
    
    def _init_ui(self):
        """إنشاء واجهة مستخدم مدمجة ومتناسقة"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # عنوان النافذة الجميل
        self._create_header(layout)
        
        # أزرار الاستيراد المحسّنة
        self._create_import_buttons(layout)
        
        # قائمة الملفات المحسّنة
        self._create_file_list(layout)
        
        # معلومات التحليل المحسّنة
        self._create_info_section(layout)
        
        # أزرار الحوار المحسّنة
        self._create_dialog_buttons(layout)
        
        self.setLayout(layout)
    
    def _create_header(self, parent_layout):
        """إنشاء عنوان النافذة بتصميم جميل وعصري"""
        # حاوي العنوان مع تصميم جميل
        header_container = QHBoxLayout()
        header_container.setContentsMargins(0, 0, 0, 12)
        header_container.setSpacing(10)
        
        # أيقونة جميلة يسار
        icon_label = QLabel("🎨")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                padding: 8px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #fbbf24, stop: 1 #f59e0b);
                border-radius: 50%;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # العنوان الرئيسي الجميل
        header_label = QLabel("استيراد وترتيب الصور")
        header_label.setProperty("class", "title")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # ترتيب جميل للعناصر
        header_container.addStretch(1)
        header_container.addWidget(icon_label)
        header_container.addWidget(header_label, 2)
        header_container.addStretch(1)
        
        parent_layout.addLayout(header_container)
    
    def _create_import_buttons(self, parent_layout):
        """إنشاء أزرار الاستيراد بتصميم جميل ومرتب"""
        # عنوان القسم بتصميم جميل
        section_label = QLabel("📎 خيارات الاستيراد والتحميل")
        section_label.setProperty("class", "section-header")
        parent_layout.addWidget(section_label)
        
        # حاوي الأزرار الجميل
        button_container = QHBoxLayout()
        button_container.setSpacing(15)
        button_container.setContentsMargins(10, 12, 10, 15)
        
        # زر اختيار صور فردية جميل
        select_btn = QPushButton(f'📄 اختيار صور متعددة')
        select_btn.setProperty("class", "primary")
        select_btn.clicked.connect(self.select_files)
        select_btn.setToolTip("اختر ملفات صور متعددة من أماكن مختلفة")
        button_container.addWidget(select_btn)
        
        # زر اختيار مجلد كامل جميل
        select_folder_btn = QPushButton(f'🗂️ استيراد مجلد بالكامل')
        select_folder_btn.setProperty("class", "primary")
        select_folder_btn.clicked.connect(self.select_folder)
        select_folder_btn.setToolTip("استيراد جميع صور مجلد ومجلداته الفرعية")
        button_container.addWidget(select_folder_btn)
        
        parent_layout.addLayout(button_container)
    
    def _create_file_list(self, parent_layout):
        """إنشاء قائمة الملفات بتصميم جدول جميل ومرتب"""
        # عنوان القسم الجميل
        files_label = QLabel("📁 قائمة الملفات المختارة والمرتبة")
        files_label.setProperty("class", "section-header")
        parent_layout.addWidget(files_label)
        
        # شريط أزرار التحكم الجميل
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)
        control_layout.setContentsMargins(6, 10, 6, 10)
        
        # عداد الملفات بتصميم جميل
        self.files_count_label = QLabel("📈 إحصائيات: 0 ملف")
        self.files_count_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.ACCENT};
                font-weight: 600;
                font-size: 13px;
                padding: 8px 12px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(99, 102, 241, 0.1),
                    stop: 1 rgba(139, 92, 246, 0.1));
                border-radius: 6px;
                border: 1px solid {COLORS.BORDER};
            }}
        """)
        control_layout.addWidget(self.files_count_label)
        
        control_layout.addStretch()
        
        # أزرار التحكم الجميلة
        select_all_btn = QPushButton(f'✅ تحديد الة')
        select_all_btn.setProperty("class", "secondary")
        select_all_btn.clicked.connect(self.select_all_files)
        select_all_btn.setFixedWidth(110)
        control_layout.addWidget(select_all_btn)
        
        delete_btn = QPushButton(f'🗑️ حذف المحدد')
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(self.delete_selected)
        delete_btn.setFixedWidth(110)
        control_layout.addWidget(delete_btn)
        
        parent_layout.addLayout(control_layout)
        
        # قائمة الملفات الجميلة والمرتبة
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.file_list.setAlternatingRowColors(True)
        self.file_list.setSortingEnabled(True)
        self.file_list.setMaximumHeight(220)  # ارتفاع مناسب
        self.file_list.setSpacing(2)
        parent_layout.addWidget(self.file_list)
    
    def _create_info_section(self, parent_layout):
        """إنشاء قسم معلومات التحليل المدمج"""
        # عنوان القسم مصغر
        info_label = QLabel("🔍 تحليل الملفات")
        info_label.setProperty("class", "section-header")
        parent_layout.addWidget(info_label)
        
        # مربع النص المحسّن والمدمج
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(120)  # ارتفاع مخفض
        self.info_text.setPlaceholderText("📈 ستظهر هنا معلومات مفصلة عن الملفات المختارة...")
        parent_layout.addWidget(self.info_text)
    
    def _create_dialog_buttons(self, parent_layout):
        """إنشاء أزرار الحوار المحسّنة"""
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        
        # تخصيص أزرار محسّنة
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("✅ موافق - استيراد")
        ok_button.setProperty("class", "primary")
        
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("❌ إلغاء")
        cancel_button.setProperty("class", "secondary")
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        parent_layout.addWidget(button_box)
    
    def select_files(self):
        """اختيار الملفات"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'اختر صور الوثائق',
            '',
            'صور (*.jpg *.jpeg *.png *.tiff *.bmp)'
        )
        
        if files:
            # اختيار مجلد السنة
            year_folder = choose_year_folder(self)
            if not year_folder:
                QMessageBox.warning(self, 'تنبيه', 'يجب اختيار أو إنشاء مجلد سنة')
                return
            
            # نسخ الملفات إلى مجلد السنة
            dest_files = []
            for f in files:
                try:
                    basename = os.path.basename(f)
                    dest = os.path.join(year_folder, basename)
                    shutil.copy2(f, dest)
                    dest_files.append(dest)
                except Exception as e:
                    print(f"خطأ في نسخ الملف {f}: {e}")
            
            if dest_files:
                self.selected_files = dest_files
                self._update_list()
            else:
                QMessageBox.warning(self, 'تنبيه', 'لم يتم نسخ أي ملفات')
    
    def select_folder(self):
        """اختيار مجلد كامل والبحث عن جميع الصور فيه"""
        folder = QFileDialog.getExistingDirectory(
            self,
            'اختر مجلد يحتوي على الصور'
        )
        
        if folder:
            # اختيار مجلد السنة
            year_folder = choose_year_folder(self)
            if not year_folder:
                QMessageBox.warning(self, 'تنبيه', 'يجب اختيار أو إنشاء مجلد سنة')
                return
            
            # البحث عن جميع الصور في المجلد والمجلدات الفرعية
            folder_path = Path(folder)
            image_extensions = set(APP_SETTINGS.SUPPORTED_IMAGE_FORMATS)
            files = []
            
            for ext in image_extensions:
                files.extend([str(f) for f in folder_path.glob(f'*{ext}')])
                files.extend([str(f) for f in folder_path.glob(f'*{ext.upper()}')])
                files.extend([str(f) for f in folder_path.glob(f'**/*{ext}')])
                files.extend([str(f) for f in folder_path.glob(f'**/*{ext.upper()}')])
            
            if files:
                # إزالة التكرارات والترتيب
                found_files = sorted(list(set(files)))
                
                # نسخ الملفات إلى مجلد السنة
                dest_files = []
                for fp in found_files:
                    try:
                        basename = os.path.basename(fp)
                        dest = os.path.join(year_folder, basename)
                        shutil.copy2(fp, dest)
                        dest_files.append(dest)
                    except Exception:
                        pass
                
                self.selected_files = dest_files
                
                count = len(self.selected_files)
                QMessageBox.information(
                    self,
                    '🎉 تم الاستيراد بنجاح',
                    f'✅ تم استيراد {count} صورة بنجاح!\n\n'
                    f'📁 مجلد الحفظ: {year_folder}\n\n'
                    f'🔍 يمكنك الآن مراجعة وتحليل الملفات المستوردة.'
                )
                
                self._update_list()
            else:
                QMessageBox.warning(self, 'تنبيه', 'لم يتم العثور على صور في المجلد')
    
    def _update_list(self):
        """تحديث قائمة الملفات وتحليلها بأسلوب حضاري"""
        self.file_list.clear()
        
        # تحديث عداد الملفات بتصميم جميل
        count = len(self.selected_files)
        self.files_count_label.setText(f"📈 إحصائيات: {count} ملف")
        
        # نص التحليل محسّن
        info_text = '🔍 تحليل ومعاينة الملفات:\n'
        info_text += '=' * 55 + '\n\n'
        
        if count == 0:
            info_text += '📄 لم يتم اختيار أي ملفات بعد.\n'
            info_text += '🔎 استخدم الأزرار في الأعلى لاختيار الصور.\n'
        else:
            # تجميع الصور
            ImageSequenceHandler.group_images(
                [os.path.basename(f) for f in self.selected_files]
            )
            
            info_text += f'🏆 تم استيراد {count} ملف بنجاح!\n\n'
            
            for i, filename in enumerate(self.selected_files, 1):
                basename = os.path.basename(filename)
                # تصميم جميل لعناصر القائمة
                item_text = f"🇫🇷 {i:03d}. 🖼️ {basename}"
                item = QListWidgetItem(item_text)
                
                # إضافة أيقونات وفقاً لنوع الملف
                if basename.lower().endswith(('.jpg', '.jpeg')):
                    item.setText(f"🌄 {i:03d}. 🖼️ {basename}")
                elif basename.lower().endswith('.png'):
                    item.setText(f"🎨 {i:03d}. 🖼️ {basename}")
                elif basename.lower().endswith(('.tiff', '.tif')):
                    item.setText(f"📎 {i:03d}. 🖼️ {basename}")
                    
                self.file_list.addItem(item)
                
                # تحليل الملف
                parsed = FilenameParser.parse_filename(basename)
                if parsed['is_valid']:
                    info_text += f"\n📁 [{i:02d}] {basename}\n"
                    info_text += f"   • 🔢 الرقم: {parsed['number']}\n"
                    info_text += f"   • 📅 التاريخ: {parsed['date']}\n"
                    info_text += f"   • 🏢 الجهة: {parsed['department']}\n"
                    if parsed.get('sequence'):
                        info_text += f"   • 🔄 التسلسل: {parsed['sequence']}\n"
                else:
                    info_text += f"\n⚠️ [{i:02d}] {basename}\n   • ملف غير محلل (قد يحتاج إعادة تسمية)\n"
        
        self.info_text.setText(info_text)
    
    def select_all_files(self):
        """تحديد جميع الملفات في القائمة"""
        for i in range(self.file_list.count()):
            self.file_list.item(i).setSelected(True)
        
        QMessageBox.information(
            self, 'تحديد', 
            f'تم تحديد جميع الملفات ({self.file_list.count()} ملف)'
        )
    
    def delete_selected(self):
        """حذف الملفات المحددة بعد التنبيه"""
        selected_items = self.file_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, 'تنبيه', 'يجب تحديد ملفات للحذف أولاً')
            return
        
        count = len(selected_items)
        reply = QMessageBox.question(
            self,
            'تأكيد الحذف',
            f'هل تريد حذف {count} ملف من القائمة؟\n\n'
            'لن يتم حذفها من الحاسب، فقط من قائمة الاستيراد',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # احصل على أسماء الملفات المحددة
            selected_names = [item.text() for item in selected_items]
            
            # احذفها من selected_files
            self.selected_files = [
                f for f in self.selected_files 
                if os.path.basename(f) not in selected_names
            ]
            
            # احذفها من القائمة المرئية
            for i in range(self.file_list.count() - 1, -1, -1):
                if self.file_list.item(i) in selected_items:
                    self.file_list.takeItem(i)
            
            # تحديث المعلومات
            self._update_list()
            QMessageBox.information(self, 'نجح', f'تم حذف {count} ملف من القائمة')
    
    def get_files(self):
        """
        الحصول على الملفات المختارة
        
        Returns:
            list: قائمة مسارات الملفات المختارة
        """
        return self.selected_files
