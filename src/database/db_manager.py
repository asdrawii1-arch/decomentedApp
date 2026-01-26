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
