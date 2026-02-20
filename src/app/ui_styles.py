"""
أنماط واجهة المستخدم
UI Styles Module

يحتوي على الأنماط الرئيسية للتطبيق باستخدام الثوابت من constants.py
"""

from .constants import COLORS, FONT_SIZES, DIMENSIONS

# =============================================================================
# ورقة الأنماط الرئيسية - Main Stylesheet
# =============================================================================

MAIN_STYLESHEET = f"""
    /* النافذة الرئيسية */
    QMainWindow {{
        background-color: {COLORS.BACKGROUND};
    }}

    /* عناصر الواجهة العامة - خطوط وحدود ألوان محدثة */
    QWidget {{
        background-color: {COLORS.BACKGROUND};
        color: {COLORS.TEXT_PRIMARY};
        font-family: 'Segoe UI', 'Tahoma', Arial, sans-serif;
        font-size: {FONT_SIZES.BODY}px;
        font-weight: 400;
    }}
    
    /* شريط القوائم */
    QMenuBar {{
        background-color: {COLORS.BACKGROUND_DARK};
        color: {COLORS.TEXT_PRIMARY};
        border: 1px solid {COLORS.BORDER};
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS.SECONDARY};
    }}
    
    QMenu {{
        background-color: {COLORS.BACKGROUND_DARK};
        color: {COLORS.TEXT_PRIMARY};
        border: 1px solid {COLORS.BORDER};
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS.SECONDARY};
    }}
    
    /* شريط الأدوات */
    QToolBar {{
        background-color: {COLORS.BACKGROUND_DARK};
        border: 1px solid {COLORS.BORDER};
        spacing: 6px;
    }}
    
    /* حقول الإدخال - محسّنة للوضوح */
    QLineEdit {{
        background-color: {COLORS.BACKGROUND_WHITE};
        color: {COLORS.TEXT_PRIMARY};
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
        padding: {DIMENSIONS.PADDING_MEDIUM}px;
        font-size: {FONT_SIZES.INPUT}px;
        selection-background-color: {COLORS.SELECTION_BG};
        selection-color: {COLORS.SELECTION_TEXT};
    }}
    
    QLineEdit:focus {{
        border: {DIMENSIONS.BORDER_WIDTH_FOCUS}px solid {COLORS.ACCENT};
        background-color: {COLORS.BACKGROUND_WHITE};
        outline: none;
    }}
    
    QLineEdit:hover {{
        border-color: {COLORS.BORDER_DARK};
    }}
    
    /* محرر النص */
    QTextEdit {{
        background-color: {COLORS.BACKGROUND_WHITE};
        color: {COLORS.TEXT_PRIMARY};
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    }}
    
    QTextEdit:focus {{
        border: {DIMENSIONS.BORDER_WIDTH_FOCUS}px solid {COLORS.BORDER_DARK};
    }}
    
    /* القوائم المنسدلة - محسّنة */
    QComboBox {{
        background-color: {COLORS.BACKGROUND_WHITE};
        color: {COLORS.TEXT_PRIMARY};
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
        padding: {DIMENSIONS.PADDING_MEDIUM}px;
        min-width: 120px;
        font-size: {FONT_SIZES.INPUT}px;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS.BORDER_DARK};
        background-color: {COLORS.HOVER_BG};
    }}
    
    QComboBox:focus {{
        border: {DIMENSIONS.BORDER_WIDTH_FOCUS}px solid {COLORS.ACCENT};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 25px;
        border-left: 1px solid {COLORS.BORDER};
        border-top-right-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
        border-bottom-right-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
        background-color: {COLORS.SECONDARY};
    }}
    
    QComboBox::down-arrow {{
        width: 12px;
        height: 12px;
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid {COLORS.TEXT_SECONDARY};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS.BACKGROUND_WHITE};
        color: {COLORS.TEXT_PRIMARY};
        selection-background-color: {COLORS.SELECTION_BG};
        selection-color: {COLORS.SELECTION_TEXT};
        border: 1px solid {COLORS.BORDER_DARK};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    }}
    
    /* الأزرار - محسّنة */
    QPushButton {{
        background-color: {COLORS.ACCENT};
        color: {COLORS.TEXT_WHITE};
        border: 1px solid {COLORS.ACCENT};
        border-radius: {DIMENSIONS.BORDER_RADIUS_LARGE}px;
        padding: {DIMENSIONS.PADDING_MEDIUM}px {DIMENSIONS.PADDING_LARGE}px;
        font-weight: 600;
        font-size: {FONT_SIZES.BUTTON}px;
        min-height: {DIMENSIONS.BUTTON_HEIGHT}px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS.BUTTON_BLUE};
        border-color: {COLORS.BUTTON_BLUE};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS.BUTTON_BLUE};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS.BACKGROUND_DARK};
        color: {COLORS.TEXT_MUTED};
        border-color: {COLORS.BORDER};
    }}
    
    /* الجداول - محسّنة لقابلية القراءة */
    QTableWidget {{
        background-color: {COLORS.BACKGROUND_WHITE};
        alternate-background-color: {COLORS.BACKGROUND_LIGHT};
        gridline-color: {COLORS.BORDER_LIGHT};
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
        font-size: {FONT_SIZES.TABLE_CELL}px;
        selection-background-color: {COLORS.SELECTION_BG};
        selection-color: {COLORS.SELECTION_TEXT};
    }}
    
    /* تحديد الصفوف - قابلية قراءة محسّنة */
    QTableWidget::item:selected {{
        background-color: {COLORS.SELECTION_BG};
        color: {COLORS.SELECTION_TEXT};
        border: none;
    }}
    
    QTableWidget::item:hover {{
        background-color: {COLORS.HOVER_BG};
        color: {COLORS.TEXT_PRIMARY};
    }}
    
    /* تحديد عدة صفوف */
    QTableWidget::item:selected:focus {{
        background-color: {COLORS.SELECTION_BG};
        color: {COLORS.SELECTION_TEXT};
        border: 1px solid {COLORS.ACCENT};
    }}
    
    /* خلايا الجدول */
    QTableWidget::item {{
        padding: 8px 12px;
        border: none;
        font-size: {FONT_SIZES.TABLE_CELL}px;
        color: {COLORS.TEXT_PRIMARY};
    }}
    
    /* رأس الجدول - محسّن */
    QHeaderView::section {{
        background-color: {COLORS.HEADER_BG};
        color: {COLORS.TEXT_PRIMARY};
        padding: {DIMENSIONS.PADDING_MEDIUM}px;
        border: 1px solid {COLORS.BORDER};
        font-weight: 600;
        font-size: {FONT_SIZES.TABLE_HEADER}px;
        border-bottom: 2px solid {COLORS.BORDER_DARK};
    }}
    
    QHeaderView::section:hover {{
        background-color: {COLORS.SECONDARY};
    }}
    
    /* أشرطة التمرير العمودية */
    QScrollBar:vertical {{
        background-color: {COLORS.BACKGROUND};
        width: 12px;
        border: 1px solid {COLORS.BORDER};
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS.SECONDARY};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS.PRIMARY_LIGHT};
    }}
    
    /* أشرطة التمرير الأفقية */
    QScrollBar:horizontal {{
        background-color: {COLORS.BACKGROUND};
        height: 12px;
        border: 1px solid {COLORS.BORDER};
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS.SECONDARY};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS.PRIMARY_LIGHT};
    }}
    
    /* مجموعات العناصر */
    QGroupBox {{
        color: {COLORS.TEXT_PRIMARY};
        border: 2px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_LARGE}px;
        margin-top: {DIMENSIONS.MARGIN_MEDIUM}px;
        padding-top: {DIMENSIONS.MARGIN_MEDIUM}px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: {DIMENSIONS.MARGIN_MEDIUM}px;
        padding: 0 3px 0 3px;
    }}
    
    /* التسميات */
    QLabel {{
        color: {COLORS.TEXT_PRIMARY};
    }}
    
    /* النوافذ الحوارية */
    QDialog {{
        background-color: {COLORS.BACKGROUND};
    }}
    
    /* حقول الأرقام */
    QSpinBox, QDoubleSpinBox {{
        background-color: {COLORS.BACKGROUND_WHITE};
        color: {COLORS.TEXT_PRIMARY};
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
        padding: {DIMENSIONS.PADDING_MEDIUM}px;
    }}
    
    /* خانات الاختيار */
    QCheckBox {{
        color: {COLORS.TEXT_PRIMARY};
        spacing: 5px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
    }}
    
    QCheckBox::indicator:unchecked {{
        background-color: {COLORS.BACKGROUND_WHITE};
        border: 1px solid {COLORS.BORDER};
        border-radius: 2px;
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS.PRIMARY};
        border: 1px solid {COLORS.PRIMARY};
        border-radius: 2px;
    }}
    
    /* شريط التقدم */
    QProgressBar {{
        background-color: {COLORS.BACKGROUND_LIGHT};
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS.SUCCESS};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    }}
    
    /* القوائم */
    QListWidget {{
        background-color: {COLORS.BACKGROUND_WHITE};
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    }}
    
    QListWidget::item:selected {{
        background-color: {COLORS.ACCENT};
        color: {COLORS.TEXT_WHITE};
    }}
    
    QListWidget::item:hover {{
        background-color: {COLORS.BACKGROUND_LIGHT};
    }}
    
    /* التبويبات */
    QTabWidget::pane {{
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    }}
    
    QTabBar::tab {{
        background-color: {COLORS.BACKGROUND_DARK};
        color: {COLORS.TEXT_PRIMARY};
        padding: {DIMENSIONS.PADDING_MEDIUM}px {DIMENSIONS.PADDING_LARGE}px;
        border: 1px solid {COLORS.BORDER};
        border-bottom: none;
        border-top-left-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
        border-top-right-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS.BACKGROUND};
    }}
    
    /* نمط عصري للخانات والنوافذ الحوارية */
    QDialog {{
        background-color: {COLORS.BACKGROUND};
        border: 1px solid {COLORS.BORDER};
        border-radius: {DIMENSIONS.BORDER_RADIUS_LARGE}px;
    }}

    /* إبراز الروابط والأزرار التفاعلية */
    QLabel#linkLabel {{
        color: {COLORS.LINK};
        text-decoration: underline;
    }}
"""

