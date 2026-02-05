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
    
    # ألوان أساسية - Primary Colors
    PRIMARY = "#696969"           # رمادي داكن - اللون الأساسي
    PRIMARY_DARK = "#505050"      # رمادي أغمق
    PRIMARY_LIGHT = "#808080"     # رمادي فاتح
    
    # ألوان ثانوية - Secondary Colors  
    SECONDARY = "#a9a9a9"         # رمادي متوسط
    SECONDARY_DARK = "#808080"    # رمادي غامق
    SECONDARY_LIGHT = "#c0c0c0"   # رمادي فاتح جداً
    
    # ألوان الخلفية - Background Colors
    BACKGROUND = "#e8e8e8"        # خلفية رئيسية
    BACKGROUND_DARK = "#ee3"   # خلفية داكنة  check usage and correct
    BACKGROUND_LIGHT = "#f5f5f5"  # خلفية فاتحة
    BACKGROUND_WHITE = "#ffffff"  # أبيض
    
    # ألوان النص - Text Colors
    TEXT_PRIMARY = "#333333"      # نص أساسي
    TEXT_SECONDARY = "#666666"    # نص ثانوي
    TEXT_MUTED = "#999999"        # نص خافت
    TEXT_WHITE = "#ffffff"        # نص أبيض
    
    # ألوان الحدود - Border Colors
    BORDER = "#999999"            # حدود عادية
    BORDER_LIGHT = "#d3d3d3"      # حدود فاتحة
    BORDER_DARK = "#696969"       # حدود داكنة
    
    # ألوان الحالة - Status Colors
    SUCCESS = "#27ae60"           # نجاح (أخضر)
    SUCCESS_LIGHT = "#eafaf1"     # خلفية نجاح
    WARNING = "#e67e22"           # تحذير (برتقالي)
    WARNING_LIGHT = "#fef9e7"     # خلفية تحذير
    ERROR = "#e74c3c"             # خطأ (أحمر)
    ERROR_LIGHT = "#fdf2f2"       # خلفية خطأ
    INFO = "#3498db"              # معلومات (أزرق)
    INFO_LIGHT = "#ebf5fb"        # خلفية معلومات
    
    # ألوان خاصة - Special Colors
    HEADER_BG = "#D9E1F2"         # خلفية الجداول (أزرق فاتح)
    ACCENT = "#2c3e50"            # لون التمييز (أزرق داكن)
    LINK = "#2980b9"              # روابط
    
    # ألوان الأزرار الخاصة - Special Button Colors
    BUTTON_PURPLE = "#9b59b6"     # زر بنفسجي (طباعة)
    BUTTON_GREEN = "#27ae60"      # زر أخضر (تصدير Excel)
    BUTTON_BLUE = "#3498db"       # زر أزرق (تصدير Word)


# =============================================================================
# أحجام الخطوط - Font Sizes
# =============================================================================

@dataclass(frozen=True)
class FontSizes:
    """أحجام الخطوط بالبكسل"""
    
    # أحجام العناوين
    TITLE_LARGE = 18              # عنوان كبير
    TITLE = 16                    # عنوان عادي
    TITLE_SMALL = 14              # عنوان صغير
    
    # أحجام النص
    BODY = 12                     # نص عادي
    BODY_SMALL = 11               # نص صغير
    CAPTION = 10                  # تعليق
    SMALL = 9                     # صغير جداً
    TINY = 7                      # صغير للغاية (للجداول)
    
    # أحجام خاصة
    BUTTON = 14                   # أزرار
    INPUT = 12                    # حقول الإدخال
    TABLE_HEADER = 11             # رأس الجدول
    TABLE_CELL = 10               # خلايا الجدول


# =============================================================================
# عائلات الخطوط - Font Families
# =============================================================================

@dataclass(frozen=True)
class FontFamilies:
    """عائلات الخطوط المستخدمة"""
    
    # الخط الافتراضي
    DEFAULT = "Arial"
    
    # خطوط عربية
    ARABIC = "Arial"              # يدعم العربية
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
    MARGIN_SMALL = 5
    MARGIN_MEDIUM = 10
    MARGIN_LARGE = 15
    MARGIN_XLARGE = 20
    
    # الحشو - Padding
    PADDING_SMALL = 3
    PADDING_MEDIUM = 6
    PADDING_LARGE = 10
    PADDING_XLARGE = 15
    
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
    INPUT_HEIGHT = 28
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
