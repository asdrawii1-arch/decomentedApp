"""
ثوابت التطبيق والتصميم
Application Constants and Design Tokens

يحتوي هذا الملف على جميع الثوابت المستخدمة في التطبيق:
- الألوان (Colors)
- أحجام الخطوط (Font Sizes)
- عائلات الخطوط (Font Families)
- الأبعاد والمقاسات (Dimensions)
- الأيقونات والرموز (Icons/Emojis)
"""

from dataclasses import dataclass
from typing import Dict


# =============================================================================
# الألوان - Colors
# =============================================================================

@dataclass(frozen=True)
class Colors:
    """ثوابت الألوان المستخدمة في التطبيق"""
    
    # Primary Colors - Enhanced modern palette
    PRIMARY = "#ffffff"           # pure white primary surface
    PRIMARY_DARK = "#f1f5f9"      # light gray for subtle surfaces
    PRIMARY_LIGHT = "#fefefe"     # slightly off-white for depth

    # Secondary tones for panels and surfaces
    SECONDARY = "#e2e8f0"         # refined light gray
    SECONDARY_DARK = "#cbd5e1"    # medium gray
    SECONDARY_LIGHT = "#f8fafc"   # very light gray

    # Backgrounds
    BACKGROUND = "#f8fafc"        # app main background (very light)
    BACKGROUND_DARK = "#e2e8f0"   # toolbar / elevated surface - darker for contrast
    BACKGROUND_LIGHT = "#ffffff"  # panel background (white)
    BACKGROUND_WHITE = "#ffffff"  # explicit white surface

    # Text - Enhanced contrast for better readability
    TEXT_PRIMARY = "#1e293b"      # darker primary text (slate 800)
    TEXT_SECONDARY = "#475569"    # secondary text (slate 600)
    TEXT_MUTED = "#64748b"        # muted text (slate 500)
    TEXT_WHITE = "#ffffff"        # white
    TEXT_CONTRAST = "#0f172a"     # maximum contrast dark (slate 900)

    # Borders - Refined for better definition
    BORDER = "#d1d5db"           # more visible border (gray 300)
    BORDER_LIGHT = "#e5e7eb"     # light border (gray 200)
    BORDER_DARK = "#9ca3af"      # dark border (gray 400)
    
    # Status Colors - Enhanced visibility
    SUCCESS = "#059669"           # نجاح (emerald 600)
    SUCCESS_LIGHT = "#d1fae5"     # خلفية نجاح (emerald 100)
    WARNING = "#d97706"           # تحذير (amber 600)
    WARNING_LIGHT = "#fef3c7"     # خلفية تحذير (amber 100)
    ERROR = "#dc2626"             # خطأ (red 600)
    ERROR_LIGHT = "#fee2e2"       # خلفية خطأ (red 100)
    INFO = "#0284c7"              # info blue (sky 600)
    INFO_LIGHT = "#e0f2fe"        # subtle info surface (sky 50)

    # Special Colors - Enhanced for better UX
    HEADER_BG = "#f1f5f9"         # table header (refined)
    ACCENT = "#3b82f6"            # modern blue accent (blue 500)
    LINK = "#2563eb"              # link blue (blue 600)
    
    # Table Selection - Improved readability
    SELECTION_BG = "#dbeafe"      # light blue selection (blue 100)
    SELECTION_TEXT = "#1e293b"    # dark text for selection (slate 800)
    HOVER_BG = "#f1f5f9"          # subtle hover (slate 50)

    # Button Colors - Refined palette
    BUTTON_PURPLE = "#7c3aed"     # violet 600
    BUTTON_GREEN = "#059669"      # emerald 600
    BUTTON_BLUE = "#3b82f6"       # blue 500


# =============================================================================
# أحجام الخطوط - Font Sizes
# =============================================================================

