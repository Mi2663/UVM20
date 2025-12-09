#!/usr/bin/env python3
"""
Скрипт сборки для Этапа 6
Создает исполняемые файлы для Windows, Linux и Web
"""

import os
import sys
import shutil
import zipfile
import tarfile
from pathlib import Path

class UVMBuilder:
    """Сборщик проекта УВМ"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        
    def clean_build(self):
        """Очистка папок сборки"""
        print("Очистка папок сборки...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(exist_ok=True)
        
        print("Папки сборки очищены")
    
    def copy_source_files(self):
        """Копирование исходных файлов"""
        print("Копирование исходных файлов...")
        
        source_files = [
            'uvm_asm.py',
            'uvm_interp.py', 
            'requirements.txt',
            'README.md',
            'LICENSE'
        ]
        
        for file in source_files:
            src = self.project_dir / file
            if src.exists():
                shutil.copy2(src, self.build_dir / file)
                print(f"  {file}")
        
        print("Исходные файлы скопированы")
    
    def create_readme(self):
        """Создание README для сборки"""
        print("Создание README...")
        
        readme_content = """# Учебная Виртуальная Машина (УВМ)

## Доступные версии:
1. Windows: uvm_windows.zip
2. Linux: uvm_linux.tar.gz  
3. Web: uvm_web.html

### Запуск:
Windows/Linux: python uvm_gui.py
Web: Откройте uvm_web.html в браузере

### Требования:
- Python 3.8+
- Tkinter

### Лицензия:
MIT License
"""
        
        with open(self.build_dir / "README_BUILD.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("README создан")
    
    def build_windows(self):
        """Сборка для Windows"""
        print("Сборка для Windows...")
        
        windows_dir = self.dist_dir / "windows"
        windows_dir.mkdir(exist_ok=True)
        
        try:
            for file in ['uvm_asm.py', 'uvm_interp.py']:
                src = self.project_dir / file
                if src.exists():
                    shutil.copy2(src, windows_dir / file)
            
            bat_content = """@echo off
echo Учебная Виртуальная Машина (УВМ)
echo.
python uvm_asm.py --help
pause
"""
            
            with open(windows_dir / "run.bat", 'w', encoding='cp866') as f:
                f.write(bat_content)
            
            zip_path = self.dist_dir / "uvm_windows.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(windows_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, windows_dir)
                        zipf.write(file_path, f"uvm_windows/{arcname}")
            
            print(f"Windows сборка создана: {zip_path}")
            
        except Exception as e:
            print(f"Ошибка сборки для Windows: {e}")
    
    def build_linux(self):
        """Сборка для Linux"""
        print("Сборка для Linux...")
        
        linux_dir = self.dist_dir / "linux"
        linux_dir.mkdir(exist_ok=True)
        
        try:
            for file in ['uvm_asm.py', 'uvm_interp.py']:
                src = self.project_dir / file
                if src.exists():
                    shutil.copy2(src, linux_dir / file)
            
            sh_content = """#!/bin/bash
echo "Учебная Виртуальная Машина (УВМ)"
echo ""
python3 uvm_asm.py --help
"""
            
            sh_path = linux_dir / "run.sh"
            with open(sh_path, 'w', encoding='utf-8') as f:
                f.write(sh_content)
            
            os.chmod(sh_path, 0o755)
            
            tar_path = self.dist_dir / "uvm_linux.tar.gz"
            with tarfile.open(tar_path, 'w:gz') as tar:
                tar.add(linux_dir, arcname="uvm_linux")
            
            print(f"Linux сборка создана: {tar_path}")
            
        except Exception as e:
            print(f"Ошибка сборки для Linux: {e}")
    
    def build_web(self):
        """Сборка для Web"""
        print("Сборка для Web...")
        
        web_dir = self.dist_dir / "web"
        web_dir.mkdir(exist_ok=True)
        
        try:
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>УВМ - Web версия</title>
</head>
<body>
    <h1>УВМ Web версия</h1>
    <p>Для работы нужен файл uvm_web.html</p>
</body>
</html>"""
            
            with open(web_dir / "uvm_web.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            for file in ['uvm_asm.py', 'uvm_interp.py']:
                src = self.project_dir / file
                if src.exists():
                    shutil.copy2(src, web_dir / file)
            
            zip_path = self.dist_dir / "uvm_web.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(web_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, web_dir)
                        zipf.write(file_path, f"uvm_web/{arcname}")
            
            print(f"Web сборка создана: {zip_path}")
            
        except Exception as e:
            print(f"Ошибка сборки для Web: {e}")
    
    def build_all(self):
        """Сборка всех версий"""
        print("Начало сборки...")
        print("="*50)
        
        self.clean_build()
        self.copy_source_files()
        self.create_readme()
        
        print("\nСборка платформ:")
        self.build_windows()
        self.build_linux()
        self.build_web()
        
        print("\nСборка завершена!")
        
        print("\nСозданные файлы:")
        for file in self.dist_dir.glob("*"):
            if file.is_file():
                size = file.stat().st_size / 1024
                print(f"  {file.name} ({size:.1f} KB)")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Сборщик проекта УВМ")
    parser.add_argument('--all', action='store_true', help='Собрать все версии')
    parser.add_argument('--clean', action='store_true', help='Очистить папки сборки')
    
    args = parser.parse_args()
    
    builder = UVMBuilder()
    
    if args.clean:
        builder.clean_build()
        return
    
    builder.build_all()

if __name__ == '__main__':
    main()
