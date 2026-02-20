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
    QSplitter
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSlot
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
        
        # معلومات تشخيصية محدودة
        if len(self.image_paths) > 0:
            pass  # تم تحميل الصور بنجاح
        
        self.setWindowTitle(f"عرض الوثيقة - {document_data[1]}")
        self.setGeometry(100, 100, 900, 700)
        self.init_ui()
        
        # تحميل الصور مسبقاً لتحسين الأداء
        self.preload_images()
        
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
        
        # التخطيط الرئيسي أفقي
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # الجانب الأيسر - مستطيل معلومات الوثيقة وقائمة الصور
        left_panel = QWidget()
        left_panel.setStyleSheet(
            "QWidget { "
            "background-color: #f8f9fa; "
            "border: 2px solid #3498db; "
            "border-radius: 12px; "
            "margin: 5px; }"
        )
        left_panel.setMaximumWidth(350)
        left_panel.setMinimumWidth(320)
        
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(15, 15, 15, 15)
        
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
            "background-color: white; color: #2c3e50; padding: 12px; "
            "font-size: 11px; border: 1px solid #bdc3c7; border-radius: 8px; "
            "line-height: 1.4; }"
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
        main_layout.addWidget(left_panel)
        
        # الجانب الأيمن - عرض الصورة الرئيسي
        right_panel = QWidget()
        right_panel.setStyleSheet(
            "QWidget { "
            "background-color: #ffffff; "
            "border: 2px solid #3498db; "
            "border-radius: 12px; "
            "margin: 5px; }"
        )
        
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        # عنوان منطقة العرض
        viewer_title = QLabel('📸 عرض الوثيقة')
        viewer_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 12px; "
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9); "
            "color: white; border-radius: 8px; text-align: center;"
        )
        viewer_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(viewer_title)
        
        # منطقة عرض الصورة
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            f"background-color: {COLORS.BACKGROUND_WHITE}; "
            "border: 2px dashed #bdc3c7; border-radius: 8px; "
            "min-height: 400px;"
        )
        
        if not self.image_paths:
            self.image_label.setText("❌ لا توجد صور متاحة")
            self.image_label.setStyleSheet(
                f"background-color: {COLORS.BACKGROUND_WHITE}; "
                "border: 2px dashed #e74c3c; border-radius: 8px; "
                "color: #e74c3c; font-size: 16px; font-weight: bold;"
            )
        
        # تضمين الصورة في منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }"
            "QScrollBar:vertical { width: 12px; border-radius: 6px; background-color: #f1f2f6; }"
            "QScrollBar::handle:vertical { background-color: #3498db; border-radius: 6px; }"
            "QScrollBar::handle:vertical:hover { background-color: #2980b9; }"
        )
        
        right_layout.addWidget(scroll_area)
        right_panel.setLayout(right_layout)
        
        # إضافة الألواح للتخطيط الرئيسي (اليسار يأخذ مساحة ثابتة، اليمين يأخذ الباقي)
        main_layout.addWidget(left_panel, 0)  # مساحة ثابتة
        main_layout.addWidget(right_panel, 1)  # مساحة مرنة
        
        central_widget.setLayout(main_layout)
        
        # عرض الصورة الأولى
        if self.image_paths:
            self.display_image(0)
    
    def display_image(self, index):
        """عرض الصورة في الموضع المحدد بأداء محسن"""
        if 0 <= index < len(self.image_paths):
            self.current_page = index
            
            # استخدام الـ cache للحصول على الصورة المحجمة
            scaled_pixmap = self.get_cached_image(index)
            
            if scaled_pixmap is None:
                # عرض رسالة خطأ إذا فشل تحميل الصورة
                image_path = self.image_paths[index]
                if not os.path.exists(image_path):
                    self.image_label.setText(f"❌ الصورة غير موجودة:\n{image_path}")
                else:
                    self.image_label.setText(f"❌ فشل تحميل الصورة:\n{image_path}")
                return
            
            # عرض الصورة المحجمة
            self.image_label.setPixmap(scaled_pixmap)
            
            # تحديث شريط التمرير بسرعة
            self.page_spin.blockSignals(True)
            self.page_spin.setValue(index + 1)
            self.page_spin.blockSignals(False)
            
            # تحديث اختيار الصورة في القائمة بسرعة (منع التداخل)
            self._programmatic_update = True
            self.image_list.blockSignals(True)
            self.image_list.clearSelection()
            if self.image_list.count() > index:
                self.image_list.item(index).setSelected(True)
                self.image_list.setCurrentRow(index)
            self.image_list.blockSignals(False)
            self._programmatic_update = False
            
            # تحديث معلومات الصورة
            self._update_current_image_info(index)
            
            # تحميل الصورة التالية والسابقة في الخلفية
            self._preload_adjacent_images(index)
    
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
        
        # إنشاء معلومات الوثيقة الأساسية بتصميم محسن ومضغوط
        doc_info_html = ""
        if self.document_data and len(self.document_data) >= 5:
            doc_name = self.document_data[1] if len(self.document_data) > 1 else "غير محدد"
            doc_date = self.document_data[2] if len(self.document_data) > 2 else "غير محدد"  
            doc_title = self.document_data[3] if len(self.document_data) > 3 else "غير محدد"
            issuing_dept = self.document_data[4] if len(self.document_data) > 4 else "غير محدد"
            
            doc_info_html = f"""
            <div style='background: linear-gradient(135deg, #3498db, #2980b9); padding: 6px; border-radius: 6px; margin-bottom: 6px;'>
                <span style='color: #fff; font-size: 13px; font-weight: bold;'>📋 معلومات الوثيقة</span><br>
                <span style='color: #ecf0f1; font-size: 11px;'>
                🔢 <b>{doc_name}</b> • 📅 {doc_date}<br>
                📝 {doc_title} • 🏢 {issuing_dept}
                </span>
            </div>
            """
        
        if index < len(self.images_data):
            img_data = self.images_data[index]
            notes = img_data.get('notes', '')
            
            if index == 0:
                # الصورة الأولى = الوثيقة الرئيسية
                type_icon = "📄"
                type_text = "الوثيقة الرئيسية"
            else:
                # المرفقات
                type_icon = "📎"
                type_text = f"المرفق {index}"
            
            # بناء النص بتنسيق أنيق ومضغوط
            header = f"<span style='font-size: 13px; color: #3498db;'>{type_icon} <b>{type_text}</b></span>"
            page_info = f"<span style='color: #bdc3c7; font-size: 11px;'>الصفحة {index + 1} من {total_pages}</span>"
            
            if notes:
                # تحويل الملاحظات لتنسيق أفضل مع أيقونات مضغوطة
                notes_parts = notes.split(' | ')
                notes_html = ""
                for part in notes_parts:
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
                
                info_text = f"{doc_info_html}{header} &nbsp;&nbsp; {page_info}{notes_html}"
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
            
            # حجم الصفحة بالبكسل
            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            print_count = 0
            
            for i, image_path in enumerate(self.image_paths):
                # تحميل الصورة
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    continue
                
                # رسم الصورة على الصفحة
                painter.drawPixmap(
                    page_rect.toRect(),
                    pixmap.scaled(
                        page_rect.width(),
                        page_rect.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
                
                print_count += 1
                
                # الصفحة التالية (إن كانت هناك صور أخرى)
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
    
    def cleanup_cache(self):
        """تنظيف الـ cache لتوفير الذاكرة"""
        self.image_cache.clear()
        self.scaled_cache.clear()
    
    def closeEvent(self, event):
        """عند إغلاق النافذة"""
        self.cleanup_cache()
        super().closeEvent(event)