@dataclass(frozen=True)
class FontSizes:
    """أحجام الخطوط بالبكسل - Enhanced for better readability"""
    
    # أحجام العناوين
    TITLE_LARGE = 20              # عنوان كبير (increased)
    TITLE = 18                    # عنوان عادي (increased)
    TITLE_SMALL = 16              # عنوان صغير (increased)
    
    # أحجام النص - Enhanced for readability
    BODY = 14                     # نص عادي
    BODY_SMALL = 12               # نص صغير (increased from 11)
    CAPTION = 11                  # تعليق (increased from 10)
    SMALL = 10                    # صغير (increased from 9)
    TINY = 8                      # صغير للغاية (increased from 7)
    
    # أحجام خاصة - Enhanced
    BUTTON = 14                   # أزرار
    INPUT = 13                    # حقول الإدخال (increased)
    TABLE_HEADER = 13             # رأس الجدول (increased from 11)
    TABLE_CELL = 12               # خلايا الجدول (increased from 10)


# =============================================================================
# عائلات الخطوط - Font Families
# =============================================================================

@dataclass(frozen=True)
class FontFamilies:
    """عائلات الخطوط المستخدمة"""
    
    # الخط الافتراضي
    DEFAULT = "Segoe UI"

    # خطوط عربية
    ARABIC = "Segoe UI"           # يدعم العربية
    ARABIC_ALT = "Tahoma"         # بديل عربي
    
    # خطوط أحادية المسافة (للكود)
    MONOSPACE = "Consolas"
    
    # خطوط النظام
    SYSTEM = "system-ui"


# =============================================================================
# الأبعاد والمقاسات - Dimensions
# =============================================================================

@dataclass(frozen=True)
class Dimensions:
    """الأبعاد والمقاسات بالبكسل"""
    
    # الهوامش - Margins
    MARGIN_SMALL = 6
    MARGIN_MEDIUM = 12
    MARGIN_LARGE = 18
    MARGIN_XLARGE = 24
    
    # الحشو - Padding
    PADDING_SMALL = 6
    PADDING_MEDIUM = 10
    PADDING_LARGE = 14
    PADDING_XLARGE = 20
    
    # الحدود - Borders
    BORDER_RADIUS_SMALL = 2
    BORDER_RADIUS_MEDIUM = 3
    BORDER_RADIUS_LARGE = 5
    BORDER_WIDTH = 1
    BORDER_WIDTH_FOCUS = 2
    
    # أحجام النوافذ - Window Sizes
    DIALOG_WIDTH_SMALL = 400
    DIALOG_WIDTH_MEDIUM = 600
    DIALOG_WIDTH_LARGE = 900
    DIALOG_HEIGHT_SMALL = 300
    DIALOG_HEIGHT_MEDIUM = 500
    DIALOG_HEIGHT_LARGE = 700
    
    # أحجام العناصر - Element Sizes
    BUTTON_HEIGHT = 32
    INPUT_HEIGHT = 34
    ROW_HEIGHT = 25
    THUMBNAIL_WIDTH = 150
    THUMBNAIL_HEIGHT = 200
    PREVIEW_WIDTH = 380
    PREVIEW_HEIGHT = 480
    
    # أعمدة الجدول - Table Columns
    TABLE_COL_CHECKBOX = 40
    TABLE_COL_SMALL = 80
    TABLE_COL_MEDIUM = 100
    TABLE_COL_LARGE = 150
    TABLE_COL_XLARGE = 200
    
    # الصفحات والطباعة
    ROWS_PER_PAGE = 25


# =============================================================================
# الأيقونات والرموز - Icons & Emojis
# =============================================================================

@dataclass(frozen=True)
class Icons:
    """الأيقونات والرموز المستخدمة في الواجهة"""
    
    # أيقونات الإجراءات
    ADD = "➕"
    DELETE = "🗑️"
    EDIT = "✏️"
    VIEW = "👁️"
    SAVE = "💾"
    CANCEL = "❌"
    CONFIRM = "✅"
    REFRESH = "🔄"
    
    # أيقونات الملفات
    FOLDER = "📂"
    FILE = "📄"
    IMAGE = "🖼️"
    ATTACHMENT = "📎"
    DOCUMENT = "📋"
    
    # أيقونات العمليات
    SCAN_SINGLE = "📷"
    SCAN_MULTIPLE = "📚"
    SEARCH = "🔍"
    IMPORT = "📁"
    EXPORT = "📤"
    PRINT = "🖨️"
    
    # أيقونات الحالة
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    INFO = "ℹ️"
    LOADING = "⏳"
    
    # أيقونات التنقل
    PREVIOUS = "⏮️"
    NEXT = "⏭️"
    UP = "⬆️"
    DOWN = "⬇️"
    
    # أيقونات أخرى
    EXCEL = "📊"
    WORD = "📄"
    CHECKBOX = "☑"
    SELECT_ALL = "✓"


