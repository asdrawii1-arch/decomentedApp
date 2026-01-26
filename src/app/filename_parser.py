import re
from datetime import datetime

class FilenameParser:
    """معالج أسماء الملفات لاستخراج البيانات"""
    
    # قاموس الاختصارات
    ABBREVIATIONS = {
        'ص': 'شعبة أمن الأفراد عنة',
        'و': 'قسم أمن الأفراد الأنبار'
    }
    
    @staticmethod
    def parse_filename(filename):
        """
        معالجة اسم الملف واستخراج البيانات
        مثال: "65 في 23-3-2025 ص" -> {number: 65, date: 23-3-2025, dept: شعبة أمن أفراد}
        أو "9236 في 6-11-2025 و_0002" -> {number: 9236, date: 6-11-2025, dept: قسم أمن الأفراد الأنبار, sequence: 0002}
        """
        result = {
            'number': None,
            'date': None,
            'department': None,
            'sequence': None,
            'is_valid': False
        }
        
        # إزالة الامتداد
        name_without_ext = re.sub(r'\.\w+$', '', filename)
        
        # البحث عن النمط: رقم في تاريخ [اختصار] [_تسلسل]
        pattern = r'(\d+)\s+في\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})\s+([ص و])(?:_(\d{4}))?'
        match = re.search(pattern, name_without_ext)
        
        if match:
            result['number'] = match.group(1)
            result['date'] = FilenameParser._normalize_date(match.group(2))
            abbr = match.group(3)
            result['department'] = FilenameParser.ABBREVIATIONS.get(abbr, abbr)
            result['sequence'] = match.group(4) if match.group(4) else None
            result['is_valid'] = True
        
        return result
    
    @staticmethod
    def _normalize_date(date_str):
        """تنسيق التاريخ"""
        # تحويل / إلى -
        date_str = date_str.replace('/', '-')
        parts = date_str.split('-')
        
        if len(parts) == 3:
            day, month, year = parts
            # تحويل إلى صيغة موحدة
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%d-%m-%Y')
            except:
                return date_str
        
        return date_str
    
    @staticmethod
    def generate_document_name(number, date, department):
        """توليد اسم الوثيقة من البيانات"""
        return f"{number} في {date} {FilenameParser._get_abbreviation(department)}"
    
    @staticmethod
    def _get_abbreviation(department):
        """الحصول على الاختصار من اسم الجهة"""
        for abbr, full_name in FilenameParser.ABBREVIATIONS.items():
            if department == full_name:
                return abbr
        return department


class ImageSequenceHandler:
    """معالج تسلسل الصور"""
    
    @staticmethod
    def extract_sequence(filename):
        """استخراج رقم التسلسل من اسم الملف"""
        # البحث عن نمط _0001 أو _0002 وغيره
        match = re.search(r'_(\d{4})(?:\.\w+)?$', filename)
        if match:
            return int(match.group(1))
        return None
    
    @staticmethod
    def is_main_image(filename):
        """التحقق من أن الصورة الرئيسية (بدون 000X)"""
        sequence = ImageSequenceHandler.extract_sequence(filename)
        return sequence is None
    
    @staticmethod
    def group_images(filenames):
        """تجميع الصور حسب الصورة الرئيسية"""
        groups = {}
        
        for filename in filenames:
            # استخراج الرقم الأساسي
            base_match = re.match(r'(\d+)\s+في', filename)
            if base_match:
                base_number = base_match.group(1)
                sequence = ImageSequenceHandler.extract_sequence(filename)
                
                if base_number not in groups:
                    groups[base_number] = {
                        'main': None,
                        'pages': []
                    }
                
                if sequence is None:
                    groups[base_number]['main'] = filename
                else:
                    groups[base_number]['pages'].append((sequence, filename))
        
        # ترتيب الصور حسب التسلسل
        for base_number in groups:
            groups[base_number]['pages'].sort(key=lambda x: x[0])
            groups[base_number]['pages'] = [filename for _, filename in groups[base_number]['pages']]
        
        return groups
