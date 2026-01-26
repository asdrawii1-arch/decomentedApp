"""
ملف الإعدادات والثوابت
"""

import json
from pathlib import Path

class Settings:
    """إدارة إعدادات البرنامج"""
    
    DEFAULT_SETTINGS = {
        'theme': 'gray',
        'language': 'ar',
        'window_geometry': {
            'width': 1200,
            'height': 700,
            'x': 0,
            'y': 0
        },
        'database': {
            'path': 'documents.db',
            'backup_interval': 7  # أيام
        },
        'scanner': {
            'default_dpi': 300,
            'default_sides': 1,
            'color_mode': 'color'
        },
        'storage': {
            'documents_folder': 'documents',
            'backup_folder': 'backups',
            'thumbnails_folder': 'documents/thumbnails'
        },
        'file_naming': {
            'auto_parse': True,
            'create_sequences': True
        },
        'ui': {
            'show_toolbar': True,
            'show_statusbar': True,
            'confirm_delete': True,
            'auto_save': True,
            'save_interval': 60  # ثواني
        }
    }
    
    def __init__(self, settings_file='settings.json'):
        self.settings_file = Path(settings_file)
        self.settings = self.load_settings()
    
    def load_settings(self):
        """تحميل الإعدادات من الملف"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.DEFAULT_SETTINGS.copy()
        
        return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """حفظ الإعدادات إلى الملف"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        """الحصول على قيمة إعداد"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """تعيين قيمة إعداد"""
        keys = key.split('.')
        current = self.settings
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self.save_settings()
    
    def reset_to_defaults(self):
        """إعادة تعيين الإعدادات الافتراضية"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()


# إنشاء نسخة عامة من الإعدادات
_global_settings = None

def get_settings():
    """الحصول على كائن الإعدادات العام"""
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings()
    return _global_settings
