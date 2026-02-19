import sqlite3
import os
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path='documents.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول الوثائق
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_name TEXT NOT NULL,
                doc_date TEXT,
                doc_title TEXT,
                issuing_dept TEXT,
                doc_classification TEXT,
                legal_paragraph TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الصور
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                original_filename TEXT,
                page_number INTEGER,
                image_number TEXT,
                sides INTEGER,
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')
        
        # جدول البحث
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_term TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_document(self, doc_name, doc_date, doc_title, issuing_dept, doc_classification, legal_paragraph):
        """إضافة وثيقة جديدة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (doc_name, doc_date, doc_title, issuing_dept, doc_classification, legal_paragraph)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (doc_name, doc_date, doc_title, issuing_dept, doc_classification, legal_paragraph))
        
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        return doc_id
    
    def add_image(self, document_id, image_path, original_filename, page_number, image_number, sides, notes=None):
        """إضافة صورة للوثيقة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # التحقق من وجود عمود notes
        cursor.execute("PRAGMA table_info(images)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'notes' in columns:
            cursor.execute('''
                INSERT INTO images (document_id, image_path, original_filename, page_number, image_number, sides, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (document_id, image_path, original_filename, page_number, image_number, sides, notes))
        else:
            # إضافة العمود إذا لم يكن موجوداً
            try:
                cursor.execute('ALTER TABLE images ADD COLUMN notes TEXT')
                conn.commit()
            except:
                pass
            
            cursor.execute('''
                INSERT INTO images (document_id, image_path, original_filename, page_number, image_number, sides, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (document_id, image_path, original_filename, page_number, image_number, sides, notes))
        
        conn.commit()
        image_id = cursor.lastrowid
        conn.close()
        return image_id
    
    def search_documents(self, search_term, search_field='doc_name'):
        """البحث عن الوثائق"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f'SELECT * FROM documents WHERE {search_field} LIKE ?'
        cursor.execute(query, (f'%{search_term}%',))
        
        results = cursor.fetchall()
        conn.close()
        
        # حفظ في السجل
        self.save_search_history(search_term)
        
        return results
    
    def find_document_exact(self, doc_name):
        """البحث عن وثيقة بالاسم الدقيق (مطابقة تامة)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE doc_name = ?', (doc_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def find_document_by_number(self, doc_number):
        """البحث عن وثيقة برقم الوثيقة فقط (البحث في بداية اسم الوثيقة)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # البحث عن الوثائق التي تبدأ برقم معين متبوعاً بمسافة
        cursor.execute('SELECT * FROM documents WHERE doc_name LIKE ?', (f'{doc_number} %',))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def find_document_by_number_and_date(self, doc_number, doc_date):
        """البحث عن وثيقة برقم الوثيقة والتاريخ (للتحقق من التكرار عند الاستيراد)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # البحث عن الوثائق التي تحتوي على الرقم والتاريخ في اسم الوثيقة
        # الصيغة المتوقعة: "رقم في تاريخ"
        doc_name_pattern = f'{doc_number} في {doc_date}'
        
        cursor.execute('''
            SELECT * FROM documents 
            WHERE doc_name = ? OR doc_name LIKE ?
        ''', (doc_name_pattern, f'{doc_name_pattern}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def search_documents_and_attachments(self, search_term, search_field='doc_name'):
        """البحث عن الوثائق والمرفقات حسب الحقل المختار بدقة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # تحويل النتائج لقاموس للتحقق من التكرار
        results_dict = {}
        
        # البحث في الوثائق الرئيسية حسب الحقل المحدد
        if search_field == 'doc_name':
            # البحث الدقيق في رقم الوثيقة - أولاً المطابق تماماً، ثم المبتدئ بنفس الرقم
            cursor.execute('''
                SELECT *, 
                       CASE 
                           WHEN SUBSTR(doc_name, 1, INSTR(doc_name || ' ', ' ') - 1) = ? THEN 1
                           WHEN SUBSTR(doc_name, 1, INSTR(doc_name || ' ', ' ') - 1) LIKE ? THEN 2
                           ELSE 3
                       END as priority
                FROM documents 
                WHERE SUBSTR(doc_name, 1, INSTR(doc_name || ' ', ' ') - 1) = ? 
                   OR SUBSTR(doc_name, 1, INSTR(doc_name || ' ', ' ') - 1) LIKE ?
                ORDER BY priority, CAST(SUBSTR(doc_name, 1, INSTR(doc_name || ' ', ' ') - 1) AS INTEGER)
            ''', (search_term, f'{search_term}%', search_term, f'{search_term}%',))
        elif search_field == 'doc_date':
            # البحث في التاريخ فقط
            cursor.execute('SELECT * FROM documents WHERE doc_date LIKE ? ORDER BY doc_date', (f'%{search_term}%',))
        elif search_field == 'doc_title':
            # البحث في المضمون فقط
            cursor.execute('SELECT * FROM documents WHERE doc_title LIKE ? ORDER BY doc_title', (f'%{search_term}%',))
        elif search_field == 'issuing_dept':
            # البحث في الجهة فقط
            cursor.execute('SELECT * FROM documents WHERE issuing_dept LIKE ? ORDER BY issuing_dept', (f'%{search_term}%',))
        elif search_field == 'doc_classification':
            # البحث في التصنيف فقط
            cursor.execute('SELECT * FROM documents WHERE doc_classification LIKE ? ORDER BY doc_classification', (f'%{search_term}%',))
        else:
            # حماية من SQL injection - استخدام الحقل الافتراضي
            cursor.execute('SELECT * FROM documents WHERE doc_name LIKE ? ORDER BY doc_name', (f'%{search_term}%',))
        
        doc_results = cursor.fetchall()
        
        # إضافة نتائج البحث الرئيسية
        for doc in doc_results:
            # استبعاد عمود priority إذا كان موجوداً (في حالة البحث بـ doc_name)
            if search_field == 'doc_name' and len(doc) > 7:
                doc = doc[:-1]  # إزالة العمود الأخير (priority)
            
            doc_id = doc[0]
            doc_name = doc[1] or ''
            # استخراج رقم الوثيقة من الاسم
            doc_number = doc_name.split()[0] if doc_name else ''
            results_dict[doc_id] = {
                'doc': doc,
                'doc_number': doc_number,
                'source': 'main',  # المصدر: الوثيقة الرئيسية
                'attachment_info': None
            }
        
        # البحث في المرفقات والصور الإضافية
        if search_field == 'doc_name':
            # البحث في ملاحظات الصور للعثور على وثائق تحتوي على نفس الرقم في المرفقات
            cursor.execute('''
                SELECT DISTINCT i.document_id, i.notes, d.*
                FROM images i
                JOIN documents d ON i.document_id = d.id
                WHERE i.notes IS NOT NULL 
                ORDER BY CAST(SUBSTR(d.doc_name, 1, INSTR(d.doc_name || ' ', ' ') - 1) AS INTEGER)
            ''')
            
            attachment_results = cursor.fetchall()
            
            for row in attachment_results:
                doc_id = row[0]
                attachment_notes = row[1] or ''
                doc_data = row[2:]  # بيانات الوثيقة تبدأ من العمود 2
                
                # البحث في ملاحظات المرفق عن رقم الوثيقة
                if attachment_notes:
                    import re
                    # البحث عن "رقم: X" في الملاحظات
                    number_match = re.search(r'رقم:\s*([^\|]+)', attachment_notes)
                    if number_match:
                        attachment_number = number_match.group(1).strip()
                        # تحقق إذا كان رقم المرفق يطابق البحث تماماً أو يبدأ بنفس الرقم
                        if (attachment_number == search_term or 
                            attachment_number.startswith(search_term)):
                            
                            # إذا كانت الوثيقة موجودة بالفعل في النتائج
                            if doc_id in results_dict:
                                main_doc_number = results_dict[doc_id]['doc_number']
                                # إذا كان رقم المرفق مختلف عن رقم الوثيقة الرئيسية
                                if attachment_number != main_doc_number:
                                    # أضف كنتيجة منفصلة (مرفق)
                                    new_key = f"{doc_id}_att_{len(results_dict)}"
                                    results_dict[new_key] = {
                                        'doc': doc_data,
                                        'doc_number': attachment_number,
                                        'source': 'attachment',
                                        'attachment_info': attachment_notes
                                    }
                            else:
                                # الوثيقة غير موجودة في النتائج الرئيسية، أضفها
                                results_dict[f"{doc_id}_att"] = {
                                    'doc': doc_data,
                                    'doc_number': attachment_number,
                                    'source': 'attachment',
                                    'attachment_info': attachment_notes
                                }
        
        elif search_field == 'doc_title':
            # البحث في مضمون المرفقات
            cursor.execute('''
                SELECT DISTINCT i.document_id, i.notes, d.*
                FROM images i
                JOIN documents d ON i.document_id = d.id
                WHERE i.notes LIKE ?
                ORDER BY d.doc_title
            ''', (f'%مضمون:%{search_term}%',))
            
            attachment_results = cursor.fetchall()
            
            for row in attachment_results:
                doc_id = row[0]
                attachment_notes = row[1] or ''
                doc_data = row[2:]
                
                if attachment_notes and search_term.lower() in attachment_notes.lower():
                    # إذا كانت الوثيقة غير موجودة في النتائج، أضفها
                    if doc_id not in results_dict:
                        import re
                        number_match = re.search(r'رقم:\s*([^\|]+)', attachment_notes)
                        attachment_number = number_match.group(1).strip() if number_match else ''
                        
                        results_dict[f"{doc_id}_att"] = {
                            'doc': doc_data,
                            'doc_number': attachment_number,
                            'source': 'attachment',
                            'attachment_info': attachment_notes
                        }
        
        conn.close()
        
        # حفظ في السجل
        self.save_search_history(search_term)
        
        return results_dict
    
    def save_search_history(self, search_term):
        """حفظ سجل البحث"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO search_history (search_term) VALUES (?)', (search_term,))
        conn.commit()
        conn.close()
    
    def get_document_by_id(self, doc_id):
        """الحصول على وثيقة من خلال ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_document_images(self, document_id):
        """الحصول على صور الوثيقة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM images WHERE document_id = ? ORDER BY page_number', (document_id,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_documents(self):
        """الحصول على جميع الوثائق"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents ORDER BY created_date DESC')
        results = cursor.fetchall()
        conn.close()
        return results

    def get_document_ids_by_image_year(self, year):
        """إرجاع قائمة معرفات الوثائق التي تحتوي صورها داخل مجلد السنة المحدد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # دعم كل من الفواصل \ و /
        pattern1 = f'%documents/{year}/%'
        pattern2 = f'%documents\\{year}\\%'
        cursor.execute('SELECT DISTINCT document_id FROM images WHERE image_path LIKE ? OR image_path LIKE ?', (pattern1, pattern2))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]
    
    def update_document(self, doc_id, doc_name=None, doc_date=None, doc_title=None, 
                       issuing_dept=None, doc_classification=None, legal_paragraph=None):
        """تحديث بيانات الوثيقة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        
        if doc_name:
            update_fields.append('doc_name = ?')
            params.append(doc_name)
        if doc_date:
            update_fields.append('doc_date = ?')
            params.append(doc_date)
        if doc_title:
            update_fields.append('doc_title = ?')
            params.append(doc_title)
        if issuing_dept:
            update_fields.append('issuing_dept = ?')
            params.append(issuing_dept)
        if doc_classification:
            update_fields.append('doc_classification = ?')
            params.append(doc_classification)
        if legal_paragraph:
            update_fields.append('legal_paragraph = ?')
            params.append(legal_paragraph)
        
        update_fields.append('updated_date = CURRENT_TIMESTAMP')
        params.append(doc_id)
        
        query = f"UPDATE documents SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
    
    def delete_document(self, doc_id):
        """حذف وثيقة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # حذف الصور أولاً
        cursor.execute('DELETE FROM images WHERE document_id = ?', (doc_id,))
        # حذف الوثيقة
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        
        conn.commit()
        conn.close()
    
    def delete_image_by_path(self, image_path):
        """حذف صورة من قاعدة البيانات بناءً على المسار"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM images WHERE image_path = ?', (image_path,))
            conn.commit()
        except Exception as e:
            print(f"خطأ في حذف الصورة من قاعدة البيانات: {e}")
        finally:
            conn.close()
