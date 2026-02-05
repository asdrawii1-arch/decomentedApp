"""
Windows Installer Module
وحدة تثبيت البرنامج على نظام ويندوز

تتضمن هذه الوحدة:
- نافذة معالج التثبيت
- اختيار مسار التثبيت
- إنشاء اختصار على سطح المكتب
- الكشف عن الإصدارات السابقة
"""

import os
import sys
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox, QCheckBox, QProgressBar, QWizard,
    QWizardPage, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from .constants import COLORS, FONT_SIZES, DIMENSIONS, ICONS, APP_SETTINGS


class InstallationWorker(QThread):
    """
    خيط عامل لتنفيذ عملية التثبيت في الخلفية
    Worker thread for installation process
    """
    progress_updated = pyqtSignal(int, str)
    installation_finished = pyqtSignal(bool, str)
    
    def __init__(self, source_path, install_path, create_shortcut=True, create_start_menu=True):
        super().__init__()
        self.source_path = source_path
        self.install_path = install_path
        self.create_shortcut = create_shortcut
        self.create_start_menu = create_start_menu
    
    def run(self):
        """تنفيذ عملية التثبيت"""
        try:
            # التحقق من صلاحيات الكتابة
            self.progress_updated.emit(5, "جاري التحقق من الصلاحيات...")
            
            install_dir = Path(self.install_path)
            if not install_dir.exists():
                install_dir.mkdir(parents=True, exist_ok=True)
            
            # نسخ الملفات
            self.progress_updated.emit(10, "جاري نسخ الملفات...")
            
            source_dir = Path(self.source_path)
            total_files = sum(1 for _ in source_dir.rglob('*') if _.is_file())
            copied_files = 0
            
            for item in source_dir.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(source_dir)
                    dest_path = install_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(item, dest_path)
                    copied_files += 1
                    
                    progress = 10 + int((copied_files / total_files) * 70)
                    self.progress_updated.emit(progress, f"جاري نسخ: {rel_path}")
            
            # إنشاء اختصار سطح المكتب
            if self.create_shortcut:
                self.progress_updated.emit(85, "جاري إنشاء اختصار سطح المكتب...")
                self._create_desktop_shortcut(install_dir)
            
            # إنشاء اختصار قائمة ابدأ
            if self.create_start_menu:
                self.progress_updated.emit(92, "جاري إنشاء اختصار قائمة ابدأ...")
                self._create_start_menu_shortcut(install_dir)
            
            # إنشاء ملف إلغاء التثبيت
            self.progress_updated.emit(95, "جاري إنشاء ملف إلغاء التثبيت...")
            self._create_uninstaller(install_dir)
            
            self.progress_updated.emit(100, "اكتمل التثبيت بنجاح!")
            self.installation_finished.emit(True, "تم تثبيت البرنامج بنجاح!")
            
        except PermissionError:
            self.installation_finished.emit(False, "خطأ في الصلاحيات: لا يمكن الكتابة في مسار التثبيت")
        except Exception as e:
            self.installation_finished.emit(False, f"حدث خطأ أثناء التثبيت: {str(e)}")
    
    def _create_desktop_shortcut(self, install_dir):
        """إنشاء اختصار على سطح المكتب (Windows فقط)"""
        try:
            if sys.platform == 'win32':
                import winshell
                from win32com.client import Dispatch
                
                desktop = winshell.desktop()
                shortcut_path = os.path.join(desktop, f"{APP_SETTINGS.APP_NAME}.lnk")
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = str(install_dir / "main.py")
                shortcut.WorkingDirectory = str(install_dir)
                shortcut.IconLocation = str(install_dir / "icon.ico")
                shortcut.Description = APP_SETTINGS.APP_NAME
                shortcut.save()
        except ImportError:
            # إذا لم تكن مكتبة winshell متوفرة، أنشئ اختصار بسيط
            self._create_simple_shortcut(install_dir, "Desktop")
        except Exception as e:
            print(f"تعذر إنشاء اختصار سطح المكتب: {e}")
    
    def _create_start_menu_shortcut(self, install_dir):
        """إنشاء اختصار في قائمة ابدأ (Windows فقط)"""
        try:
            if sys.platform == 'win32':
                import winshell
                from win32com.client import Dispatch
                
                start_menu = winshell.start_menu()
                program_folder = os.path.join(start_menu, "Programs", APP_SETTINGS.APP_NAME)
                os.makedirs(program_folder, exist_ok=True)
                
                shortcut_path = os.path.join(program_folder, f"{APP_SETTINGS.APP_NAME}.lnk")
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = str(install_dir / "main.py")
                shortcut.WorkingDirectory = str(install_dir)
                shortcut.IconLocation = str(install_dir / "icon.ico")
                shortcut.Description = APP_SETTINGS.APP_NAME
                shortcut.save()
        except ImportError:
            pass
        except Exception as e:
            print(f"تعذر إنشاء اختصار قائمة ابدأ: {e}")
    
    def _create_simple_shortcut(self, install_dir, location):
        """إنشاء اختصار بسيط باستخدام ملف .bat"""
        try:
            if location == "Desktop":
                shortcut_dir = Path.home() / "Desktop"
            else:
                shortcut_dir = install_dir
            
            bat_content = f'''@echo off
cd /d "{install_dir}"
python main.py
'''
            bat_path = shortcut_dir / f"{APP_SETTINGS.APP_NAME}.bat"
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
        except Exception as e:
            print(f"تعذر إنشاء الاختصار: {e}")
    
    def _create_uninstaller(self, install_dir):
        """إنشاء ملف إلغاء التثبيت"""
        uninstaller_content = f'''@echo off
echo سيتم إزالة برنامج {APP_SETTINGS.APP_NAME}
echo.
set /p confirm=هل أنت متأكد؟ (Y/N): 
if /i "%confirm%"=="Y" (
    rd /s /q "{install_dir}"
    del /q "%USERPROFILE%\\Desktop\\{APP_SETTINGS.APP_NAME}.lnk" 2>nul
    del /q "%USERPROFILE%\\Desktop\\{APP_SETTINGS.APP_NAME}.bat" 2>nul
    echo تمت إزالة البرنامج بنجاح
) else (
    echo تم إلغاء العملية
)
pause
'''
        uninstaller_path = install_dir / "uninstall.bat"
        with open(uninstaller_path, 'w', encoding='utf-8') as f:
            f.write(uninstaller_content)


