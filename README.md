# نظام إدارة الوثائق - Document Management System

## الوصف
تطبيق سطح مكتب لإدارة وأرشفة الوثائق والكتب الرسمية باستخدام واجهة رسومية حديثة.

## المتطلبات
- Python 3.10 أو أحدث
- نظام Windows

## التثبيت

```bash
# تثبيت المكتبات المطلوبة
pip install -r requirements.txt
```

## التشغيل

```bash
python main.py
```

## هيكل المشروع

```
├── main.py              # نقطة البدء الرئيسية
├── requirements.txt     # المكتبات المطلوبة
├── documents/           # مجلد تخزين الوثائق
├── assets/              # الملفات والأيقونات
└── src/
    ├── app/             # وحدات التطبيق
    │   ├── document_viewer.py
    │   ├── filename_parser.py
    │   ├── helpers.py
    │   ├── image_manager.py
    │   ├── ocr_extractor.py
    │   ├── scanner_manager.py
    │   ├── settings.py
    │   └── ui_styles.py
    └── database/        # إدارة قاعدة البيانات
        └── db_manager.py
```

## الميزات
- إضافة وإدارة الوثائق
- استيراد الصور ومعالجتها
- استخراج النصوص بتقنية OCR
- البحث والتصفية
- تصدير البيانات

