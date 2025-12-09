#!/usr/bin/env python3
"""
Скрипт сборки для Этапа 6
Создает исполняемые файлы для Windows, Linux и Web
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

class UVMBuilder:
    """Сборщик проекта УВМ"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        
    def clean_build(self):
        """Очистка папок сборки"""
        print("🧹 Очистка папок сборки...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(exist_ok=True)
        
        print("✅ Папки сборки очищены")
    
    def copy_source_files(self):
        """Копирование исходных файлов"""
        print("📁 Копирование исходных файлов...")
        
        # Основные файлы
        source_files = [
            'uvm_asm.py',
            'uvm_interp.py', 
            'uvm_gui.py',
            'requirements.txt',
            'README.md',
            'LICENSE'
        ]
        
        # Примеры программ
        example_files = []
        for file in self.project_dir.glob('*.json'):
            if file.name.endswith('.json'):
                example_files.append(file.name)
        
        # Копируем файлы
        for file in source_files:
            src = self.project_dir / file
            if src.exists():
                shutil.copy2(src, self.build_dir / file)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠ {file} не найден")
        
        # Создаем папку examples
        examples_dir = self.build_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        for example in example_files[:5]:  # Первые 5 примеров
            src = self.project_dir / example
            shutil.copy2(src, examples_dir / example)
            print(f"  ✅ examples/{example}")
        
        print("✅ Исходные файлы скопированы")
    
    def create_readme(self):
        """Создание README для сборки"""
        print("📝 Создание README...")
        
        readme_content = """# Учебная Виртуальная Машина (УВМ) - Вариант 20

## Сборка от %DATE%

### Доступные версии:
1. **Windows**: `uvm_windows.zip` - GUI приложение на Tkinter
2. **Linux**: `uvm_linux.tar.gz` - GUI приложение на Tkinter  
3. **Web**: `uvm_web.html` - Веб-версия через PyScript

### Запуск:

#### Windows/Linux (GUI):
```bash
python uvm_gui.py