class WelcomePage(QWizardPage):
    """صفحة الترحيب في معالج التثبيت"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(f"مرحباً بك في معالج تثبيت {APP_SETTINGS.APP_NAME}")
        self.setSubTitle("سيقوم هذا المعالج بإرشادك خلال عملية تثبيت البرنامج.")
        
        layout = QVBoxLayout()
        
        # معلومات البرنامج
        info_label = QLabel(f"""
        <h2>{ICONS.DOCUMENT} {APP_SETTINGS.APP_NAME}</h2>
        <p>الإصدار: {APP_SETTINGS.VERSION}</p>
        <p>برنامج متكامل لإدارة وأرشفة الوثائق والكتب الرسمية</p>
        <br>
        <p><b>المميزات:</b></p>
        <ul>
            <li>مسح الوثائق بالسكانر</li>
            <li>استخراج النصوص تلقائياً (OCR)</li>
            <li>إدارة قاعدة بيانات متكاملة</li>
            <li>استمارات إتلاف الوثائق</li>
            <li>تصدير إلى Excel و Word</li>
        </ul>
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # تحذير
        warning_label = QLabel(f"{ICONS.WARNING} يُنصح بإغلاق جميع البرامج الأخرى قبل المتابعة.")
        warning_label.setStyleSheet(f"color: {COLORS.WARNING}; padding: 10px;")
        layout.addWidget(warning_label)
        
        self.setLayout(layout)


