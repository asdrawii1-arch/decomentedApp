import re
import easyocr
from datetime import datetime

class OCRExtractor:
    """استخراج المعلومات من الصور باستخدام OCR"""
    
    def __init__(self):
        """تهيئة قارئ OCR"""
        try:
            self.reader = easyocr.Reader(['ar', 'en'])
        except Exception as e:
            print(f"[ERROR] خطأ في تهيئة OCR: {str(e)}")
            self.reader = None
    
    def extract_text(self, image_path):
        """استخراج النصوص من الصورة"""
        if not self.reader:
            return None
        
        try:
            result = self.reader.readtext(image_path)
            text = '\n'.join([line[1] for line in result])
            return text
        except Exception as e:
            print(f"[ERROR] خطأ في استخراج النصوص: {str(e)}")
            return None
    
    def extract_document_info(self, image_path):
        """استخراج معلومات الوثيقة من الصورة"""
        text = self.extract_text(image_path)
        if not text:
            return None
        
        return {
            'doc_number': self._extract_document_number(text),
            'doc_date': self._extract_date(text),
            'doc_title': self._extract_title(text),
            'issuing_dept': self._extract_department(text)
        }
    
    def _extract_document_number(self, text):
        """استخراج رقم الوثيقة - يبحث بعد كلمة 'العدد' أو 'عدد'"""
        # ابحث عن رقم بعد كلمة العدد
        patterns = [
            r'العدد\s*:?\s*(\d+)',
            r'عدد\s*:?\s*(\d+)',
            r'رقم\s*:?\s*(\d+)',
            r'الرقم\s*:?\s*(\d+)',
            r'^\s*(\d{1,5})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1)
        
        return ''
    
    def _extract_date(self, text):
        """استخراج التاريخ - يبحث بعد كلمة 'تاريخ' أو 'التاريخ'"""
        # ابحث عن تواريخ بصيغ مختلفة بعد كلمة تاريخ
        patterns = [
            r'التاريخ\s*:?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'تاريخ\s*:?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'في\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                day, month, year = match.groups()
                return f"{day}-{month}-{year}"
        
        return ''
    
    def _extract_title(self, text):
        """استخراج عنوان/موضوع الوثيقة - يبحث بعد كلمة 'موضوع' في وسط الكتاب"""
        # ابحث عن نص بعد كلمة موضوع
        pattern = r'موضوع\s*:?\s*(.{10,200}?)(?:\n|$|\.)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            title = match.group(1).strip()
            # نظف النص
            title = re.sub(r'\s+', ' ', title)
            return title[:100]
        
        # إذا لم نجد، خذ أول سطر طويل
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 15 and len(line) < 150:
                # تأكد أنه ليس رقم أو تاريخ فقط
                if not re.match(r'^[\d\s/-]+$', line):
                    return line[:100]
        
        return ''
    
    def _extract_department(self, text):
        """استخراج جهة الإصدار"""
        # ابحث عن جهات معروفة
        departments = [
            ('شعبة أمن الأفراد', ['شعبة أمن الأفراد', 'أمن الأفراد']),
            ('قسم أمن الأفراد الأنبار', ['قسم أمن الأفراد الأنبار', 'الأنبار']),
            ('شعبة التحريات', ['شعبة التحريات', 'التحريات']),
            ('قسم البحث الجنائي', ['قسم البحث الجنائي', 'البحث الجنائي']),
        ]
        
        for dept_name, keywords in departments:
            for keyword in keywords:
                if keyword in text:
                    return dept_name
        
        # ابحث عن كلمة "من" أو "صادرة عن"
        pattern = r'(?:من|صادرة عن|إصدار)\s+(.{5,50}?)(?:\n|$|في|،)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        
        return ''
