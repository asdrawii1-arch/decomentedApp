"""أنماط واجهة المستخدم بالألوان الرمادية"""

MAIN_STYLESHEET = """
    QMainWindow {
        background-color: #e8e8e8;
    }
    
    QWidget {
        background-color: #e8e8e8;
        color: #333333;
    }
    
    QMenuBar {
        background-color: #d3d3d3;
        color: #333333;
        border: 1px solid #999999;
    }
    
    QMenuBar::item:selected {
        background-color: #a9a9a9;
    }
    
    QMenu {
        background-color: #d3d3d3;
        color: #333333;
        border: 1px solid #999999;
    }
    
    QMenu::item:selected {
        background-color: #a9a9a9;
    }
    
    QToolBar {
        background-color: #d3d3d3;
        border: 1px solid #999999;
        spacing: 3px;
    }
    
    QLineEdit {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #999999;
        border-radius: 3px;
        padding: 5px;
    }
    
    QLineEdit:focus {
        border: 2px solid #696969;
        background-color: #ffffff;
    }
    
    QTextEdit {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #999999;
        border-radius: 3px;
    }
    
    QTextEdit:focus {
        border: 2px solid #696969;
    }
    
    QComboBox {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #999999;
        border-radius: 3px;
        padding: 5px;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #333333;
        selection-background-color: #a9a9a9;
    }
    
    QPushButton {
        background-color: #a9a9a9;
        color: #ffffff;
        border: 1px solid #696969;
        border-radius: 3px;
        padding: 6px 12px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #808080;
    }
    
    QPushButton:pressed {
        background-color: #696969;
    }
    
    QPushButton:disabled {
        background-color: #d3d3d3;
        color: #999999;
    }
    
    QTableWidget {
        background-color: #ffffff;
        alternate-background-color: #f5f5f5;
        gridline-color: #d3d3d3;
        border: 1px solid #999999;
    }
    
    QTableWidget::item:selected {
        background-color: #a9a9a9;
        color: #ffffff;
    }
    
    QHeaderView::section {
        background-color: #d3d3d3;
        color: #333333;
        padding: 5px;
        border: 1px solid #999999;
    }
    
    QScrollBar:vertical {
        background-color: #e8e8e8;
        width: 12px;
        border: 1px solid #999999;
    }
    
    QScrollBar::handle:vertical {
        background-color: #a9a9a9;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #808080;
    }
    
    QScrollBar:horizontal {
        background-color: #e8e8e8;
        height: 12px;
        border: 1px solid #999999;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #a9a9a9;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #808080;
    }
    
    QGroupBox {
        color: #333333;
        border: 2px solid #999999;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }
    
    QLabel {
        color: #333333;
    }
    
    QDialog {
        background-color: #e8e8e8;
    }
    
    QSpinBox, QDoubleSpinBox {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #999999;
        border-radius: 3px;
        padding: 5px;
    }
    
    QCheckBox {
        color: #333333;
        spacing: 5px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
    }
    
    QCheckBox::indicator:unchecked {
        background-color: #ffffff;
        border: 1px solid #999999;
        border-radius: 2px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #a9a9a9;
        border: 1px solid #696969;
        border-radius: 2px;
    }
    
    QRadioButton {
        color: #333333;
        spacing: 5px;
    }
    
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
    }
"""

# الألوان المستخدمة
COLORS = {
    'background': '#e8e8e8',
    'dark_gray': '#a9a9a9',
    'light_gray': '#d3d3d3',
    'white': '#ffffff',
    'black': '#333333',
    'border': '#999999',
    'dark_border': '#696969',
}

# قياسات معيارية
SIZES = {
    'button_height': 40,
    'input_height': 35,
    'icon_size': 24,
    'large_icon': 32,
    'border_radius': 3,
}