class InstallLocationPage(QWizardPage):
    """صفحة اختيار مسار التثبيت"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("اختيار مسار التثبيت")
        self.setSubTitle("اختر المجلد الذي سيتم تثبيت البرنامج فيه.")
        
        layout = QVBoxLayout()
        
        # مسار التثبيت
        path_group = QGroupBox("مسار التثبيت")
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        default_path = str(Path.home() / "Documents" / APP_SETTINGS.APP_NAME)
        self.path_input.setText(default_path)
        self.path_input.setMinimumWidth(400)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton(f"{ICONS.FOLDER} تصفح...")
        browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(browse_btn)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # معلومات المساحة
        self.space_info = QLabel()
        self._update_space_info()
        self.path_input.textChanged.connect(self._update_space_info)
        layout.addWidget(self.space_info)
        
        # تسجيل الحقل في المعالج
        self.registerField("install_path*", self.path_input)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _browse_folder(self):
        """فتح نافذة اختيار المجلد"""
        folder = QFileDialog.getExistingDirectory(
            self, "اختر مجلد التثبيت",
            self.path_input.text()
        )
        if folder:
            self.path_input.setText(folder)
    
    def _update_space_info(self):
        """تحديث معلومات المساحة المتاحة"""
        try:
            path = Path(self.path_input.text())
            # الحصول على القرص الجذر
            while not path.exists():
                path = path.parent
                if path == path.parent:
                    break
            
            if sys.platform == 'win32':
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(str(path)),
                    None, None,
                    ctypes.pointer(free_bytes)
                )
                free_gb = free_bytes.value / (1024**3)
                self.space_info.setText(f"{ICONS.FILE} المساحة المتاحة: {free_gb:.2f} جيجابايت")
            else:
                import shutil
                total, used, free = shutil.disk_usage(path)
                free_gb = free / (1024**3)
                self.space_info.setText(f"{ICONS.FILE} المساحة المتاحة: {free_gb:.2f} جيجابايت")
        except:
            self.space_info.setText("")
    
    def validatePage(self):
        """التحقق من صحة المسار"""
        path = self.path_input.text()
        if not path:
            QMessageBox.warning(self, "خطأ", "الرجاء اختيار مسار التثبيت")
            return False
        return True


class OptionsPage(QWizardPage):
    """صفحة خيارات التثبيت الإضافية"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("خيارات التثبيت")
        self.setSubTitle("اختر الخيارات الإضافية للتثبيت.")
        
        layout = QVBoxLayout()
        
        # خيارات الاختصارات
        shortcuts_group = QGroupBox("الاختصارات")
        shortcuts_layout = QVBoxLayout()
        
        self.desktop_checkbox = QCheckBox(f"{ICONS.FILE} إنشاء اختصار على سطح المكتب")
        self.desktop_checkbox.setChecked(True)
        shortcuts_layout.addWidget(self.desktop_checkbox)
        
        self.start_menu_checkbox = QCheckBox(f"{ICONS.FOLDER} إنشاء اختصار في قائمة ابدأ")
        self.start_menu_checkbox.setChecked(True)
        shortcuts_layout.addWidget(self.start_menu_checkbox)
        
        shortcuts_group.setLayout(shortcuts_layout)
        layout.addWidget(shortcuts_group)
        
        # خيارات إضافية
        options_group = QGroupBox("خيارات إضافية")
        options_layout = QVBoxLayout()
        
        self.run_after_checkbox = QCheckBox(f"{ICONS.SUCCESS} تشغيل البرنامج بعد انتهاء التثبيت")
        self.run_after_checkbox.setChecked(True)
        options_layout.addWidget(self.run_after_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # تسجيل الحقول
        self.registerField("create_desktop_shortcut", self.desktop_checkbox)
        self.registerField("create_start_menu_shortcut", self.start_menu_checkbox)
        self.registerField("run_after_install", self.run_after_checkbox)
        
        layout.addStretch()
        self.setLayout(layout)


class InstallationPage(QWizardPage):
    """صفحة التثبيت الفعلي"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("جاري التثبيت...")
        self.setSubTitle("الرجاء الانتظار حتى اكتمال عملية التثبيت.")
        
        self.installation_complete = False
        self.installation_success = False
        
        layout = QVBoxLayout()
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # حالة التثبيت
        self.status_label = QLabel("جاري التحضير...")
        self.status_label.setStyleSheet(f"padding: 10px; font-size: {FONT_SIZES.BODY}px;")
        layout.addWidget(self.status_label)
        
        # سجل التثبيت
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def initializePage(self):
        """بدء عملية التثبيت عند دخول الصفحة"""
        install_path = self.field("install_path")
        create_desktop = self.field("create_desktop_shortcut")
        create_start_menu = self.field("create_start_menu_shortcut")
        
        # الحصول على مسار المصدر (المجلد الحالي للتطبيق)
        source_path = Path(__file__).parent.parent
        
        # إنشاء وتشغيل خيط التثبيت
        self.worker = InstallationWorker(
            str(source_path),
            install_path,
            create_desktop,
            create_start_menu
        )
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.installation_finished.connect(self._installation_finished)
        self.worker.start()
    
    def _update_progress(self, value, message):
        """تحديث شريط التقدم"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        self.log_text.append(message)
    
    def _installation_finished(self, success, message):
        """معالجة انتهاء التثبيت"""
        self.installation_complete = True
        self.installation_success = success
        
        if success:
            self.status_label.setText(f"{ICONS.SUCCESS} {message}")
            self.status_label.setStyleSheet(f"color: {COLORS.SUCCESS}; padding: 10px; font-size: {FONT_SIZES.BODY}px;")
        else:
            self.status_label.setText(f"{ICONS.ERROR} {message}")
            self.status_label.setStyleSheet(f"color: {COLORS.ERROR}; padding: 10px; font-size: {FONT_SIZES.BODY}px;")
        
        self.log_text.append(f"\n{'='*50}\n{message}")
        self.completeChanged.emit()
    
    def isComplete(self):
        """التحقق من اكتمال التثبيت"""
        return self.installation_complete


class FinishPage(QWizardPage):
    """صفحة الانتهاء"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("اكتمل التثبيت!")
        self.setSubTitle("تم تثبيت البرنامج بنجاح.")
        
        layout = QVBoxLayout()
        
        # رسالة النجاح
        success_label = QLabel(f"""
        <h2>{ICONS.SUCCESS} تهانينا!</h2>
        <p>تم تثبيت <b>{APP_SETTINGS.APP_NAME}</b> بنجاح على جهازك.</p>
        <br>
        <p>يمكنك الآن تشغيل البرنامج من:</p>
        <ul>
            <li>اختصار سطح المكتب</li>
            <li>قائمة ابدأ</li>
            <li>مجلد التثبيت مباشرة</li>
        </ul>
        """)
        success_label.setWordWrap(True)
        layout.addWidget(success_label)
        
        layout.addStretch()
        
        # ملاحظة
        note_label = QLabel(f"{ICONS.INFO} شكراً لاستخدامك برنامج أرشفة الكتب الرسمية!")
        note_label.setStyleSheet(f"color: {COLORS.INFO}; padding: 10px;")
        layout.addWidget(note_label)
        
        self.setLayout(layout)


class InstallerWizard(QWizard):
    """
    معالج تثبيت البرنامج الرئيسي
    Main Installation Wizard
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"تثبيت {APP_SETTINGS.APP_NAME}")
        self.setMinimumSize(600, 450)
        
        # إضافة الصفحات
        self.addPage(WelcomePage(self))
        self.addPage(InstallLocationPage(self))
        self.addPage(OptionsPage(self))
        self.addPage(InstallationPage(self))
        self.addPage(FinishPage(self))
        
        # تخصيص الأزرار
        self.setButtonText(QWizard.WizardButton.NextButton, "التالي >")
        self.setButtonText(QWizard.WizardButton.BackButton, "< السابق")
        self.setButtonText(QWizard.WizardButton.FinishButton, "إنهاء")
        self.setButtonText(QWizard.WizardButton.CancelButton, "إلغاء")
        
        # تعيين الخيارات
        self.setOptions(
            QWizard.WizardOption.NoBackButtonOnStartPage |
            QWizard.WizardOption.NoBackButtonOnLastPage
        )
    
    def done(self, result):
        """معالجة إنهاء المعالج"""
        if result == QDialog.DialogCode.Accepted:
            # التحقق من خيار تشغيل البرنامج
            if self.field("run_after_install"):
                install_path = self.field("install_path")
                self._run_installed_app(install_path)
        
        super().done(result)
    
    def _run_installed_app(self, install_path):
        """تشغيل البرنامج بعد التثبيت"""
        try:
            import subprocess
            app_path = Path(install_path) / "main.py"
            if app_path.exists():
                subprocess.Popen([sys.executable, str(app_path)], cwd=install_path)
        except Exception as e:
            print(f"تعذر تشغيل البرنامج: {e}")


