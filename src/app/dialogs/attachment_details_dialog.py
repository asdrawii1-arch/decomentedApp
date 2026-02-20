"""
نافذة معلومات المرفقات
Attachment Details Dialog

نافذة لإدخال معلومات المرفقات مع معاينة الصور والتنقل بينها
"""

import os
import tempfile

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from ..constants import COLORS, FONT_SIZES, DIMENSIONS, ICONS, APP_SETTINGS
from ..ui_styles import TITLE_STYLES, NAV_STYLES, IMAGE_PREVIEW_STYLE, BUTTON_STYLES


class AttachmentDetailsDialog(QDialog):
    """
    نافذة لإدخال معلومات المرفقات مع معاينة الصور
    
    تتيح هذه النافذة للمستخدم:
    - مشاهدة صورة المرفق
    - إدخال معلومات تفصيلية لكل مرفق
    - التنقل بين المرفقات
    """
    
    def __init__(self, parent=None, scanned_images=None, start_index=0):
        """
        تهيئة النافذة
        
        Args:
            parent: النافذة الأب
            scanned_images: قائمة مسارات الصور الممسوحة
            start_index: فهرس البداية (عادة 1 لتخطي الوثيقة الرئيسية)
        """
        super().__init__(parent)
        self.scanned_images = scanned_images or []
        self.current_index = start_index
        self.attachment_data = {}  # قاموس لتخزين بيانات كل مرفق
        
        self.setWindowTitle('معلومات المرفقات')
        self.setGeometry(100, 100, 950, 650)
        self._init_ui()
        self.apply_dialog_styles()
        self.load_attachment(self.current_index)

    def apply_dialog_styles(self):
        """Apply light-theme styles to this dialog"""
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
            QLabel {{
                color: {COLORS.TEXT_PRIMARY};
            }}
        """)
    
    def _init_ui(self):
        """إنشاء واجهة المستخدم"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(DIMENSIONS.PADDING_MEDIUM)
        main_layout.setContentsMargins(
            DIMENSIONS.MARGIN_MEDIUM, DIMENSIONS.MARGIN_MEDIUM,
            DIMENSIONS.MARGIN_MEDIUM, DIMENSIONS.MARGIN_MEDIUM
        )
        
        # شريط العنوان
        self._create_header(main_layout)
        
        # المحتوى الرئيسي (صورة + معلومات)
        self._create_content(main_layout)
        
        # أزرار التنقل
        self._create_navigation(main_layout)
        
        # أزرار الإجراءات
        self._create_action_buttons(main_layout)
        
        self.setLayout(main_layout)
    
    def _create_header(self, parent_layout):
        """إنشاء شريط العنوان"""
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet(TITLE_STYLES['medium'])
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def _create_content(self, parent_layout):
        """إنشاء قسم المحتوى (صورة + معلومات)"""
        content_layout = QHBoxLayout()
        
        # قسم الصورة (يسار)
        self._create_image_section(content_layout)
        
        # قسم المعلومات (يمين)
        self._create_info_section(content_layout)
        
        parent_layout.addLayout(content_layout)
    
    def _create_image_section(self, parent_layout):
        """إنشاء قسم معاينة الصورة"""
        image_group = QGroupBox('معاينة الصورة')
        image_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setMinimumSize(DIMENSIONS.PREVIEW_WIDTH, DIMENSIONS.PREVIEW_HEIGHT)
        self.image_label.setMaximumSize(DIMENSIONS.PREVIEW_WIDTH, DIMENSIONS.PREVIEW_HEIGHT)
        self.image_label.setStyleSheet(IMAGE_PREVIEW_STYLE)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        
        image_layout.addWidget(self.image_label)
        image_group.setLayout(image_layout)
        parent_layout.addWidget(image_group)
    
    def _create_info_section(self, parent_layout):
        """إنشاء قسم معلومات المرفق"""
        info_group = QGroupBox('معلومات المرفق')
        info_layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # رقم الوثيقة/المرفق
        self.doc_name = QLineEdit()
        self.doc_name.setPlaceholderText('رقم الوثيقة/المرفق')
        form_layout.addRow('رقم الوثيقة:', self.doc_name)
        
        # التاريخ
        self.doc_date = QLineEdit()
        self.doc_date.setPlaceholderText('مثال: 23-3-2025')
        form_layout.addRow('التاريخ:', self.doc_date)
        
        # المضمون/العنوان
        self.doc_title = QLineEdit()
        self.doc_title.setPlaceholderText('موضوع المرفق')
        form_layout.addRow('المضمون:', self.doc_title)
        
        # جهة الإصدار
        self.issuing_dept = QComboBox()
        self.issuing_dept.addItems(APP_SETTINGS.DEFAULT_DEPARTMENTS + ['أخرى'])
        form_layout.addRow('جهة الإصدار:', self.issuing_dept)
        
        # التصنيف
        self.doc_classification = QLineEdit()
        self.doc_classification.setPlaceholderText('التصنيف')
        form_layout.addRow('التصنيف:', self.doc_classification)
        
        # الفقرة القانونية
        self.legal_paragraph = QTextEdit()
        self.legal_paragraph.setMaximumHeight(60)
        self.legal_paragraph.setPlaceholderText('الفقرة القانونية')
        form_layout.addRow('الفقرة القانونية:', self.legal_paragraph)
        
        # ملاحظات خاصة بالمرفق
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText('ملاحظات إضافية خاصة بهذا المرفق')
        form_layout.addRow('ملاحظات المرفق:', self.notes)
        
        info_layout.addLayout(form_layout)
        info_group.setLayout(info_layout)
        parent_layout.addWidget(info_group)
    
    def _create_navigation(self, parent_layout):
        """إنشاء أزرار التنقل"""
        nav_layout = QHBoxLayout()
        
        # زر السابق
        self.prev_btn = QPushButton(f'{ICONS.PREVIOUS} السابق')
        self.prev_btn.clicked.connect(self.go_previous)
        self.prev_btn.setStyleSheet(NAV_STYLES['nav_button'])
        nav_layout.addWidget(self.prev_btn)
        
        # مؤشر الموقع
        self.position_label = QLabel()
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_label.setStyleSheet(NAV_STYLES['position_label'])
        nav_layout.addWidget(self.position_label)
        
        # زر التالي
        self.next_btn = QPushButton(f'التالي {ICONS.NEXT}')
        self.next_btn.clicked.connect(self.go_next)
        self.next_btn.setStyleSheet(NAV_STYLES['nav_button'])
        nav_layout.addWidget(self.next_btn)
        
        parent_layout.addLayout(nav_layout)
    
    def _create_action_buttons(self, parent_layout):
        """إنشاء أزرار الإجراءات"""
        button_layout = QHBoxLayout()
        
        # زر الحفظ
        save_all_btn = QPushButton(f'{ICONS.CONFIRM} حفظ والإنهاء')
        save_all_btn.clicked.connect(self.accept)
        save_all_btn.setStyleSheet(BUTTON_STYLES['success'])
        button_layout.addWidget(save_all_btn)
        
        # زر الإلغاء
        cancel_btn = QPushButton(f'{ICONS.CANCEL} إلغاء')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        parent_layout.addLayout(button_layout)
    
    def load_attachment(self, index):
        """
        تحميل معلومات وصورة المرفق الحالي
        
        Args:
            index: فهرس المرفق في قائمة الصور
        """
        if index < 1 or index >= len(self.scanned_images):
            return
        
        # حفظ البيانات الحالية قبل الانتقال
        if self.current_index >= 1 and self.current_index != index:
            self.save_current_data()
        
        self.current_index = index
        
        # تحديث العنوان
        attachment_num = index
        total_attachments = len(self.scanned_images) - 1
        self.title_label.setText(f'{ICONS.ATTACHMENT} المرفق رقم {attachment_num} من {total_attachments}')
        self.position_label.setText(f'{attachment_num} / {total_attachments}')
        
        # تحديث حالة الأزرار
        self.prev_btn.setEnabled(index > 1)
        self.next_btn.setEnabled(index < len(self.scanned_images) - 1)
        
        # تحميل الصورة المصغرة
        self._load_preview_image(index)
        
        # تحميل البيانات المحفوظة إن وجدت
        self._load_saved_data(index)
    
    def _load_preview_image(self, index):
        """تحميل وعرض صورة المعاينة"""
        try:
            from PIL import Image
            
            image_path = self.scanned_images[index]
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img.thumbnail(
                    (DIMENSIONS.PREVIEW_WIDTH, DIMENSIONS.PREVIEW_HEIGHT), 
                    Image.Resampling.LANCZOS
                )
                
                # حفظ مؤقت
                temp_file = os.path.join(tempfile.gettempdir(), 'preview_temp.jpg')
                img.save(temp_file, 'JPEG')
                
                pixmap = QPixmap(temp_file)
                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.setText(f'{ICONS.ERROR} لا يمكن تحميل الصورة')
        except Exception as e:
            self.image_label.setText(f'{ICONS.ERROR} خطأ في تحميل الصورة:\n{str(e)}')
    
    def _load_saved_data(self, index):
        """تحميل البيانات المحفوظة للمرفق"""
        if index in self.attachment_data:
            data = self.attachment_data[index]
            self.doc_name.setText(data.get('doc_name', ''))
            self.doc_date.setText(data.get('doc_date', ''))
            self.doc_title.setText(data.get('doc_title', ''))
            self.doc_classification.setText(data.get('doc_classification', ''))
            self.legal_paragraph.setPlainText(data.get('legal_paragraph', ''))
            self.notes.setPlainText(data.get('notes', ''))
            
            dept = data.get('issuing_dept')
            if dept:
                index_dept = self.issuing_dept.findText(dept)
                if index_dept >= 0:
                    self.issuing_dept.setCurrentIndex(index_dept)
        else:
            # مسح الحقول للمرفق الجديد
            self._clear_fields()
    
    def _clear_fields(self):
        """مسح جميع الحقول"""
        self.doc_name.clear()
        self.doc_date.clear()
        self.doc_title.clear()
        self.doc_classification.clear()
        self.legal_paragraph.clear()
        self.notes.clear()
        self.issuing_dept.setCurrentIndex(0)
    
    def save_current_data(self):
        """حفظ بيانات المرفق الحالي"""
        dept = self.issuing_dept.currentText()
        
        data = {
            'doc_name': self.doc_name.text(),
            'doc_date': self.doc_date.text(),
            'doc_title': self.doc_title.text(),
            'issuing_dept': dept if dept != APP_SETTINGS.DEFAULT_DEPARTMENTS[0] else None,
            'doc_classification': self.doc_classification.text(),
            'legal_paragraph': self.legal_paragraph.toPlainText(),
            'notes': self.notes.toPlainText()
        }
        
        # تحقق إذا كان هناك أي قيمة غير فارغة
        has_any_data = any(
            v is not None and str(v).strip() != '' 
            for v in data.values()
        )
        
        if has_any_data:
            self.attachment_data[self.current_index] = data
        elif self.current_index in self.attachment_data:
            del self.attachment_data[self.current_index]
    
    def go_previous(self):
        """الانتقال للمرفق السابق"""
        if self.current_index > 1:
            self.save_current_data()
            self.load_attachment(self.current_index - 1)
    
    def go_next(self):
        """الانتقال للمرفق التالي"""
        if self.current_index < len(self.scanned_images) - 1:
            self.save_current_data()
            self.load_attachment(self.current_index + 1)
    
    def accept(self):
        """حفظ جميع البيانات عند الإنهاء"""
        self.save_current_data()
        super().accept()
    
    def get_all_data(self):
        """
        الحصول على بيانات جميع المرفقات
        
        Returns:
            dict: قاموس يحتوي على بيانات كل مرفق
        """
        return self.attachment_data
