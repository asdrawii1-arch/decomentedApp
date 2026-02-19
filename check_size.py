#!/usr/bin/env python3
import os
import sys

def get_dir_size(path):
    """Get directory size in bytes"""
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += get_dir_size(entry.path)
                except (PermissionError, OSError):
                    pass
    except (PermissionError, OSError):
        pass
    return total

def format_bytes(bytes_size):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

# Main directories to check
base_dirs = [
    ('venv', './venv'),
    ('documents', './documents'),
    ('.git', './.git'),
    ('src', './src'),
    ('__pycache__', './__pycache__'),
]

print("\n" + "="*60)
print("PROJECT SIZE ANALYSIS")
print("="*60)

results = []
for name, path in base_dirs:
    if os.path.exists(path):
        print(f"Calculating size of {name}...", end=" ")
        sys.stdout.flush()
        size = get_dir_size(path)
        results.append((name, size))
        print(f"{format_bytes(size)}")
    else:
        print(f"{name}: NOT FOUND")

# Check venv packages specifically
venv_packages_path = './venv/lib/python3.12/site-packages'
if os.path.exists(venv_packages_path):
    print("\nTop 10 largest packages in venv:")
    print("-"*60)
    packages = []
    try:
        for item in os.listdir(venv_packages_path):
            item_path = os.path.join(venv_packages_path, item)
            if os.path.isdir(item_path):
                size = get_dir_size(item_path)
                packages.append((item, size))
    except Exception as e:
        print(f"Error reading packages: {e}")
    
    packages.sort(key=lambda x: x[1], reverse=True)
    for name, size in packages[:10]:
        print(f"  {name:40} {format_bytes(size):>12}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
results.sort(key=lambda x: x[1], reverse=True)
total_size = sum(size for _, size in results)
for name, size in results:
    percentage = (size / total_size * 100) if total_size > 0 else 0
    print(f"{name:20} {format_bytes(size):>12}  ({percentage:5.1f}%)")
print("-"*60)
print(f"{'TOTAL':20} {format_bytes(total_size):>12}  (100.0%)")
print("="*60)
