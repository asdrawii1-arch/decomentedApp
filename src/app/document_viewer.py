"""
نافذة عرض الوثائق والصور
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QPushButton, QSpinBox, QComboBox, QMessageBox,
    QFileDialog, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem,
    QSplitter, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSlot, QTimer
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ui_styles import COLORS


class DocumentViewerWindow(QMainWindow):
    """نافذة عرض الوثائق"""
    
    def __init__(self, document_id, document_data, images_data, parent=None):
        super().__init__(parent)
        self.document_id = document_id
        self.document_data = document_data
        
        # images_data يمكن أن يكون قائمة من القواميس أو قائمة من المسارات (للتوافقية)
        if images_data and isinstance(images_data[0], dict):
            self.images_data = images_data
            self.image_paths = [img['path'] for img in images_data]
        else:
            # التوافقية مع الكود القديم
            self.image_paths = images_data if images_data else []
            self.images_data = [{'path': p, 'notes': None} for p in self.image_paths]
        
        self.current_page = 0
        self.image_manager = None
        
        # نظام Cache للأداء السريع
        self.image_cache = {}  # cache للصور المحملة
        self.scaled_cache = {}  # cache للصور المُحجمة
        self.target_width = 700  # العرض المستهدف للصور
        self._programmatic_update = False  # علامة للتحديث البرمجي
        
        # متغيرات التكبير والتصغير
        self.zoom_factor = 1.0
        self.original_pixmap = None
        
        # معلومات تشخيصية محدودة
        if len(self.image_paths) > 0:
            pass  # تم تحميل الصور بنجاح
        
        self.setWindowTitle(f"عرض الوثيقة - {document_data[1]}")
        self.setGeometry(50, 50, 1400, 900)  # حجم محسن للتصميم الجديد بثلاثة أجزاء
        self.init_ui()
        
        # تحميل الصور مسبقاً لتحسين الأداء
        self.preload_images()

        # افتح نافذة العارض مكبرة لتملأ الشاشة
        try:
            self.showMaximized()
        except Exception:
            # في حالة عدم دعم البيئة، تجاهل الخطأ
            pass
        
        # عرض الصورة الأولى
        if self.image_paths:
            self.display_image(0)
    
    def preload_images(self):
        """تحميل الصور مسبقاً في الخلفية لتحسين الأداء"""
        for i, image_path in enumerate(self.image_paths[:3]):  # تحميل أول 3 صور فقط لتوفير الذاكرة
            if os.path.exists(image_path) and i not in self.image_cache:
                try:
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        self.image_cache[i] = pixmap
                        # تحجيم الصورة وحفظها في الـ cache أيضاً
                        scaled_pixmap = pixmap.scaledToWidth(
                            self.target_width, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.scaled_cache[i] = scaled_pixmap
                except Exception:
                    pass  # تجاهل الأخطاء في التحميل المسبق
    
    def get_cached_image(self, index):
        """الحصول على صورة محجمة من الـ cache أو تحميلها"""
        # تحقق من وجود الصورة المحجمة في الـ cache
        if index in self.scaled_cache:
            return self.scaled_cache[index]
        
        # تحقق من وجود الصورة الأصلية في الـ cache
        if index in self.image_cache:
            pixmap = self.image_cache[index]
        else:
            # تحميل الصورة من القرص
            image_path = self.image_paths[index]
            if not os.path.exists(image_path):
                return None
            
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                return None
            
            # حفظ في الـ cache
            self.image_cache[index] = pixmap
        
        # تحجيم الصورة
        scaled_pixmap = pixmap.scaledToWidth(
            self.target_width, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # حفظ النسخة المحجمة في الـ cache
        self.scaled_cache[index] = scaled_pixmap
        
        # إدارة حجم الـ cache
        self._manage_cache_size()
        
        return scaled_pixmap
    
    def _manage_cache_size(self):
        """إدارة حجم الـ cache لمنع استهلاك الذاكرة المفرط"""
        max_cache_size = 10  # أقصى عدد صور في الـ cache
        
        if len(self.scaled_cache) > max_cache_size:
            # احتفظ بالصور الأقرب للصورة الحالية
            current_index = self.current_page
            keys_to_keep = []
            
            # احتفظ بالصورة الحالية والمجاورة لها
            for i in range(max(0, current_index - 2), min(len(self.image_paths), current_index + 3)):
                if i in self.scaled_cache:
                    keys_to_keep.append(i)
            
            # احذف باقي الصور من الـ cache
            keys_to_remove = [k for k in self.scaled_cache.keys() if k not in keys_to_keep]
            for key in keys_to_remove[:5]:  # احذف 5 صور كحد أقصى في المرة الواحدة
                if key in self.scaled_cache:
                    del self.scaled_cache[key]
                if key in self.image_cache:
                    del self.image_cache[key]
    
    def init_ui(self):
        """إنشاء واجهة المشاهد بتصميم حديث وأنيق"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط الرئيسي أفقي محسن
        main_layout = QHBoxLayout()
        main_layout.setSpacing(5)  # تقليل المسافة
        main_layout.setContentsMargins(5, 5, 5, 5)  # تقليل الهوامش
        
        # الجانب الأيسر - مستطيل معلومات الوثيقة وقائمة الصور
        left_panel = QWidget()
        left_panel.setStyleSheet(
            "QWidget { "
            "background-color: #f8f9fa; "
            "border: 2px solid #3498db; "
            "border-radius: 12px; "
            "margin: 2px; }"
        )
        left_panel.setMaximumWidth(330)  # تقليل العرض قليلاً
        left_panel.setMinimumWidth(300)  # تقليل العرض الأدنى
        
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)  # تقليل المسافة
        left_layout.setContentsMargins(12, 12, 12, 12)  # تقليل الهوامش
        
        # معلومات الوثيقة في الأعلى
        doc_info_title = QLabel('📄 معلومات الوثيقة')
        doc_info_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 8px; "
            "background-color: #2c3e50; color: white; border-radius: 8px; "
            "margin-bottom: 5px; text-align: center;"
        )
        doc_info_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(doc_info_title)
        
        # معلومات الوثيقة التفصيلية
        self.current_image_info = QLabel()
        self.current_image_info.setStyleSheet(
            "QLabel { "
            "background-color: white; color: #000000; padding: 12px; "
            "font-size: 12px; border: 1px solid #bdc3c7; border-radius: 8px; "
            "line-height: 1.4; font-weight: 800; font-family: 'Segoe UI', Arial, sans-serif; }"
        )
        self.current_image_info.setWordWrap(True)
        self.current_image_info.setMinimumHeight(120)
        self.current_image_info.setMaximumHeight(150)
        left_layout.addWidget(self.current_image_info)
        
        # عنوان قائمة الصور
        images_title = QLabel('🖼️ قائمة الصور')
        images_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 8px; "
            "background-color: #2c3e50; color: white; border-radius: 8px; "
            "margin-top: 10px; margin-bottom: 5px;"
        )
        images_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(images_title)
        
        # أزرار التنقل
        nav_container = QWidget()
        nav_container.setStyleSheet(
            "QWidget { background-color: white; border: 1px solid #bdc3c7; border-radius: 8px; padding: 8px; }"
        )
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(8)
        
        # أزرار التنقل الأساسية
        nav_buttons_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton('◀ السابق')
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(len(self.image_paths) > 1)
        self.prev_btn.setStyleSheet(
            "QPushButton { padding: 10px 15px; font-size: 12px; font-weight: bold; "
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9); "
            "color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2980b9, stop:1 #21618c); }"
            "QPushButton:pressed { background: #21618c; }"
            "QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }"
        )
        nav_buttons_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton('التالي ▶')
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(len(self.image_paths) > 1)
        self.next_btn.setStyleSheet(
            "QPushButton { padding: 10px 15px; font-size: 12px; font-weight: bold; "
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9); "
            "color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2980b9, stop:1 #21618c); }"
            "QPushButton:pressed { background: #21618c; }"
            "QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }"
        )
        nav_buttons_layout.addWidget(self.next_btn)
        
        nav_layout.addLayout(nav_buttons_layout)
        
        # معلومات الصفحة
        page_info_layout = QHBoxLayout()
        page_label = QLabel('الصورة:')
        page_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(len(self.image_paths) if self.image_paths else 1)
        self.page_spin.setValue(1)
        self.page_spin.valueChanged.connect(self.go_to_page)
        self.page_spin.setStyleSheet(
            "QSpinBox { padding: 6px; border: 2px solid #3498db; border-radius: 4px; "
            "font-weight: bold; background-color: white; font-size: 11px; }"
        )
        
        page_count_label = QLabel(f'من {len(self.image_paths)}')
        page_count_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        page_info_layout.addWidget(page_label)
        page_info_layout.addWidget(self.page_spin)
        page_info_layout.addWidget(page_count_label)
        page_info_layout.addStretch()
        
        nav_layout.addLayout(page_info_layout)
        nav_container.setLayout(nav_layout)
        left_layout.addWidget(nav_container)
        
        # قائمة الصور
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        # إشارة للتنقل السريع
        self.image_list.itemClicked.connect(self.on_image_clicked)
        self.image_list.itemSelectionChanged.connect(self.on_image_selected)
        
        # تصميم أنيق لقائمة الصور
        self.image_list.setStyleSheet(
            "QListWidget { "
            "border: 1px solid #bdc3c7; border-radius: 8px; "
            "background-color: white; padding: 5px; }"
            "QListWidget::item { "
            "padding: 10px; margin: 3px; border-radius: 6px; "
            "background-color: #ecf0f1; border: 1px solid #d5dbdb; }"
            "QListWidget::item:selected { "
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9); "
            "color: white; border-color: #2980b9; }"
            "QListWidget::item:hover { "
            "background-color: #d6eaf8; border-color: #3498db; }"
        )
        self.image_list.setMinimumHeight(200)
        
        # إضافة الصور إلى القائمة
        for i, image_path in enumerate(self.image_paths):
            item_text = f"🖼️ صورة {i+1}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setToolTip(f"اضغط لعرض الصورة\nالمسار: {image_path}")
            self.image_list.addItem(item)
        
        left_layout.addWidget(self.image_list)
        
        # أزرار الطباعة والتصدير
        actions_layout = QHBoxLayout()
        
        print_btn = QPushButton('🖨️ طباعة')
        print_btn.clicked.connect(self.print_images)
        print_btn.setStyleSheet(
            "QPushButton { padding: 8px 12px; font-size: 11px; font-weight: bold; "
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #27ae60, stop:1 #229954); "
            "color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #229954, stop:1 #1e8449); }"
        )
        actions_layout.addWidget(print_btn)
        
        export_btn = QPushButton('💾 تصدير')
        export_btn.clicked.connect(self.export_images)
        export_btn.setStyleSheet(
            "QPushButton { padding: 8px 12px; font-size: 11px; font-weight: bold; "
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e67e22, stop:1 #d35400); "
            "color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d35400, stop:1 #ba4a00); }"
        )
        actions_layout.addWidget(export_btn)
        
        left_layout.addLayout(actions_layout)
        left_layout.addStretch()  # دفع المحتوى للأعلى
        
        left_panel.setLayout(left_layout)
        
        # المنطقة الوسطى - عرض الصورة الرئيسي
        center_panel = QWidget()
        center_panel.setStyleSheet(
            "QWidget { "
            "background-color: #ffffff; "
            "border: 2px solid #3498db; "
            "border-radius: 12px; "
            "margin: 2px; }"
        )
        center_panel.setMinimumWidth(500)  # مساحة أكبر لعرض الصور
        
        center_layout = QVBoxLayout()
        center_layout.setSpacing(3)
        center_layout.setContentsMargins(8, 8, 8, 8)
        
        # (عنوان منطقة العرض تمت إزالته للاستفادة من المساحة الرأسية)
        
        # منطقة عرض الصورة مع تحسين المساحة الطولية
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            f"background-color: {COLORS.BACKGROUND_WHITE}; "
            "border: 1px solid #bdc3c7; border-radius: 6px;"
        )
        self.image_label.setScaledContents(False)
        
        if not self.image_paths:
            self.image_label.setText("❌ لا توجد صور متاحة")
            self.image_label.setStyleSheet(
                f"background-color: {COLORS.BACKGROUND_WHITE}; "
                "border: 2px dashed #e74c3c; border-radius: 6px; "
                "color: #e74c3c; font-size: 16px; font-weight: bold;"
            )
        
        # منطقة التمرير مع تحكم محسن
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }"
            "QScrollBar:vertical { width: 12px; border-radius: 6px; background-color: #f1f2f6; }"
            "QScrollBar::handle:vertical { background-color: #3498db; border-radius: 6px; min-height: 20px; }"
            "QScrollBar::handle:vertical:hover { background-color: #2980b9; }"
            "QScrollBar:horizontal { height: 12px; border-radius: 6px; background-color: #f1f2f6; }"
            "QScrollBar::handle:horizontal { background-color: #3498db; border-radius: 6px; min-width: 20px; }"
            "QScrollBar::handle:horizontal:hover { background-color: #2980b9; }"
        )
        
        center_layout.addWidget(self.scroll_area)
        center_panel.setLayout(center_layout)
        
        # الجانب الأيمن - أدوات التحكم في التكبير عمودياً
        right_panel = QWidget()
        right_panel.setStyleSheet(
            "QWidget { "
            "background-color: #f8f9fa; "
            "border: 2px solid #3498db; "
            "border-radius: 12px; "
            "margin: 2px; }"
        )
        right_panel.setFixedWidth(120)  # عرض ثابت للوحة التحكم
        
        right_layout = QVBoxLayout()
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # عنوان لوحة التحكم محسن
        control_title = QLabel('🎛️ العرض')
        control_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 6px; "
            "background-color: #2c3e50; color: white; border-radius: 6px; "
            "text-align: center;"
        )
        control_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(control_title)
        
        # مؤشر نسبة التكبير
        self.zoom_label = QLabel('100%')
        self.zoom_label.setStyleSheet(
            "font-weight: bold; color: #2c3e50; padding: 8px; "
            "background-color: white; border: 1px solid #bdc3c7; border-radius: 4px; "
            "text-align: center; font-size: 12px;"
        )
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.zoom_label)
        
        # زر التكبير
        zoom_in_btn = QPushButton('🔍+')
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_in_btn.setStyleSheet(
            "QPushButton { padding: 12px; font-size: 14px; font-weight: bold; "
            "background-color: #27ae60; color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background-color: #229954; }"
            "QPushButton:pressed { background-color: #1e8449; }"
        )
        zoom_in_btn.setToolTip('تكبير الصورة')
        zoom_in_btn.setMinimumHeight(45)
        right_layout.addWidget(zoom_in_btn)
        
        # زر التصغير
        zoom_out_btn = QPushButton('🔍-')
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_out_btn.setStyleSheet(
            "QPushButton { padding: 12px; font-size: 14px; font-weight: bold; "
            "background-color: #e74c3c; color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background-color: #c0392b; }"
            "QPushButton:pressed { background-color: #a93226; }"
        )
        zoom_out_btn.setToolTip('تصغير الصورة')
        zoom_out_btn.setMinimumHeight(45)
        right_layout.addWidget(zoom_out_btn)
        
        # فاصل بصري
        separator = QLabel()
        separator.setStyleSheet("background-color: #bdc3c7; margin: 5px 20px;")
        separator.setFixedHeight(1)
        right_layout.addWidget(separator)
        
        # زر ملء النافذة مع اختصار
        fit_window_btn = QPushButton('📐\nملء')
        fit_window_btn.clicked.connect(self.fit_to_window)
        fit_window_btn.setStyleSheet(
            "QPushButton { padding: 8px; font-size: 12px; font-weight: bold; "
            "background-color: #3498db; color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background-color: #2980b9; }"
            "QPushButton:pressed { background-color: #21618c; }"
        )
        fit_window_btn.setToolTip('ملء النافذة')
        fit_window_btn.setMinimumHeight(40)
        right_layout.addWidget(fit_window_btn)
        
        # زر الحجم الأصلي مع اختصار
        actual_size_btn = QPushButton('📏\n100%')
        actual_size_btn.clicked.connect(self.actual_size)
        actual_size_btn.setStyleSheet(
            "QPushButton { padding: 8px; font-size: 12px; font-weight: bold; "
            "background-color: #9b59b6; color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background-color: #8e44ad; }"
            "QPushButton:pressed { background-color: #7d3c98; }"
        )
        actual_size_btn.setToolTip('الحجم الأصلي 100%')
        actual_size_btn.setMinimumHeight(40)
        right_layout.addWidget(actual_size_btn)
        
        right_layout.addStretch()  # دفع الأزرار للأعلى
        right_panel.setLayout(right_layout)
        
        # توزيع محسن للمساحة - اليسار 25%، الوسط 65%، اليمين 10%
        main_layout.addWidget(left_panel, 25)   # 25% للمعلومات والقوائم
        main_layout.addWidget(center_panel, 65) # 65% لعرض الصورة
        main_layout.addWidget(right_panel, 10)  # 10% لأدوات التحكم
        
        central_widget.setLayout(main_layout)
        
        # عرض الصورة الأولى مع تأخير قصير لضمان حساب المساحة بشكل صحيح
        if self.image_paths:
            # استخدام QTimer لضمان رسم النافذة أولاً
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self.display_image(0))
    
    def display_image(self, index):
        """عرض الصورة في الموضع المحدد مع دعم التكبير والتصغير"""
        if 0 <= index < len(self.image_paths):
            self.current_page = index
            image_path = self.image_paths[index]
            
            # تحميل الصورة الأصلية
            if not os.path.exists(image_path):
                self.image_label.setText(f"❌ الصورة غير موجودة:\n{os.path.basename(image_path)}")
                self.image_label.setStyleSheet(
                    f"background-color: {COLORS.BACKGROUND_WHITE}; "
                    "border: 2px dashed #e74c3c; border-radius: 8px; "
                    "color: #e74c3c; font-size: 16px; font-weight: bold;"
                )
                return
            
            # تحميل الصورة الأصلية
            self.original_pixmap = QPixmap(image_path)
            
            if self.original_pixmap.isNull():
                self.image_label.setText(f"❌ فشل تحميل الصورة:\n{os.path.basename(image_path)}")
                self.image_label.setStyleSheet(
                    f"background-color: {COLORS.BACKGROUND_WHITE}; "
                    "border: 2px dashed #e74c3c; border-radius: 8px; "
                    "color: #e74c3c; font-size: 16px; font-weight: bold;"
                )
                return
            
            # إعادة تعيين التكبير وعرض الصورة بحجم مناسب for the new longitudinal design
            self.zoom_factor = 1.0
            
            # حساب الحجم المناسب للعرض الأولي مع الاستفادة من المساحة الطولية الكبيرة
            available_size = self.scroll_area.viewport().size()
            if available_size.width() > 200 and available_size.height() > 200:
                # حساب نسبة محسنة للتكبير للاستفادة من التصميم الطولي
                scale_x = (available_size.width() - 30) / self.original_pixmap.width()
                scale_y = (available_size.height() - 80) / self.original_pixmap.height()
                initial_scale = min(scale_x, scale_y, 1.5)  # السماح بالتكبير حتى 150% للاستفادة من المساحة
                
                if initial_scale > 0.2:  # تجنب التصغير المفرط
                    self.zoom_factor = initial_scale
            
            self.apply_zoom()
            
            # تحديث عناصر التحكم
            self._update_controls(index)
            
            # تحديث معلومات الصورة
            self._update_current_image_info(index)
            
            # تحديث مؤشر التكبير
            self.update_zoom_label()
            
            # إصلاح تصميم الصورة
            self.image_label.setStyleSheet(
                "background-color: white; "
                "border: 1px solid #bdc3c7; border-radius: 4px;"
            )
            
            # تحميل الصور المجاورة في الخلفية
            self._preload_adjacent_images(index)
    
    def _update_controls(self, index):
        """تحديث عناصر التحكم بالصفحة"""
        # تحديث شريط التمرير
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(index + 1)
        self.page_spin.blockSignals(False)
        
        # تحديث اختيار الصورة في القائمة
        self._programmatic_update = True
        self.image_list.blockSignals(True)
        self.image_list.clearSelection()
        if self.image_list.count() > index:
            self.image_list.item(index).setSelected(True)
            self.image_list.setCurrentRow(index)
        self.image_list.blockSignals(False)
        self._programmatic_update = False
        
        # تحديث أزرار التنقل
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.image_paths) - 1)
    
    def zoom_in(self):
        """تكبير الصورة مع حد أقصى محسن للتصميم الطولي"""
        if self.original_pixmap:
            self.zoom_factor = min(self.zoom_factor * 1.25, 8.0)  # حد أقصى 800% للاستفادة من المساحة الكبيرة
            self.apply_zoom()
    
    def zoom_out(self):
        """تصغير الصورة مع حد أدنى محسن"""
        if self.original_pixmap:
            self.zoom_factor = max(self.zoom_factor / 1.25, 0.05)  # حد أدنى 5%
            self.apply_zoom()
    
    def fit_to_window(self):
        """ملء النافذة بالصورة مع حساب أفضل للمساحة المتاحة - محسن للتصميم الطولي"""
        if self.original_pixmap:
            # حساب المساحة المتاحة الفعلية في المنطقة الوسطى
            available_size = self.scroll_area.viewport().size()
            
            # طرح مساحة العنوان والهوامش المحسنة للتصميم الجديد
            toolbar_height = 45  # ارتفاع شريط العنوان المحسن
            margins = 20  # هوامش أقل للاستفادة القصوى من المساحة
            
            available_size.setWidth(available_size.width() - margins)
            available_size.setHeight(available_size.height() - toolbar_height - margins)
            
            # التأكد من أن المساحة المتاحة صالحة
            if available_size.width() <= 0 or available_size.height() <= 0:
                # استخدام قيم افتراضية محسنة للتصميم الطولي
                available_size.setWidth(800)
                available_size.setHeight(600)
            
            # حساب نسبة التكبير للاستفادة من المساحة الطولية
            scale_x = available_size.width() / self.original_pixmap.width()
            scale_y = available_size.height() / self.original_pixmap.height()
            self.zoom_factor = min(scale_x, scale_y, 3.0)  # حد أقصى 300% للاستفادة من المساحة الكبيرة
            
            self.apply_zoom()
    
    def actual_size(self):
        """الحجم الأصلي 100%"""
        if self.original_pixmap:
            self.zoom_factor = 1.0
            self.apply_zoom()
    
    def apply_zoom(self):
        """تطبيق التكبير على الصورة"""
        if self.original_pixmap:
            # حساب الحجم الجديد
            new_size = self.original_pixmap.size() * self.zoom_factor
            
            # تطبيق التكبير مع الحفاظ على الجودة
            scaled_pixmap = self.original_pixmap.scaled(
                new_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            # عرض الصورة
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
            
            # تحديث مؤشر التكبير
            self.update_zoom_label()
    
    def update_zoom_label(self):
        """تحديث مؤشر نسبة التكبير"""
        if hasattr(self, 'zoom_label'):
            percentage = int(self.zoom_factor * 100)
            self.zoom_label.setText(f'{percentage}%')
    
    def _preload_adjacent_images(self, current_index):
        """تحميل الصور المجاورة في الخلفية لتحسين التنقل"""
        # تحميل الصورة التالية
        if current_index + 1 < len(self.image_paths) and (current_index + 1) not in self.scaled_cache:
            try:
                self.get_cached_image(current_index + 1)
            except Exception:
                pass
        
        # تحميل الصورة السابقة
        if current_index - 1 >= 0 and (current_index - 1) not in self.scaled_cache:
            try:
                self.get_cached_image(current_index - 1)
            except Exception:
                pass
    
    def _update_current_image_info(self, index):
        """تحديث معلومات الصورة/المرفق الحالي مع عرض معلومات الوثيقة"""
        total_pages = len(self.image_paths)
        
        # استخراج بيانات الوثيقة الرئيسية
        doc_name = ""
        doc_date = ""
        doc_title = ""
        issuing_dept = ""
        doc_classification = ""
        
        if self.document_data and len(self.document_data) >= 5:
            doc_name = self.document_data[1] if len(self.document_data) > 1 else ""
            doc_date = self.document_data[2] if len(self.document_data) > 2 else ""
            doc_title = self.document_data[3] if len(self.document_data) > 3 else ""
            issuing_dept = self.document_data[4] if len(self.document_data) > 4 else ""
            doc_classification = self.document_data[5] if len(self.document_data) > 5 else ""
        
        # إنشاء معلومات الوثيقة الأساسية
        doc_info_html = ""
        if doc_name or doc_date or doc_title or issuing_dept:
            doc_info_html = f"""
            <div style='background: linear-gradient(135deg, #3498db, #2980b9); padding: 6px; border-radius: 6px; margin-bottom: 6px;'>
                <span style='color: #fff; font-size: 12px; font-weight: bold;'>📋 معلومات الوثيقة</span><br>
                <span style='color: #000000; font-size: 12px; font-weight: 700;'>
                🔢 <b>{doc_name or 'غير محدد'}</b> • 📅 {doc_date or 'غير محدد'}<br>
                📝 {doc_title or 'غير محدد'} • 🏢 {issuing_dept or 'غير محدد'}
                </span>
            </div>
            """
        
        if index < len(self.images_data):
            img_data = self.images_data[index]
            notes = img_data.get('notes', '')
            
            if index == 0:
                type_icon = "📄"
                type_text = "الوثيقة الرئيسية"
            else:
                type_icon = "📎"
                type_text = f"المرفق {index}"
            
            header = f"<span style='font-size: 13px; color: #3498db;'>{type_icon} <b>{type_text}</b></span>"
            page_info = f"<span style='color: #bdc3c7; font-size: 11px;'>الصفحة {index + 1} من {total_pages}</span>"
            
            if notes:
                # تحليل الملاحظات واستبعاد الحقول المتطابقة مع الوثيقة الرئيسية
                notes_parts = notes.split(' | ')
                notes_html = ""
                for part in notes_parts:
                    # استخراج القيمة من الحقل (مثل "رقم: 65" -> "65")
                    part_value = part.split(':', 1)[1].strip() if ':' in part else part.strip()
                    
                    # تحقق مما إذا كانت القيمة مطابقة لبيانات الوثيقة الرئيسية
                    is_duplicate = False
                    if part.startswith('رقم:'):
                        # مقارنة مع اسم الوثيقة (قد يحتوي على "رقم في تاريخ")
                        is_duplicate = (part_value == doc_name or 
                                       part_value in doc_name or 
                                       doc_name.startswith(part_value))
                    elif part.startswith('تاريخ:'):
                        is_duplicate = (part_value == doc_date or part_value in doc_date)
                    elif part.startswith('مضمون:'):
                        is_duplicate = (part_value == doc_title)
                    elif part.startswith('جهة:'):
                        is_duplicate = (part_value == issuing_dept)
                    elif part.startswith('تصنيف:'):
                        is_duplicate = (part_value == doc_classification)
                    
                    # تخطي الحقول المتطابقة
                    if is_duplicate:
                        continue
                    
                    # عرض الحقول غير المتطابقة فقط
                    if part.startswith('رقم:'):
                        notes_html += f"<br><span style='font-size: 11px; color: #e74c3c;'>🔢 {part}</span>"
                    elif part.startswith('تاريخ:'):
                        notes_html += f"<br><span style='font-size: 11px; color: #e67e22;'>📅 {part}</span>"
                    elif part.startswith('مضمون:'):
                        notes_html += f"<br><span style='font-size: 11px; color: #f39c12;'>📝 {part}</span>"
                    elif part.startswith('جهة:'):
                        notes_html += f"<br><span style='font-size: 11px; color: #27ae60;'>🏢 {part}</span>"
                    elif part.startswith('تصنيف:'):
                        notes_html += f"<br><span style='font-size: 11px; color: #8e44ad;'>🏷️ {part}</span>"
                    elif part.startswith('ملاحظات:'):
                        notes_html += f"<br><span style='font-size: 11px; color: #16a085;'>💬 {part}</span>"
                    else:
                        notes_html += f"<br><span style='font-size: 11px; color: #95a5a6;'>• {part}</span>"
                
                if notes_html:
                    info_text = f"{doc_info_html}{header} &nbsp;&nbsp; {page_info}{notes_html}"
                else:
                    # جميع الحقول متطابقة - لا تعرض قسم الملاحظات
                    info_text = f"{doc_info_html}{header} &nbsp;&nbsp; {page_info}"
            else:
                info_text = f"{doc_info_html}{header} &nbsp;&nbsp; {page_info}"
            
            self.current_image_info.setText(info_text)
        else:
            self.current_image_info.setText(f"{doc_info_html}<b style='color: #3498db;'>📄 الصورة {index + 1} من {total_pages}</b>")
    
    def prev_page(self):
        """الصفحة السابقة"""
        if self.current_page > 0:
            self.display_image(self.current_page - 1)
    
    def next_page(self):
        """الصفحة التالية"""
        if self.current_page < len(self.image_paths) - 1:
            self.display_image(self.current_page + 1)
    
    def go_to_page(self, page_num):
        """الذهاب إلى صفحة محددة (محاكاة on_page_changed)"""
        self.display_image(page_num - 1)
    
    def print_images(self):
        """طباعة الصور"""
        if not self.image_paths:
            QMessageBox.warning(self, 'تنبيه', 'لا توجد صور للطباعة')
            return
        
        # إنشاء نافذة خيارات الطباعة
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        
        if print_dialog.exec() == QDialog.DialogCode.Accepted:
            # الطباعة
            self.print_document(printer)
    
    def print_document(self, printer):
        """طباعة الوثيقة على الطابعة"""
        from PyQt6.QtGui import QPainter
        
        try:
            painter = QPainter()
            if not painter.begin(printer):
                QMessageBox.critical(self, 'خطأ', 'فشل بدء الطباعة')
                return
            # احصل على مستطيل الصفحة بوحدات الجهاز؛ تحقّق من القيم وحسّن التحجيم
            try:
                page_rect = printer.pageRect()  # الوحدة الافتراضية تعمل عادةً بشكل جيد
            except Exception:
                page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)

            print_count = 0

            for i, image_path in enumerate(self.image_paths):
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    continue

                # احسب حجم الهدف مع الحفاظ على نسبة العرض للارتفاع
                from PyQt6.QtCore import QSize as _QSize
                page_size = _QSize(int(page_rect.width()), int(page_rect.height()))
                target_size = pixmap.size().scaled(
                    page_size,
                    Qt.AspectRatioMode.KeepAspectRatio
                )

                # في بعض الطابعات القيم قد تكون صفرية - تعامل مع هذه الحالة
                if target_size.width() <= 0 or target_size.height() <= 0:
                    # حاول استخدام أبعاد الصورة الأصلية كاحتياط
                    target_size = pixmap.size()
                    if target_size.width() <= 0 or target_size.height() <= 0:
                        continue

                # محاذاة الصورة في منتصف الصفحة
                x = int((page_rect.width() - target_size.width()) / 2)
                y = int((page_rect.height() - target_size.height()) / 2)
                target_rect = page_rect.toRect()
                target_rect.setX(x)
                target_rect.setY(y)
                target_rect.setWidth(target_size.width())
                target_rect.setHeight(target_size.height())

                # ارسم الصورة محجمة إلى الحجم المحسوب
                painter.drawPixmap(
                    target_rect,
                    pixmap
                )

                print_count += 1

                if i < len(self.image_paths) - 1:
                    printer.newPage()
            
            painter.end()
            
            QMessageBox.information(
                self, 'نجح',
                f'تم طباعة {print_count} صورة بنجاح'
            )
            print(f"[PRINT] تم طباعة {print_count} صورة من {len(self.image_paths)}")
            
        except Exception as e:
            QMessageBox.critical(self, 'خطأ في الطباعة', f'حدث خطأ: {str(e)}')
            print(f"[ERROR] خطأ في الطباعة: {e}")
    
    def export_images(self):
        """استرجاع واستخراج الصور - صورة واحدة أو ملف كامل"""
        if not self.image_paths:
            QMessageBox.warning(self, 'تنبيه', 'لا توجد صور للاستخراج')
            return
        
        # إنشاء نافذة حوار لاختيار نوع الاستخراج
        dialog = QDialog(self)
        dialog.setWindowTitle('خيارات الاستخراج')
        dialog.setGeometry(150, 150, 400, 200)
        
        layout = QVBoxLayout()
        
        # تسميات توضيحية
        label = QLabel('اختر طريقة الاستخراج:')
        layout.addWidget(label)
        
        # الأزرار
        button_layout = QVBoxLayout()
        
        single_btn = QPushButton('📄 استخراج صورة واحدة (الصورة الحالية)')
        single_btn.clicked.connect(lambda: self.export_single_image(dialog))
        button_layout.addWidget(single_btn)
        
        all_btn = QPushButton('📁 استخراج كل الصور (مجلد منفصل)')
        all_btn.clicked.connect(lambda: self.export_all_images(dialog))
        button_layout.addWidget(all_btn)
        
        zip_btn = QPushButton('🗜️ استخراج كملف ZIP')
        zip_btn.clicked.connect(lambda: self.export_as_zip(dialog))
        button_layout.addWidget(zip_btn)
        
        pdf_btn = QPushButton('📕 استخراج كملف PDF')
        pdf_btn.clicked.connect(lambda: self.export_as_pdf(dialog))
        button_layout.addWidget(pdf_btn)
        
        # زر الإغلاق
        cancel_btn = QPushButton('إلغاء')
        cancel_btn.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
    
    def export_single_image(self, parent_dialog):
        """استخراج صورة واحدة فقط"""
        parent_dialog.close()
        
        # فتح نافذة حفظ الملف
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'حفظ الصورة الحالية',
            f'صورة_{self.current_page + 1}.jpg',
            'صور JPEG (*.jpg);;صور PNG (*.png);;كل الملفات (*)'
        )
        
        if file_path:
            try:
                import shutil
                source_path = self.image_paths[self.current_page]
                shutil.copy2(source_path, file_path)
                
                QMessageBox.information(
                    self, 'نجح',
                    f'تم حفظ الصورة بنجاح\n{file_path}'
                )
                print(f"[EXPORT] تم حفظ الصورة: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'فشل الحفظ: {str(e)}')
    
    def export_all_images(self, parent_dialog):
        """استخراج كل الصور في مجلد"""
        parent_dialog.close()
        
        output_dir = QFileDialog.getExistingDirectory(
            self,
            'اختر مجلد الحفظ'
        )
        
        if output_dir:
            try:
                from pathlib import Path
                import shutil
                
                output_path = Path(output_dir)
                count = 0
                
                for i, image_path in enumerate(self.image_paths):
                    dest = output_path / f'صورة_{i+1:04d}.jpg'
                    shutil.copy2(image_path, dest)
                    count += 1
                
                QMessageBox.information(
                    self, 'نجح',
                    f'تم استخراج {count} صورة بنجاح'
                )
                print(f"[EXPORT] تم استخراج {count} صورة إلى: {output_dir}")
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'فشل الاستخراج: {str(e)}')
    
    def export_as_zip(self, parent_dialog):
        """استخراج كملف ZIP"""
        parent_dialog.close()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'حفظ كملف ZIP',
            f'{self.document_data[1]}.zip',
            'ملفات ZIP (*.zip)'
        )
        
        if file_path:
            try:
                import zipfile
                from pathlib import Path
                
                with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for i, image_path in enumerate(self.image_paths):
                        zipf.write(
                            image_path,
                            arcname=f'صورة_{i+1:04d}.jpg'
                        )
                
                QMessageBox.information(
                    self, 'نجح',
                    f'تم إنشاء ملف ZIP بنجاح\n{file_path}\nعدد الصور: {len(self.image_paths)}'
                )
                print(f"[EXPORT] تم إنشاء ZIP: {file_path} بـ {len(self.image_paths)} صورة")
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'فشل إنشاء ZIP: {str(e)}')
    
    def export_as_pdf(self, parent_dialog):
        """استخراج كملف PDF"""
        parent_dialog.close()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'حفظ كملف PDF',
            f'{self.document_data[1]}.pdf',
            'ملفات PDF (*.pdf)'
        )
        
        if file_path:
            try:
                from PIL import Image
                
                images = []
                
                # تحميل جميع الصور
                for image_path in self.image_paths:
                    img = Image.open(image_path).convert('RGB')
                    images.append(img)
                
                # حفظ كـ PDF
                if images:
                    images[0].save(
                        file_path,
                        save_all=True,
                        append_images=images[1:],
                        duration=100,
                        loop=0
                    )
                
                QMessageBox.information(
                    self, 'نجح',
                    f'تم إنشاء ملف PDF بنجاح\n{file_path}\nعدد الصفحات: {len(images)}'
                )
                print(f"[EXPORT] تم إنشاء PDF: {file_path} بـ {len(images)} صفحة")
            except ImportError:
                QMessageBox.warning(
                    self, 'تنبيه',
                    'مكتبة Pillow غير مثبتة\nثبّتها باستخدام: pip install pillow'
                )
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'فشل إنشاء PDF: {str(e)}')

    def on_image_clicked(self, item):
        """عند النقر على صورة من القائمة - للتنقل السريع"""
        if item:
            index = self.image_list.row(item)
            # إلغاء كل التحديدات الأخرى وتحديد هذا العنصر فقط
            self.image_list.clearSelection()
            item.setSelected(True)
            # عرض الصورة فوراً
            self.display_image(index)
    
    def on_image_selected(self):
        """عند اختيار صورة من القائمة - للوظائف الأخرى مثل الحذف والتصدير"""
        # التحديث الأساسي فقط، التنقل الأساسي يتم عبر on_image_clicked
        # هذه الدالة تبقى فعالة للوظائف الأخرى مثل الحذف والتصدير
        if not self._programmatic_update:
            selected_items = self.image_list.selectedItems()
            if selected_items:
                # إذا لم يكن التحديث برمجياً، يمكن عرض الصورة أيضاً كاحتياط
                index = self.image_list.row(selected_items[0])
                self.display_image(index)
    
    def resizeEvent(self, event):
        """استجابة لتغيير حجم النافذة لإعادة تحجيم الصورة بما يناسب المساحة الجديدة"""
        super().resizeEvent(event)
        
        # إعادة تطبيق الزوم إذا كانت هناك صورة معروضة حالياً
        if hasattr(self, 'original_pixmap') and self.original_pixmap:
            # التحقق من وضع العرض الحالي ومحاولة المحافظة عليه
            if hasattr(self, 'zoom_factor') and self.zoom_factor > 0:
                # إذا كانت الصورة في وضع "ملء النافذة" (نسبة صغيرة)، أعد حسابها
                if self.zoom_factor < 1.0:
                    # إعادة حساب الملء للنافذة الجديدة
                    self.fit_to_window()
                else:
                    # الحفاظ على الزوم الحالي
                    self.apply_zoom()
    
    def cleanup_cache(self):
        """تنظيف الـ cache لتوفير الذاكرة"""
        self.image_cache.clear()
        self.scaled_cache.clear()
    
    def closeEvent(self, event):
        """عند إغلاق النافذة"""
        self.cleanup_cache()
        super().closeEvent(event)