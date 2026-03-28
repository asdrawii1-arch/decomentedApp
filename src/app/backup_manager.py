"""
مدير النسخ الاحتياطي - Backup Manager
يوفر نسخ احتياطي يدوي وتلقائي مع إمكانية الاستعادة
"""

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta


class BackupManager:
    """مدير النسخ الاحتياطي لقاعدة البيانات ومجلد الوثائق"""

    # المجلد الافتراضي للنسخ الاحتياطية
    DEFAULT_BACKUP_DIR = Path.home() / "Documents" / "ArchiveBackups"
    BACKUP_PREFIX = "backup_"
    BACKUP_EXTENSION = ".zip"
    AUTO_BACKUP_INTERVAL_DAYS = 7

    def __init__(self, backup_dir=None):
        """
        Args:
            backup_dir: مسار مجلد النسخ الاحتياطية (اختياري)
        """
        self.backup_dir = Path(backup_dir) if backup_dir else self.DEFAULT_BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, db_path, documents_dir):
        """
        إنشاء نسخة احتياطية مضغوطة تحتوي على قاعدة البيانات ومجلد الوثائق
        
        Args:
            db_path: مسار ملف قاعدة البيانات
            documents_dir: مسار مجلد الوثائق
        
        Returns:
            tuple: (success: bool, message: str, zip_path: str | None)
        """
        try:
            db_path = Path(db_path).resolve()
            documents_dir = Path(documents_dir).resolve()

            if not db_path.exists():
                return False, f"ملف قاعدة البيانات غير موجود: {db_path}", None

            # اسم ملف النسخة الاحتياطية
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"{self.BACKUP_PREFIX}{timestamp}{self.BACKUP_EXTENSION}"
            zip_path = self.backup_dir / zip_filename

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # إضافة قاعدة البيانات
                zipf.write(db_path, db_path.name)

                # إضافة مجلد الوثائق
                if documents_dir.exists():
                    for root, dirs, files in os.walk(documents_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = str(
                                Path("documents") / file_path.relative_to(documents_dir)
                            )
                            zipf.write(file_path, arcname)

            # حجم الملف بصيغة مقروءة
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            return (
                True,
                f"تم إنشاء النسخة الاحتياطية بنجاح\n"
                f"📁 المسار: {zip_path}\n"
                f"📦 الحجم: {size_mb:.1f} ميجابايت",
                str(zip_path),
            )

        except Exception as e:
            return False, f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}", None

    def restore_backup(self, zip_path, db_path, documents_dir):
        """
        استعادة نسخة احتياطية من ملف ZIP
        
        Args:
            zip_path: مسار ملف ZIP
            db_path: مسار ملف قاعدة البيانات المراد استبداله
            documents_dir: مسار مجلد الوثائق المراد استبداله
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            zip_path = Path(zip_path)
            db_path = Path(db_path).resolve()
            documents_dir = Path(documents_dir).resolve()

            if not zip_path.exists():
                return False, "ملف النسخة الاحتياطية غير موجود"

            if not zipfile.is_zipfile(zip_path):
                return False, "الملف المحدد ليس ملف ZIP صالح"

            # التحقق من محتويات الأرشيف
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                names = zipf.namelist()
                has_db = any(n.endswith('.db') for n in names)
                if not has_db:
                    return False, "النسخة الاحتياطية لا تحتوي على قاعدة بيانات"

            # إنشاء نسخة احتياطية من الحالة الحالية قبل الاستعادة
            pre_restore_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_name = f"pre_restore_{pre_restore_timestamp}{self.BACKUP_EXTENSION}"
            pre_restore_path = self.backup_dir / pre_restore_name

            try:
                self.create_backup(str(db_path), str(documents_dir))
            except Exception:
                pass  # إذا فشلت النسخة الاحتياطية المسبقة، نتابع

            # استخراج محتويات الأرشيف إلى مجلد مؤقت
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zipf.extractall(temp_path)

                # استعادة قاعدة البيانات
                for item in temp_path.iterdir():
                    if item.suffix == '.db':
                        shutil.copy2(item, db_path)
                        break

                # استعادة مجلد الوثائق
                temp_docs = temp_path / "documents"
                if temp_docs.exists():
                    # حذف المجلد الحالي واستبداله
                    if documents_dir.exists():
                        shutil.rmtree(documents_dir)
                    shutil.copytree(temp_docs, documents_dir)

            return True, "تم استعادة النسخة الاحتياطية بنجاح ✅\nيجب إعادة تشغيل البرنامج"

        except Exception as e:
            return False, f"خطأ في استعادة النسخة الاحتياطية: {str(e)}"

    def get_last_backup_date(self):
        """
        الحصول على تاريخ آخر نسخة احتياطية
        
        Returns:
            datetime | None: تاريخ آخر نسخة احتياطية، أو None إذا لم توجد
        """
        backups = self.list_backups()
        if backups:
            return backups[0]['date']
        return None

    def should_auto_backup(self):
        """
        التحقق مما إذا كان يجب إنشاء نسخة احتياطية تلقائية
        
        Returns:
            bool: True إذا مضى أكثر من 7 أيام على آخر نسخة
        """
        last_date = self.get_last_backup_date()
        if last_date is None:
            return True

        days_since = (datetime.now() - last_date).days
        return days_since >= self.AUTO_BACKUP_INTERVAL_DAYS

    def list_backups(self):
        """
        سرد جميع النسخ الاحتياطية المتاحة
        
        Returns:
            list[dict]: قائمة بالنسخ الاحتياطية مرتبة من الأحدث للأقدم
                كل عنصر يحتوي على: path, filename, date, size_mb
        """
        backups = []

        if not self.backup_dir.exists():
            return backups

        for f in self.backup_dir.iterdir():
            if f.suffix == self.BACKUP_EXTENSION and f.name.startswith(self.BACKUP_PREFIX):
                try:
                    # استخراج التاريخ من اسم الملف
                    date_str = f.stem.replace(self.BACKUP_PREFIX, "").replace("pre_restore_", "")
                    backup_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                    size_mb = f.stat().st_size / (1024 * 1024)

                    backups.append({
                        'path': str(f),
                        'filename': f.name,
                        'date': backup_date,
                        'size_mb': round(size_mb, 1),
                    })
                except (ValueError, OSError):
                    continue

        # ترتيب من الأحدث للأقدم
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups
