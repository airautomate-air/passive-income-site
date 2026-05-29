#!/usr/bin/env python3
import shutil
import os
import sys

def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(src_dir, 'dist')
    # Remove existing dist
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    # Copy everything except .git, dist, __pycache__, .gitignore maybe
    ignore_patterns = shutil.ignore_patterns('.git', 'dist', '__pycache__', '*.pyc', '*.pyo')
    shutil.copytree(src_dir, dist_dir, ignore=ignore_patterns)
    print(f"Site built to {dist_dir}")

if __name__ == '__main__':
    main()