class UpdateChecker:
    """
    فئة للتحقق من وجود تحديثات
    Update Checker Class
    """
    
    def __init__(self, current_version):
        self.current_version = current_version
        self.update_url = "https://example.com/updates/version.json"  # يمكن تغييره
    
    def check_for_updates(self):
        """التحقق من وجود تحديثات جديدة"""
        try:
            import urllib.request
            import json
            
            response = urllib.request.urlopen(self.update_url, timeout=5)
            data = json.loads(response.read().decode())
            
            latest_version = data.get('version', '0.0.0')
            download_url = data.get('download_url', '')
            changelog = data.get('changelog', '')
            
            if self._compare_versions(latest_version, self.current_version) > 0:
                return {
                    'available': True,
                    'version': latest_version,
                    'download_url': download_url,
                    'changelog': changelog
                }
            
            return {'available': False}
        except:
            return {'available': False, 'error': 'تعذر الاتصال بخادم التحديثات'}
    
    def _compare_versions(self, v1, v2):
        """مقارنة إصدارين"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        
        return 0


class UpdateDialog(QDialog):
    """
    نافذة عرض التحديثات المتاحة
    Update Available Dialog
    """
    
    def __init__(self, parent=None, update_info=None):
        super().__init__(parent)
        self.update_info = update_info or {}
        self.setWindowTitle("تحديث متاح")
        self.setMinimumSize(400, 300)
        
        self._init_ui()
    
    def _init_ui(self):
        """إنشاء واجهة المستخدم"""
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel(f"{ICONS.INFO} يتوفر تحديث جديد!")
        title.setStyleSheet(f"font-size: {FONT_SIZES.TITLE}px; font-weight: bold; color: {COLORS.SUCCESS};")
        layout.addWidget(title)
        
        # معلومات التحديث
        version_label = QLabel(f"الإصدار الجديد: {self.update_info.get('version', 'غير معروف')}")
        layout.addWidget(version_label)
        
        current_label = QLabel(f"الإصدار الحالي: {APP_SETTINGS.VERSION}")
        layout.addWidget(current_label)
        
        # سجل التغييرات
        changelog_group = QGroupBox("التغييرات في هذا الإصدار:")
        changelog_layout = QVBoxLayout()
        
        changelog_text = QTextEdit()
        changelog_text.setReadOnly(True)
        changelog_text.setText(self.update_info.get('changelog', 'لا توجد معلومات'))
        changelog_layout.addWidget(changelog_text)
        
        changelog_group.setLayout(changelog_layout)
        layout.addWidget(changelog_group)
        
        # الأزرار
        buttons_layout = QHBoxLayout()
        
        download_btn = QPushButton(f"{ICONS.IMPORT} تحميل الآن")
        download_btn.setStyleSheet(f"background-color: {COLORS.SUCCESS}; color: white; padding: 10px;")
        download_btn.clicked.connect(self._download_update)
        buttons_layout.addWidget(download_btn)
        
        later_btn = QPushButton(f"{ICONS.CANCEL} لاحقاً")
        later_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(later_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def _download_update(self):
        """فتح رابط تحميل التحديث"""
        download_url = self.update_info.get('download_url', '')
        if download_url:
            import webbrowser
            webbrowser.open(download_url)
        self.accept()


def show_installer():
    """عرض نافذة معالج التثبيت"""
    wizard = InstallerWizard()
    return wizard.exec()


def check_and_show_updates(parent=None):
    """التحقق من التحديثات وعرض النافذة إذا وجدت"""
    checker = UpdateChecker(APP_SETTINGS.VERSION)
    result = checker.check_for_updates()
    
    if result.get('available'):
        dialog = UpdateDialog(parent, result)
        dialog.exec()
        return True
    
    return False


# للتشغيل المباشر
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # عرض معالج التثبيت
    result = show_installer()
    
    sys.exit(result)