# =============================================================================
# أنماط مخصصة - Custom Styles
# =============================================================================

# أنماط حالة السكانر
SCANNER_STATUS_STYLES = {
    'unavailable': f'''
        color: {COLORS.ERROR}; 
        font-size: {FONT_SIZES.BODY_SMALL}px; 
        padding: {DIMENSIONS.PADDING_MEDIUM}px; 
        background-color: {COLORS.ERROR_LIGHT}; 
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    ''',
    'disconnected': f'''
        color: {COLORS.WARNING}; 
        font-size: {FONT_SIZES.BODY_SMALL}px; 
        padding: {DIMENSIONS.PADDING_MEDIUM}px; 
        background-color: {COLORS.WARNING_LIGHT}; 
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    ''',
    'connected': f'''
        color: {COLORS.SUCCESS}; 
        font-size: {FONT_SIZES.BODY_SMALL}px; 
        padding: {DIMENSIONS.PADDING_MEDIUM}px; 
        background-color: {COLORS.SUCCESS_LIGHT}; 
        border-radius: {DIMENSIONS.BORDER_RADIUS_MEDIUM}px;
    '''
}

# أنماط الأزرار الخاصة
BUTTON_STYLES = {
    'primary': f'''
        background-color: {COLORS.PRIMARY}; 
        color: {COLORS.TEXT_WHITE}; 
        padding: {DIMENSIONS.PADDING_LARGE}px; 
        font-size: {FONT_SIZES.BUTTON}px;
    ''',
    'success': f'''
        background-color: {COLORS.SUCCESS}; 
        color: {COLORS.TEXT_WHITE}; 
        padding: {DIMENSIONS.PADDING_LARGE}px; 
        font-size: {FONT_SIZES.BUTTON}px;
    ''',
    'danger': f'''
        background-color: {COLORS.ERROR}; 
        color: {COLORS.TEXT_WHITE}; 
        padding: {DIMENSIONS.PADDING_LARGE}px; 
        font-size: {FONT_SIZES.BUTTON}px;
    ''',
    'info': f'''
        background-color: {COLORS.INFO}; 
        color: {COLORS.TEXT_WHITE}; 
        padding: {DIMENSIONS.PADDING_LARGE}px; 
        font-size: {FONT_SIZES.BUTTON}px;
    ''',
    'purple': f'''
        background-color: {COLORS.BUTTON_PURPLE}; 
        color: {COLORS.TEXT_WHITE}; 
        padding: {DIMENSIONS.PADDING_LARGE}px; 
        font-size: {FONT_SIZES.BUTTON}px;
    '''
}

