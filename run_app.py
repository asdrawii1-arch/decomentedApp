#!/usr/bin/env python3
"""
تشغيل البرنامج الرئيسي
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

if __name__ == '__main__':
    from main import main
    main()
