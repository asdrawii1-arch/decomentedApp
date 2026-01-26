"""
وحدة المساعدات والوظائف الإضافية
"""

from datetime import datetime
from pathlib import Path


class DateHelper:
    """مساعد معالجة التواريخ"""
    
    @staticmethod
    def format_date(date_str):
        """تحويل التاريخ إلى صيغة موحدة"""
        formats = [
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%d-%m-%y',
            '%Y-%m-%d',
            '%d %m %Y'
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%d-%m-%Y')
            except:
                continue
        
        return date_str
    
    @staticmethod
    def get_current_date():
        """الحصول على التاريخ الحالي"""
        return datetime.now().strftime('%d-%m-%Y')


class FileHelper:
    """مساعد معالجة الملفات"""
    
    @staticmethod
    def get_file_size(file_path):
        """الحصول على حجم الملف بصيغة قابلة للقراءة"""
        size_bytes = Path(file_path).stat().st_size
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    def is_valid_image(file_path):
        """التحقق من أن الملف صورة صحيحة"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif']
        
        file_path = Path(file_path)
        
        if file_path.suffix.lower() not in valid_extensions:
            return False
        
        # التحقق من أن الملف موجود وقابل للقراءة
        if not file_path.exists() or not file_path.is_file():
            return False
        
        return True
    
    @staticmethod
    def safe_filename(filename):
        """جعل اسم الملف آمناً"""
        invalid_chars = '<>:"/\\|?*'
        
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename


class ValidationHelper:
    """مساعد التحقق من البيانات"""
    
    @staticmethod
    def validate_document_number(number_str):
        """التحقق من صحة رقم الوثيقة"""
        return number_str.isdigit() and 0 < int(number_str) < 999999
    
    @staticmethod
    def validate_date(date_str):
        """التحقق من صحة التاريخ"""
        try:
            DateHelper.format_date(date_str)
            return True
        except:
            return False
    
    @staticmethod
    def validate_document_data(data):
        """التحقق من صحة بيانات الوثيقة"""
        errors = []
        
        if not data.get('doc_name') or not data['doc_name'].strip():
            errors.append('اسم الوثيقة مطلوب')
        
        if data.get('doc_date') and not ValidationHelper.validate_date(data['doc_date']):
            errors.append('صيغة التاريخ غير صحيحة')
        
        if not data.get('issuing_dept') or data['issuing_dept'] == 'اختر جهة الإصدار':
            errors.append('يجب اختيار جهة الإصدار')
        
        return errors


class ExportHelper:
    """مساعد تصدير البيانات"""
    
    @staticmethod
    def export_to_csv(documents, filepath):
        """تصدير الوثائق إلى ملف CSV"""
        import csv
        
        try:
            with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                
                # رؤوس الأعمدة
                writer.writerow([
                    'الرقم', 'اسم الوثيقة', 'التاريخ', 'العنوان',
                    'جهة الإصدار', 'التصنيف', 'الفقرة القانونية'
                ])
                
                # البيانات
                for doc in documents:
                    writer.writerow([
                        doc[0], doc[1], doc[2], doc[3],
                        doc[4], doc[5], doc[6]
                    ])
            
            return True, f"تم التصدير بنجاح إلى {filepath}"
        
        except Exception as e:
            return False, f"خطأ في التصدير: {str(e)}"
    
    @staticmethod
    def export_to_json(documents, filepath):
        """تصدير الوثائق إلى ملف JSON"""
        import json
        
        try:
            data = []
            
            for doc in documents:
                data.append({
                    'id': doc[0],
                    'name': doc[1],
                    'date': doc[2],
                    'title': doc[3],
                    'issuing_department': doc[4],
                    'classification': doc[5],
                    'legal_paragraph': doc[6],
                    'created_date': doc[7]
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True, f"تم التصدير بنجاح إلى {filepath}"
        
        except Exception as e:
            return False, f"خطأ في التصدير: {str(e)}"


class DatabaseBackupHelper:
    """مساعد النسخ الاحتياطي لقاعدة البيانات"""
    
    @staticmethod
    def create_backup(db_path, backup_dir='backups'):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        import shutil
        
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)
            
            db_file = Path(db_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_path / f'backup_{timestamp}.db'
            
            shutil.copy2(db_file, backup_file)
            
            return True, f"تم إنشاء النسخة الاحتياطية: {backup_file}"
        
        except Exception as e:
            return False, f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}"
    
    @staticmethod
    def restore_backup(backup_file, db_path):
        """استعادة قاعدة البيانات من نسخة احتياطية"""
        import shutil
        
        try:
            shutil.copy2(backup_file, db_path)
            return True, "تم استعادة قاعدة البيانات بنجاح"
        
        except Exception as e:
            return False, f"خطأ في استعادة قاعدة البيانات: {str(e)}"
