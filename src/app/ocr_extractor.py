import re
import os

# محاولة استخدام pytesseract (أخف وأسرع)
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    TESSERACT_AVAILABLE = True
    
    # محاولة تحديد مسار Tesseract على Windows
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe',
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
            
except ImportError:
    TESSERACT_AVAILABLE = False
    print("[WARNING] pytesseract غير مثبت")

class OCRExtractor:
    """استخراج المعلومات من الصور باستخدام OCR"""
    
    def __init__(self):
        """تهيئة قارئ OCR"""
        self.reader = None
        
        if TESSERACT_AVAILABLE:
            try:
                # اختبار أن Tesseract يعمل
                pytesseract.get_tesseract_version()
                self.reader = True
                print("[OCR] تم تهيئة Tesseract بنجاح")
            except Exception as e:
                print(f"[OCR ERROR] Tesseract غير مثبت أو غير متاح: {str(e)}")
                self.reader = None
    
    def _preprocess_image_v1(self, image_path):
        """معالجة الصورة - الطريقة الأولى (تباين عالي)"""
        try:
            img = Image.open(image_path)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # تكبير الصورة إذا كانت صغيرة
            width, height = img.size
            if width < 2000:
                scale = 2000 / width
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # تحويل إلى تدرج الرمادي
            img = img.convert('L')
            
            # زيادة التباين
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            # زيادة الحدة
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            return img
            
        except Exception as e:
            return Image.open(image_path)
    
    def _preprocess_image_v2(self, image_path):
        """معالجة الصورة - الطريقة الثانية (بدون معالجة كثيرة)"""
        try:
            img = Image.open(image_path)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # تكبير الصورة فقط
            width, height = img.size
            if width < 1500:
                scale = 1500 / width
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            return img
            
        except Exception as e:
            return Image.open(image_path)
    
    def extract_text(self, image_path):
        """استخراج النصوص من الصورة - محاولة عدة طرق"""
        if not self.reader:
            return None
        
        best_text = ""
        best_arabic_count = 0
        
        # قائمة الإعدادات المختلفة للمحاولة
        configs = [
            ('--oem 3 --psm 6 -l ara+eng', self._preprocess_image_v1),
            ('--oem 3 --psm 3 -l ara+eng', self._preprocess_image_v1),
            ('--oem 3 --psm 6 -l ara', self._preprocess_image_v2),
            ('--oem 3 --psm 4 -l ara+eng', self._preprocess_image_v2),
        ]
        
        for config, preprocess_func in configs:
            try:
                img = preprocess_func(image_path)
                text = pytesseract.image_to_string(img, config=config)
                
                # حساب عدد الأحرف العربية
                arabic_count = len(re.findall(r'[\u0600-\u06FF]', text))
                
                # البحث عن كلمة "الموضوع" - أولوية عالية
                has_subject = 'الموضوع' in text or 'موضوع' in text
                
                # اختيار أفضل نتيجة
                if has_subject and arabic_count > best_arabic_count * 0.7:
                    best_text = text
                    best_arabic_count = arabic_count
                    break  # وجدنا "الموضوع"، توقف
                elif arabic_count > best_arabic_count:
                    best_text = text
                    best_arabic_count = arabic_count
                    
            except Exception as e:
                continue
        
        return best_text if best_text else None
    
    def extract_document_info(self, image_path):
        """استخراج معلومات الوثيقة من الصورة"""
        text = self.extract_text(image_path)
        if not text:
            return None
        
        # طباعة جزء من النص للتشخيص
        print(f"[OCR] تم استخراج {len(text)} حرف")
        
        title = self._extract_title(text)
        
        # إذا لم نجد الموضوع، حاول بطريقة أخرى
        if not title:
            title = self._extract_title_fallback(text)
        
        return {
            'doc_number': self._extract_document_number(text),
            'doc_date': self._extract_date(text),
            'doc_title': title,
            'issuing_dept': self._extract_department(text)
        }
    
    def _extract_document_number(self, text):
        """استخراج رقم الوثيقة"""
        patterns = [
            r'العدد\s*[:/]?\s*(\d+)',
            r'عدد\s*[:/]?\s*(\d+)',
            r'رقم\s*[:/]?\s*(\d+)',
            r'الرقم\s*[:/]?\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1)
        
        return ''
    
    def _extract_date(self, text):
        """استخراج التاريخ"""
        patterns = [
            r'التاريخ\s*[:/]?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'تاريخ\s*[:/]?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'في\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                day, month, year = match.groups()
                return f"{day}-{month}-{year}"
        
        return ''
    
    def _extract_title(self, text):
        """استخراج عنوان/موضوع الوثيقة"""
        patterns = [
            # البحث عن الموضوع مع عدة أسطر بعده
            r'الموضوع\s*[:/\-]?\s*(.+?)(?=\n\s*\n|\n[أ-ي]*\s*[:/]|$)',
            r'موضوع\s*[:/\-]?\s*(.+?)(?=\n\s*\n|\n[أ-ي]*\s*[:/]|$)',
            r'م\s*/\s*(.+?)(?=\n\s*\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                # تنظيف العنوان
                title = self._clean_title(title)
                if len(title) > 3:
                    return title[:200]
        
        return ''
    
    def _extract_title_fallback(self, text):
        """طريقة بديلة لاستخراج الموضوع"""
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # البحث عن سطر يحتوي على "الموضوع" أو "موضوع"
            if 'الموضوع' in line or 'موضوع' in line:
                # استخراج ما بعد الكلمة في نفس السطر
                for keyword in ['الموضوع', 'موضوع']:
                    if keyword in line:
                        idx = line.find(keyword)
                        after = line[idx + len(keyword):].strip()
                        # إزالة علامات الترقيم من البداية
                        after = re.sub(r'^[\s:/\-]+', '', after).strip()
                        
                        # إذا كان هناك نص في نفس السطر
                        if len(after) > 3:
                            result = after
                        else:
                            result = ''
                        
                        # إضافة الأسطر التالية إذا لزم الأمر
                        for j in range(i + 1, min(i + 4, len(lines))):
                            next_line = lines[j].strip()
                            # توقف إذا وصلنا لقسم جديد
                            if any(kw in next_line for kw in ['العدد', 'التاريخ', 'إلى', 'من']):
                                break
                            if next_line and len(next_line) > 2:
                                result += ' ' + next_line
                        
                        result = self._clean_title(result)
                        if len(result) > 3:
                            return result[:200]
        
        return ''
    
    def _clean_title(self, title):
        """تنظيف عنوان الوثيقة"""
        if not title:
            return ''
        
        # إزالة الأسطر الجديدة المتعددة
        title = re.sub(r'\n+', ' ', title)
        # إزالة المسافات المتعددة
        title = re.sub(r'\s+', ' ', title)
        # إزالة الأرقام والرموز من البداية
        title = re.sub(r'^[\d\s/\-:\.،]+', '', title)
        # إزالة الأحرف الإنجليزية العشوائية
        title = re.sub(r'\b[A-Z]{2,}\b', '', title)
        # إزالة الرموز الغريبة
        title = re.sub(r'[^\u0600-\u06FFa-zA-Z0-9\s\-/:\.\,،()؟!]', '', title)
        
        return title.strip()
    
    def _extract_department(self, text):
        """استخراج جهة الإصدار"""
        departments = [
            ('شعبة أمن الأفراد عنة', ['شعبة أمن الأفراد', 'أمن الأفراد عنة', 'شعبة امن']),
            ('قسم أمن الأفراد الأنبار', ['قسم أمن الأفراد الأنبار', 'الأنبار', 'قسم امن']),
        ]
        
        for dept_name, keywords in departments:
            for keyword in keywords:
                if keyword in text:
                    return dept_name
        
        return ''
    
    def is_available(self):
        """التحقق من توفر OCR"""
        return self.reader is not None