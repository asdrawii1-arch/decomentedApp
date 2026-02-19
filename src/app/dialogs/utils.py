"""
دوال مساعدة للنوافذ الحوارية
Utility functions for dialogs
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import QInputDialog, QMessageBox


def choose_year_folder(parent):
    """
    دالة مساعدة لعرض مجلدات السنوات الموجودة أو إنشاء مجلد سنة جديدة.
    
    Args:
        parent: النافذة الأب
    
    Returns:
        str | None: المسار كسلسلة أو None إذا ألغاها المستخدم
    """
    documents_path = Path('documents')
    documents_path.mkdir(exist_ok=True)
    
    # الحصول على قائمة السنوات الموجودة
    years = sorted(
        [f.name for f in documents_path.iterdir() if f.is_dir() and f.name.isdigit()],
        reverse=True
    )
    
    # عرض قائمة الاختيار
    year, ok = QInputDialog.getItem(
        parent, 
        'اختر السنة', 
        'السنة:', 
        years + ['سنة جديدة...'], 
        0, 
        False
    )
    
    if not ok:
        return None
    
    if year == 'سنة جديدة...':
        # إنشاء سنة جديدة
        new_year, ok2 = QInputDialog.getText(parent, 'سنة جديدة', 'أدخل السنة:')
        if ok2 and new_year.isdigit():
            year_folder = documents_path / new_year
            year_folder.mkdir(exist_ok=True)
            QMessageBox.information(
                parent, 
                'مجلد السنة', 
                f'تم إنشاء/اختيار مجلد السنة: {year_folder}'
            )
            return str(year_folder)
        else:
            return None
    else:
        year_folder = documents_path / year
        QMessageBox.information(
            parent, 
            'مجلد السنة', 
            f'المجلد المختار: {year_folder}'
        )
        return str(year_folder)
