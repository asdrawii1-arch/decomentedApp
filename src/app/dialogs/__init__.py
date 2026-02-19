"""
نوافذ الحوار - Dialogs Module
حزمة تحتوي على جميع نوافذ الحوار المستخدمة في التطبيق
"""

from .add_document_dialog import AddDocumentDialog
from .attachment_details_dialog import AttachmentDetailsDialog
from .import_images_dialog import ImportImagesDialog
from .destruction_form_dialog import DestructionFormDialog

__all__ = [
    'AddDocumentDialog',
    'AttachmentDetailsDialog', 
    'ImportImagesDialog',
    'DestructionFormDialog'
]
