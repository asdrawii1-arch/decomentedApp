"""
معالج أجهزة الماسح الضوئي
يدعم TWAIN و WIA على Windows
"""

import os
import subprocess
from pathlib import Path
from enum import Enum


class ScannerType(Enum):
    """أنواع أجهزة الماسح"""
    TWAIN = "twain"
    WIA = "wia"
    UNKNOWN = "unknown"


class ScannerManager:
    """مدير أجهزة الماسح الضوئي"""
    
    def __init__(self):
        self.available_scanners = []
        self.selected_scanner = None
        self.detect_scanners()
    
    def detect_scanners(self):
        """الكشف عن أجهزة الماسح المتصلة"""
        self.available_scanners = []
        
        # محاولة الكشف عن WIA على Windows
        try:
            import ctypes
            # هذا مثال تقريبي للكشف
            self.available_scanners.append({
                'name': 'جهاز ماسح محلي',
                'type': ScannerType.WIA,
                'id': 'local_scanner'
            })
        except:
            pass
        
        # إذا لم يتم العثور على أي ماسح
        if not self.available_scanners:
            self.available_scanners.append({
                'name': 'بدون ماسح متصل',
                'type': ScannerType.UNKNOWN,
                'id': 'none'
            })
    
    def get_available_scanners(self):
        """الحصول على قائمة الماسحات المتاحة"""
        return self.available_scanners
    
    def select_scanner(self, scanner_id):
        """اختيار ماسح معين"""
        for scanner in self.available_scanners:
            if scanner['id'] == scanner_id:
                self.selected_scanner = scanner
                return True
        return False
    
    def scan_document(self, output_dir, pages=1, sides=1, dpi=300):
        """
        مسح وثيقة
        
        Args:
            output_dir: مسار مجلد الحفظ
            pages: عدد الصفحات
            sides: عدد الوجوه (1 أو 2)
            dpi: الدقة (dots per inch)
        
        Returns:
            list: قائمة مسارات الملفات المحفوظة
        """
        if not self.selected_scanner:
            raise Exception('لم يتم اختيار ماسح')
        
        if self.selected_scanner['type'] == ScannerType.UNKNOWN:
            raise Exception('لا يوجد ماسح متصل')
        
        saved_files = []
        
        try:
            # يمكن إضافة أكواد معالجة حقيقية هنا
            # حالياً نرجع مثالاً
            for i in range(pages):
                if sides == 2:
                    # مسح الوجهين
                    pass
                
                filename = f"scan_{i+1:04d}.jpg"
                filepath = os.path.join(output_dir, filename)
                saved_files.append(filepath)
        
        except Exception as e:
            raise Exception(f'خطأ في المسح: {str(e)}')
        
        return saved_files
    
    def is_scanner_available(self):
        """التحقق من توفر ماسح"""
        return self.selected_scanner and self.selected_scanner['type'] != ScannerType.UNKNOWN


class ScannerDialog:
    """نافذة حوار لإعدادات الماسح"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.manager = ScannerManager()
        self.settings = {
            'dpi': 300,
            'pages': 1,
            'sides': 1,
            'color_mode': 'color'  # or 'bw'
        }
    
    def get_scanners(self):
        """الحصول على قائمة الماسحات"""
        return self.manager.get_available_scanners()
    
    def scan(self, output_dir, scanner_id=None):
        """بدء المسح"""
        if scanner_id:
            self.manager.select_scanner(scanner_id)
        
        try:
            files = self.manager.scan_document(
                output_dir,
                pages=self.settings['pages'],
                sides=self.settings['sides'],
                dpi=self.settings['dpi']
            )
            return files
        except Exception as e:
            raise e
