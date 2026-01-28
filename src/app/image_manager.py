"""
معالج الصور - دعم معالجة وتخزين الصور
"""

import os
from pathlib import Path
from PIL import Image
import shutil


class ImageManager:
    """مدير الصور والملفات"""
    
    def __init__(self, storage_dir='documents'):
        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(exist_ok=True)
        self.thumbnails_dir = self.storage_dir / 'thumbnails'
        self.thumbnails_dir.mkdir(exist_ok=True)
    
    def save_image(self, source_path, document_id, image_number=None, year=None):
        """
        حفظ الصورة في مجلد التخزين
        
        Args:
            source_path: مسار الملف الأصلي
            document_id: معرف الوثيقة
            image_number: رقم الصورة
        
        Returns:
            str: مسار الملف المحفوظ
        """
        source_path = Path(source_path).resolve()
        
        # تحديد مجلد السنة: يستعمل الوسيطة `year` إن وُجدت، وإلا يحاول استخلاصها من مسار المصدر
        year_dir = None
        if year:
            try:
                year_dir = str(year)
            except Exception:
                year_dir = None
        else:
            try:
                for p in source_path.parents:
                    try:
                        if p.parent.resolve() == self.storage_dir and p.name.isdigit():
                            year_dir = p.name
                            break
                    except Exception:
                        continue
            except Exception:
                year_dir = None

        # إنشاء مجلد للوثيقة (ضمن مجلد السنة إذا وُجدت)
        if year_dir:
            doc_dir = self.storage_dir / year_dir / f'doc_{document_id}'
            (self.storage_dir / year_dir).mkdir(exist_ok=True)
        else:
            doc_dir = self.storage_dir / f'doc_{document_id}'
        doc_dir.mkdir(exist_ok=True)
        
        # تحديد اسم الملف
        if image_number:
            filename = f'image_{image_number:04d}{source_path.suffix}'
        else:
            filename = source_path.name
        
        dest_path = doc_dir / filename
        
        # نسخ الملف
        shutil.copy2(source_path, dest_path)
        
        # إنشاء صورة مصغرة
        self.create_thumbnail(dest_path)
        
        return str(dest_path.resolve())
    
    def create_thumbnail(self, image_path, size=(150, 200)):
        """
        إنشاء صورة مصغرة
        
        Args:
            image_path: مسار الصورة
            size: حجم الصورة المصغرة (عرض، ارتفاع)
        """
        try:
            image_path = Path(image_path)
            
            # فتح الصورة
            img = Image.open(image_path)
            
            # تحويل إلى RGB إذا كانت RGBA
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # تغيير الحجم
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # حفظ الصورة المصغرة
            thumb_path = self.thumbnails_dir / f'{image_path.stem}_thumb.jpg'
            img.save(thumb_path, 'JPEG', quality=85)
            
        except Exception as e:
            print(f'خطأ في إنشاء الصورة المصغرة: {e}')
    
    def get_thumbnail(self, image_name):
        """الحصول على مسار الصورة المصغرة"""
        thumb_path = self.thumbnails_dir / f'{Path(image_name).stem}_thumb.jpg'
        if thumb_path.exists():
            return str(thumb_path)
        return None
    
    def get_document_images(self, document_id):
        """الحصول على قائمة صور الوثيقة"""
        doc_dir = self.storage_dir / f'doc_{document_id}'
        
        if not doc_dir.exists():
            return []
        
        images = []
        for file in sorted(doc_dir.glob('*')):
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                images.append(str(file))
        
        return images
    
    def delete_image(self, image_path):
        """حذف صورة"""
        image_path = Path(image_path)
        
        if image_path.exists():
            image_path.unlink()
            
            # حذف الصورة المصغرة
            thumb_path = self.thumbnails_dir / f'{image_path.stem}_thumb.jpg'
            if thumb_path.exists():
                thumb_path.unlink()
    
    def delete_document_images(self, document_id):
        """حذف جميع صور الوثيقة"""
        doc_dir = self.storage_dir / f'doc_{document_id}'
        
        if doc_dir.exists():
            for file in doc_dir.glob('*'):
                file.unlink()
            doc_dir.rmdir()
    
    def get_image_info(self, image_path):
        """الحصول على معلومات الصورة"""
        try:
            img = Image.open(image_path)
            return {
                'size': img.size,
                'mode': img.mode,
                'format': img.format,
                'dpi': img.info.get('dpi', (72, 72))
            }
        except:
            return None
