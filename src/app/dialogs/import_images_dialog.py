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
        self.setWindowTitle('استيراد الصور')
        self.setGeometry(100, 100, 700, 500)
        self.selected_files = []
        self._init_ui()
        self.apply_dialog_styles()

    def apply_dialog_styles(self):
        """Apply dialog-level styles to match the light theme"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS.BACKGROUND_LIGHT};
                color: {COLORS.TEXT_PRIMARY};
                font-size: {FONT_SIZES.BODY}px;
                font-family: {FONT_FAMILIES.DEFAULT if 'FONT_FAMILIES' in globals() else 'Segoe UI'};
            }}
            QPushButton {{
                background-color: {COLORS.ACCENT};
                color: {COLORS.TEXT_WHITE};
                border: 1px solid {COLORS.BORDER};
                border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
                padding: {DIMENSIONS.PADDING_SMALL}px {DIMENSIONS.PADDING_MEDIUM}px;
                min-height: {DIMENSIONS.BUTTON_HEIGHT}px;
            }}
            QListWidget {{
                background-color: {COLORS.BACKGROUND_WHITE};
                border: 1px solid {COLORS.BORDER};
            }}
            QTextEdit {{
                background-color: {COLORS.BACKGROUND_WHITE};
                border: 1px solid {COLORS.BORDER};
            }}
        """)
    
    def _init_ui(self):
        """إنشاء واجهة المستخدم"""
        layout = QVBoxLayout()
        layout.setSpacing(DIMENSIONS.PADDING_MEDIUM)
        layout.setContentsMargins(
            DIMENSIONS.MARGIN_MEDIUM, DIMENSIONS.MARGIN_MEDIUM,
            DIMENSIONS.MARGIN_MEDIUM, DIMENSIONS.MARGIN_MEDIUM
        )
        
        # أزرار الاستيراد
        self._create_import_buttons(layout)
        
        # قائمة الملفات
        self._create_file_list(layout)
        
        # معلومات التحليل
        self._create_info_section(layout)
        
        # أزرار الحوار
        self._create_dialog_buttons(layout)
        
        self.setLayout(layout)
    
    def _create_import_buttons(self, parent_layout):
        """إنشاء أزرار الاستيراد"""
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton(f'{ICONS.FILE} اختر صور من الحاسب')
        select_btn.clicked.connect(self.select_files)
        button_layout.addWidget(select_btn)
        
        select_folder_btn = QPushButton(f'{ICONS.FOLDER} اختر مجلد كامل')
        select_folder_btn.clicked.connect(self.select_folder)
        button_layout.addWidget(select_folder_btn)
        
        parent_layout.addLayout(button_layout)
    
    def _create_file_list(self, parent_layout):
        """إنشاء قائمة الملفات المختارة"""
        # شريط العنوان مع أزرار التحكم
        file_label_layout = QHBoxLayout()
        file_label_layout.setSpacing(DIMENSIONS.PADDING_SMALL)
        file_label_layout.addWidget(QLabel('الملفات المختارة:'))
        file_label_layout.addStretch()
        
        select_all_btn = QPushButton(f'{ICONS.CHECKBOX} تحديد الكل')
        select_all_btn.clicked.connect(self.select_all_files)
        select_all_btn.setMaximumWidth(100)
        file_label_layout.addWidget(select_all_btn)
        
        delete_btn = QPushButton(f'{ICONS.DELETE} حذف المحددة')
        delete_btn.clicked.connect(self.delete_selected)
        delete_btn.setMaximumWidth(100)
        file_label_layout.addWidget(delete_btn)
        
        parent_layout.addLayout(file_label_layout)
        
        # قائمة الملفات
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        parent_layout.addWidget(self.file_list)
    
    def _create_info_section(self, parent_layout):
        """إنشاء قسم معلومات التحليل"""
        parent_layout.addWidget(QLabel('معلومات الملفات المكتشفة:'))
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        parent_layout.addWidget(self.info_text)
    
    def _create_dialog_buttons(self, parent_layout):
        """إنشاء أزرار الحوار"""
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
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
                    'تم الاستيراد',
                    f'تم استيراد {count} صورة إلى مجلد السنة: {year_folder}'
                )
                
                self._update_list()
            else:
                QMessageBox.warning(self, 'تنبيه', 'لم يتم العثور على صور في المجلد')
    
    def _update_list(self):
        """تحديث قائمة الملفات وتحليلها"""
        self.file_list.clear()
        info_text = 'تحليل الملفات:\n' + '='*50 + '\n'
        
        # تجميع الصور
        ImageSequenceHandler.group_images(
            [os.path.basename(f) for f in self.selected_files]
        )
        
        for filename in self.selected_files:
            basename = os.path.basename(filename)
            item = QListWidgetItem(basename)
            self.file_list.addItem(item)
            
            # تحليل الملف
            parsed = FilenameParser.parse_filename(basename)
            if parsed['is_valid']:
                info_text += f"\n{ICONS.FILE} {basename}\n"
                info_text += f"  • الرقم: {parsed['number']}\n"
                info_text += f"  • التاريخ: {parsed['date']}\n"
                info_text += f"  • الجهة: {parsed['department']}\n"
                if parsed.get('sequence'):
                    info_text += f"  • التسلسل: {parsed['sequence']}\n"
        
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