# أنماط العناوين
TITLE_STYLES = {
    'large': f'''
        font-size: {FONT_SIZES.TITLE_LARGE}px; 
        font-weight: bold; 
        color: {COLORS.ACCENT}; 
        padding: {DIMENSIONS.PADDING_LARGE}px;
    ''',
    'medium': f'''
        font-size: {FONT_SIZES.TITLE}px; 
        font-weight: bold; 
        color: {COLORS.ACCENT};
    ''',
    'small': f'''
        font-size: {FONT_SIZES.TITLE_SMALL}px; 
        font-weight: bold; 
        color: {COLORS.TEXT_PRIMARY};
    '''
}

# أنماط التنقل
NAV_STYLES = {
    'position_label': f'''
        font-size: {FONT_SIZES.TITLE}px; 
        font-weight: bold; 
        color: {COLORS.LINK};
    ''',
    'nav_button': f'''
        padding: 8px; 
        font-size: {FONT_SIZES.BUTTON}px;
    '''
}

# أنماط معاينة الصور
IMAGE_PREVIEW_STYLE = f'''
    border: 2px solid {COLORS.BORDER_LIGHT}; 
    background-color: {COLORS.BACKGROUND_LIGHT};
'''

# أنماط معلومات الصفحات
PAGES_INFO_STYLE = f'''
    font-size: {FONT_SIZES.BODY}px; 
    color: {COLORS.TEXT_SECONDARY}; 
    padding: {DIMENSIONS.PADDING_MEDIUM}px;
'''

# =============================================================================
# ثوابت موروثة للتوافق - Legacy Constants (for backward compatibility)
# =============================================================================

COLORS_LEGACY = {
    'primary': COLORS.PRIMARY,
    'secondary': COLORS.SECONDARY,
    'background': COLORS.BACKGROUND,
    'text': COLORS.TEXT_PRIMARY,
    'border': COLORS.BORDER,
    'success': COLORS.SUCCESS,
    'warning': COLORS.WARNING,
    'error': COLORS.ERROR,
}

SIZES = {
    'font_small': FONT_SIZES.BODY_SMALL,
    'font_normal': FONT_SIZES.BODY,
    'font_large': FONT_SIZES.TITLE,
    'padding': DIMENSIONS.PADDING_MEDIUM,
    'margin': DIMENSIONS.MARGIN_MEDIUM,
    'border_radius': DIMENSIONS.BORDER_RADIUS_MEDIUM,
}