# =============================================================================
# نصوص الرسائل - Message Texts
# =============================================================================

@dataclass(frozen=True)
class Messages:
    """نصوص الرسائل المستخدمة في التطبيق"""
    
    # رسائل النجاح
    SAVE_SUCCESS = "تم الحفظ بنجاح ✅"
    DELETE_SUCCESS = "تم الحذف بنجاح"
    IMPORT_SUCCESS = "تم الاستيراد بنجاح"
    
    # رسائل التحذير
    SELECT_DOCUMENT = "يجب اختيار وثيقة أولاً"
    SELECT_YEAR = "يجب اختيار أو إنشاء مجلد سنة"
    ENTER_DOC_NAME = "يجب إدخال اسم الوثيقة"
    
    # رسائل الخطأ
    SCANNER_NOT_AVAILABLE = "مكتبة السكانر (pywin32) غير مثبتة"
    SCANNER_NOT_CONNECTED = "لا يوجد سكانر متصل بالحاسب"
    FILE_NOT_FOUND = "لا يمكن العثور على الملف"
    
    # رسائل التأكيد
    CONFIRM_DELETE = "هل أنت متأكد من الحذف؟"
    CONFIRM_DELETE_MULTIPLE = "هل أنت متأكد من حذف {} وثيقة؟"


# =============================================================================
# إعدادات التطبيق - App Settings
# =============================================================================

@dataclass(frozen=True)
class AppSettings:
    """إعدادات التطبيق"""
    
    # اسم التطبيق
    APP_NAME = "برنامج أرشفة الكتب الرسمية"
    APP_VERSION = "1.0.0"
    
    # مجلدات التخزين
    DOCUMENTS_DIR = "documents"
    DATABASE_NAME = "documents.db"
    
    # إعدادات الصور
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif', '.webp']
    THUMBNAIL_SIZE = (150, 200)
    PREVIEW_SIZE = (380, 480)
    
    # إعدادات OCR
    OCR_LANGUAGES = ['ar', 'en']
    
    # جهات الإصدار الافتراضية
    DEFAULT_DEPARTMENTS = [
        'اختر جهة الإصدار',
        'شعبة أمن الأفراد عنة',
        'قسم أمن الأفراد الأنبار'
    ]


# =============================================================================
# دوال مساعدة - Helper Functions
# =============================================================================

def get_status_style(status: str) -> str:
    """
    الحصول على نمط CSS بناءً على الحالة
    
    Args:
        status: نوع الحالة ('success', 'warning', 'error', 'info')
    
    Returns:
        str: نمط CSS
    """
    styles = {
        'success': f'color: {Colors.SUCCESS}; background-color: {Colors.SUCCESS_LIGHT};',
        'warning': f'color: {Colors.WARNING}; background-color: {Colors.WARNING_LIGHT};',
        'error': f'color: {Colors.ERROR}; background-color: {Colors.ERROR_LIGHT};',
        'info': f'color: {Colors.INFO}; background-color: {Colors.INFO_LIGHT};',
    }
    return styles.get(status, '')


def get_button_style(color: str) -> str:
    """
    الحصول على نمط زر مخصص
    
    Args:
        color: لون الزر (من Colors)
    
    Returns:
        str: نمط CSS للزر
    """
    return f'''
        background-color: {color}; 
        color: {Colors.TEXT_WHITE}; 
        padding: {Dimensions.PADDING_LARGE}px; 
        font-size: {FontSizes.BUTTON}px;
        border-radius: {Dimensions.BORDER_RADIUS_MEDIUM}px;
    '''


# تصدير الثوابت للاستخدام المباشر
COLORS = Colors()
FONT_SIZES = FontSizes()
FONT_FAMILIES = FontFamilies()
DIMENSIONS = Dimensions()
ICONS = Icons()
MESSAGES = Messages()
APP_SETTINGS = AppSettings()
