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
        
        print(f"\n[VIEWER] تهيئة العارض:")
        print(f"  • معرف الوثيقة: {document_id}")
        print(f"  • اسم الوثيقة: {document_data[1]}")
        print(f"  • عدد الصور المتلقاة: {len(self.image_paths)}")
        
        if self.image_paths:
            print(f"  • أول صورة: {self.image_paths[0]}")
            print(f"  • آخر صورة: {self.image_paths[-1]}")
        
        self.setWindowTitle(f"عرض الوثيقة - {document_data[1]}")
        self.setGeometry(100, 100, 900, 700)
        self.init_ui()
        
        # عرض الصورة الأولى
        if self.image_paths:
            self.display_image(0)
    
    def init_ui(self):
        """إنشاء واجهة المشاهد"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # معلومات الصورة/المرفق الحالي (شريط واحد فقط)
        self.current_image_info = QLabel()
        self.current_image_info.setStyleSheet(
            "background-color: #2c3e50; color: white; padding: 12px; "
            "font-size: 13px; border-radius: 5px; margin: 5px;"
        )
        self.current_image_info.setWordWrap(True)
        self.current_image_info.setMinimumHeight(80)
        main_layout.addWidget(self.current_image_info)
        
        # منطقة عرض الصور مع قائمة الصور
        content_layout = QHBoxLayout()
        
        # قائمة الصور على اليسار
        image_list_layout = QVBoxLayout()
        image_list_layout.addWidget(QLabel('<b>قائمة الصور:</b>'))
        
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.image_list.itemSelectionChanged.connect(self.on_image_selected)
        self.image_list.setMaximumWidth(150)
        
        # إضافة الصور إلى القائمة
        for i, image_path in enumerate(self.image_paths):
            item = QListWidgetItem(f"صورة {i+1}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.image_list.addItem(item)
        
        image_list_layout.addWidget(self.image_list)
        
        # أزرار التحكم بالقائمة
        image_buttons_layout = QVBoxLayout()
        
        select_all_images_btn = QPushButton('✓ اختر الكل')
        select_all_images_btn.clicked.connect(self.select_all_images)
        image_buttons_layout.addWidget(select_all_images_btn)
        
        deselect_all_images_btn = QPushButton('✗ إلغاء')
        deselect_all_images_btn.clicked.connect(self.deselect_all_images)
        image_buttons_layout.addWidget(deselect_all_images_btn)
        
        delete_selected_images_btn = QPushButton('🗑️ حذف المحددة')
        delete_selected_images_btn.setStyleSheet('background-color: #e74c3c; color: white;')
        delete_selected_images_btn.clicked.connect(self.delete_selected_images)
        image_buttons_layout.addWidget(delete_selected_images_btn)
        
        image_buttons_layout.addStretch()
        image_list_layout.addLayout(image_buttons_layout)
        
        content_layout.addLayout(image_list_layout, 0)
        
        # منطقة عرض الصور الرئيسية
        viewer_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(f"background-color: {COLORS['white']}; border: 2px solid {COLORS['border']};")
        
        if not self.image_paths:
            self.image_label.setText("❌ لا توجد صور متاحة")
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        
        viewer_layout.addWidget(scroll_area)
        
        # أزرار التحكم
        control_layout = QHBoxLayout()
        
        prev_btn = QPushButton('⬅️ السابق')
        prev_btn.clicked.connect(self.prev_page)
        prev_btn.setEnabled(len(self.image_paths) > 1)
        control_layout.addWidget(prev_btn)
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(len(self.image_paths) if self.image_paths else 1)
        self.page_spin.setValue(1)
        self.page_spin.valueChanged.connect(self.go_to_page)
        control_layout.addWidget(QLabel('الصفحة:'))
        control_layout.addWidget(self.page_spin)
        
        page_count_label = QLabel(f'من {len(self.image_paths)}')
        control_layout.addWidget(page_count_label)
        
        next_btn = QPushButton('التالي ➡️')
        next_btn.clicked.connect(self.next_page)
        next_btn.setEnabled(len(self.image_paths) > 1)
        control_layout.addWidget(next_btn)
        
        control_layout.addStretch()
        
        print_btn = QPushButton('🖨️ طباعة')
        print_btn.clicked.connect(self.print_images)
        control_layout.addWidget(print_btn)
        
        export_btn = QPushButton('💾 تصدير')
        export_btn.clicked.connect(self.export_images)
        control_layout.addWidget(export_btn)
        
        viewer_layout.addLayout(control_layout)
        
        content_layout.addLayout(viewer_layout, 1)
        
        main_layout.addLayout(content_layout)
        
        central_widget.setLayout(main_layout)
        
        # عرض الصورة الأولى
        if self.image_paths:
            self.display_image(0)
    
    def display_image(self, index):
        """عرض الصورة في الموضع المحدد"""
        if 0 <= index < len(self.image_paths):
            self.current_page = index
            image_path = self.image_paths[index]
            
            print(f"\n[DISPLAY] محاولة تحميل الصورة رقم {index + 1}/{len(self.image_paths)}:")
            print(f"  • المسار: {image_path}")
            print(f"  • موجودة؟ {os.path.exists(image_path)}")
            
            # تحقق من وجود الملف
            if not os.path.exists(image_path):
                self.image_label.setText(f"❌ الصورة غير موجودة:\n{image_path}")
                print(f"  ❌ ERROR: الملف غير موجود")
                return
            
            # حاول تحميل الصورة
            pixmap = QPixmap(image_path)
            
            # تحقق من أن الصورة تم تحميلها بنجاح
            if pixmap.isNull():
                self.image_label.setText(f"❌ فشل تحميل الصورة:\n{image_path}\n(قد يكون الملف تالفاً)")
                print(f"  ❌ ERROR: فشل تحميل الصورة")
                return
            
            print(f"  • الحجم الأصلي: {pixmap.width()}x{pixmap.height()}")
            
            # تحجيم الصورة لتناسب الحجم
            scaled_pixmap = pixmap.scaledToWidth(700, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
            # تحديث شريط التمرير
            self.page_spin.blockSignals(True)
            self.page_spin.setValue(index + 1)
            self.page_spin.blockSignals(False)
            
            # عرض معلومات الصورة/المرفق الحالي
            self._update_current_image_info(index)
            
            print(f"  ✅ تم تحميل الصورة بنجاح (الحجم بعد التحجيم: {scaled_pixmap.width()}x{scaled_pixmap.height()})")
    
    def _update_current_image_info(self, index):
        """تحديث معلومات الصورة/المرفق الحالي"""
        total_pages = len(self.image_paths)
        
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
            
            # بناء النص بتنسيق أنيق
            header = f"<span style='font-size: 15px;'>{type_icon} <b>{type_text}</b></span>"
            page_info = f"<span style='color: #bdc3c7;'>الصفحة {index + 1} من {total_pages}</span>"
            
            if notes:
                # تحويل الملاحظات لتنسيق أفضل مع أيقونات
                notes_parts = notes.split(' | ')
                notes_html = ""
                for part in notes_parts:
                    if part.startswith('رقم:'):
                        notes_html += f"<br>🔢 {part}"
                    elif part.startswith('تاريخ:'):
                        notes_html += f"<br>📅 {part}"
                    elif part.startswith('مضمون:'):
                        notes_html += f"<br>📝 {part}"
                    elif part.startswith('جهة:'):
                        notes_html += f"<br>🏢 {part}"
                    elif part.startswith('تصنيف:'):
                        notes_html += f"<br>🏷️ {part}"
                    elif part.startswith('ملاحظات:'):
                        notes_html += f"<br>💬 {part}"
                    else:
                        notes_html += f"<br>• {part}"
                
                info_text = f"{header} &nbsp;&nbsp; {page_info}{notes_html}"
            else:
                info_text = f"{header} &nbsp;&nbsp; {page_info}<br><br><span style='color: #95a5a6;'>لا توجد معلومات إضافية</span>"
            
            self.current_image_info.setText(info_text)
        else:
            self.current_image_info.setText(f"<b>📄 الصورة {index + 1} من {total_pages}</b>")
    
    def prev_page(self):
        """الصفحة السابقة"""
        print(f"\n[BTN-PREV] نقر على زر السابق (حالياً في صفحة {self.current_page + 1})")
        if self.current_page > 0:
            self.display_image(self.current_page - 1)
        else:
            print("  ⚠️  أنت بالفعل في الصفحة الأولى")
    
    def next_page(self):
        """الصفحة التالية"""
        print(f"\n[BTN-NEXT] نقر على زر التالي (حالياً في صفحة {self.current_page + 1})")
        if self.current_page < len(self.image_paths) - 1:
            self.display_image(self.current_page + 1)
        else:
            print(f"  ⚠️  أنت بالفعل في الصفحة الأخيرة ({len(self.image_paths)})")
    
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

    def on_image_selected(self):
        """عند اختيار صورة من القائمة"""
        selected_items = self.image_list.selectedItems()
        if selected_items:
            index = self.image_list.row(selected_items[0])
            self.display_image(index)
    
    def select_all_images(self):
        """اختيار جميع الصور"""
        for i in range(self.image_list.count()):
            self.image_list.item(i).setSelected(True)
        QMessageBox.information(self, 'تحديد', f'تم تحديد جميع الصور ({self.image_list.count()} صورة)')
    
    def deselect_all_images(self):
        """إلغاء تحديد جميع الصور"""
        self.image_list.clearSelection()
    
    def delete_selected_images(self):
        """حذف الصور المحددة من الوثيقة"""
        selected_items = self.image_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, 'تنبيه', 'يجب تحديد صور للحذف أولاً')
            return
        
        count = len(selected_items)
        reply = QMessageBox.question(
            self,
            'تأكيد الحذف',
            f'هل أنت متأكد من حذف {count} صورة؟\n\nسيتم حذفها من قاعدة البيانات والقرص الصلب',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from pathlib import Path
                import sys
                
                print(f"\n[DELETE] بدء حذف {count} صورة...")
                
                # احصل على قائمة الصور المراد حذفها (قبل تعديل القائمة)
                images_to_delete = []
                for item in selected_items:
                    index = self.image_list.row(item)
                    if 0 <= index < len(self.image_paths):
                        images_to_delete.append((index, self.image_paths[index]))
                
                print(f"[DELETE] الصور المراد حذفها: {len(images_to_delete)}")
                
                # احذفها من الأعلى للأسفل لتجنب مشاكل الفهرسة
                deleted_count = 0
                deleted_paths = []
                
                for index, image_path in sorted(images_to_delete, reverse=True):
                    try:
                        print(f"[DELETE] حذف صورة #{index}: {image_path}")
                        
                        path = Path(image_path)
                        if path.exists():
                            path.unlink()
                            deleted_count += 1
                            deleted_paths.append(image_path)
                            print(f"[DELETE] ✓ تم حذف الملف: {image_path}")
                        else:
                            print(f"[WARNING] الملف غير موجود: {image_path}")
                        
                        # حذف الصورة المصغرة إن وجدت
                        try:
                            thumb_path = path.parent.parent / 'thumbnails' / f'{path.stem}_thumb.jpg'
                            if thumb_path.exists():
                                thumb_path.unlink()
                                print(f"[DELETE] ✓ تم حذف الصورة المصغرة")
                        except Exception as e:
                            print(f"[WARNING] فشل حذف الصورة المصغرة: {e}")
                        
                    except Exception as e:
                        print(f"[ERROR] خطأ في حذف {image_path}: {e}")
                    
                    # احذفها من القائمة والبيانات
                    try:
                        self.image_list.takeItem(index)
                        self.image_paths.pop(index)
                        print(f"[DELETE] ✓ تم إزالة من القائمة")
                    except Exception as e:
                        print(f"[ERROR] خطأ في إزالة من القائمة: {e}")
                
                print(f"[DELETE] تم حذف {deleted_count} صورة من النظام")
                
                # حذف الصور من قاعدة البيانات
                if deleted_paths:
                    try:
                        print(f"[DELETE] جاري حذف من قاعدة البيانات...")
                        sys.path.insert(0, str(Path(__file__).parent.parent))
                        from database.db_manager import DatabaseManager
                        
                        db = DatabaseManager()
                        for image_path in deleted_paths:
                            try:
                                db.delete_image_by_path(image_path)
                                print(f"[DELETE] ✓ تم حذف من قاعدة البيانات: {image_path}")
                            except Exception as e:
                                print(f"[ERROR] فشل حذف من قاعدة البيانات: {e}")
                    except Exception as e:
                        print(f"[ERROR] خطأ في حذف من قاعدة البيانات: {e}")
                
                # تحديث العرض
                print(f"[DELETE] تحديث الواجهة...")
                if self.image_paths:
                    self.display_image(0)
                    print(f"[DELETE] عرض الصورة الأولى المتبقية")
                else:
                    self.image_label.setText("❌ لا توجد صور متبقية")
                    self.page_spin.setMaximum(0)
                    print(f"[DELETE] لا توجد صور متبقية")
                
                # رسالة النجاح
                if deleted_count > 0:
                    msg = f'تم حذف {deleted_count} صورة بنجاح'
                    QMessageBox.information(self, 'نجح', msg)
                    print(f"[DELETE] {msg}")
                else:
                    msg = 'لم يتم حذف أي صور'
                    QMessageBox.warning(self, 'تنبيه', msg)
                    print(f"[DELETE] {msg}")
            
            except Exception as e:
                error_msg = f'حدث خطأ أثناء الحذف:\n{str(e)}'
                QMessageBox.critical(self, 'خطأ', error_msg)
                print(f"[ERROR] خطأ حرج في حذف الصور: {e}")
                import traceback
                traceback.print_exc()

