#!/usr/bin/env python3
"""
GUI приложение для УВМ - Этап 6
Кроссплатформенное приложение (Windows, Linux, Web/WASM)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import sys
import threading
import subprocess
import tempfile
from pathlib import Path

# Добавляем путь для импорта наших модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from uvm_asm import UVMAssembler
    from uvm_interp import UVMInterpreter
    HAS_MODULES = True
except ImportError:
    HAS_MODULES = False
    print("⚠ Модули УВМ не найдены. GUI будет работать в демо-режиме.")

class UVMGUI:
    """Главное окно GUI приложения УВМ"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Учебная Виртуальная Машина (УВМ) - Вариант 20")
        self.root.geometry("1200x700")
        
        # Стиль
        self.setup_styles()
        
        # Переменные
        self.asm_file = None
        self.bin_file = None
        self.dump_file = None
        self.temp_files = []
        
        # Создание интерфейса
        self.create_widgets()
        
        # Статус
        self.update_status("Готов к работе")
        
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цветовая схема
        self.bg_color = "#f0f0f0"
        self.text_bg = "#ffffff"
        self.highlight_color = "#4a86e8"
        
        self.root.configure(bg=self.bg_color)
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов строк и столбцов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(
            main_frame, 
            text="🎮 Учебная Виртуальная Машина (УВМ) - Вариант 20",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Левая панель: редактор кода
        left_frame = ttk.LabelFrame(main_frame, text="Редактор программы", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # Панель инструментов редактора
        editor_toolbar = ttk.Frame(left_frame)
        editor_toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(editor_toolbar, text="Загрузить", command=self.load_program).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_toolbar, text="Сохранить", command=self.save_program).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_toolbar, text="Пример", command=self.load_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_toolbar, text="Очистить", command=self.clear_editor).pack(side=tk.LEFT, padx=2)
        
        # Редактор кода
        self.code_editor = scrolledtext.ScrolledText(
            left_frame,
            width=50,
            height=25,
            font=("Consolas", 10),
            bg=self.text_bg,
            undo=True
        )
        self.code_editor.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Загружаем пример программы
        self.load_example()
        
        # Центральная панель: управление
        center_frame = ttk.LabelFrame(main_frame, text="Управление", padding="10")
        center_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        
        # Кнопки управления
        control_frame = ttk.Frame(center_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.assemble_btn = ttk.Button(
            control_frame,
            text="▶ Ассемблировать",
            command=self.assemble_program,
            style="Accent.TButton"
        )
        self.assemble_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.run_btn = ttk.Button(
            control_frame,
            text="⚡ Выполнить",
            command=self.run_program,
            style="Accent.TButton"
        )
        self.run_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Настройки выполнения
        settings_frame = ttk.LabelFrame(center_frame, text="Настройки выполнения", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Диапазон дампа памяти
        ttk.Label(settings_frame, text="Диапазон дампа памяти:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        range_frame = ttk.Frame(settings_frame)
        range_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(range_frame, text="От:").pack(side=tk.LEFT)
        self.start_addr = ttk.Entry(range_frame, width=10)
        self.start_addr.pack(side=tk.LEFT, padx=5)
        self.start_addr.insert(0, "0")
        
        ttk.Label(range_frame, text="До:").pack(side=tk.LEFT, padx=(10, 0))
        self.end_addr = ttk.Entry(range_frame, width=10)
        self.end_addr.pack(side=tk.LEFT, padx=5)
        self.end_addr.insert(0, "1000")
        
        # Инициализация памяти
        self.init_memory_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings_frame,
            text="Инициализировать тестовую память",
            variable=self.init_memory_var
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.verbose_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Подробный вывод (verbose)",
            variable=self.verbose_var
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Правая панель: вывод и память
        right_frame = ttk.LabelFrame(main_frame, text="Вывод и память", padding="10")
        right_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Вкладки
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка вывода
        output_frame = ttk.Frame(self.notebook)
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            width=40,
            height=20,
            font=("Consolas", 9),
            bg=self.text_bg,
            state='disabled'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(output_frame, text="Вывод")
        
        # Вкладка памяти
        memory_frame = ttk.Frame(self.notebook)
        self.memory_text = scrolledtext.ScrolledText(
            memory_frame,
            width=40,
            height=20,
            font=("Consolas", 9),
            bg=self.text_bg,
            state='disabled'
        )
        self.memory_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(memory_frame, text="Память")
        
        # Вкладка справки
        help_frame = ttk.Frame(self.notebook)
        help_text = scrolledtext.ScrolledText(
            help_frame,
            width=40,
            height=20,
            font=("Arial", 10),
            bg=self.bg_color
        )
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Заполняем справку
        help_content = """
        КОМАНДЫ УВМ:
        
        1. LOAD_CONST <value>
           Загружает константу в аккумулятор
           Пример: {"opcode": "LOAD_CONST", "operand": 520}
        
        2. LOAD_MEM <offset>
           Читает из памяти: ACC = MEM[ACC + offset]
           Пример: {"opcode": "LOAD_MEM", "operand": 133}
        
        3. STORE_MEM <address>
           Записывает в память: MEM[address] = ACC
           Пример: {"opcode": "STORE_MEM", "operand": 167}
        
        4. SQRT <address>
           Вычисляет квадратный корень: MEM[address] = sqrt(MEM[ACC])
           Пример: {"opcode": "SQRT", "operand": 954}
        
        ФОРМАТ ПРОГРАММЫ (JSON):
        {
          "program": [
            {"opcode": "LOAD_CONST", "operand": 100},
            {"opcode": "STORE_MEM", "operand": 500}
          ]
        }
        
        ИСПОЛЬЗОВАНИЕ:
        1. Напишите или загрузите программу
        2. Нажмите "Ассемблировать"
        3. Нажмите "Выполнить"
        4. Просмотрите результаты во вкладках
        """
        
        help_text.insert('1.0', help_content)
        help_text.configure(state='disabled')
        self.notebook.add(help_frame, text="Справка")
        
        # Статус бар
        self.status_bar = ttk.Label(
            main_frame,
            text="Готов",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Информация о проекте
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Label(
            info_frame,
            text="УВМ Вариант 20 | Этап 6: GUI приложение | Python + Tkinter",
            font=("Arial", 8)
        ).pack()
    
    def update_status(self, message):
        """Обновить строку состояния"""
        self.status_bar.config(text=f"Статус: {message}")
        self.root.update_idletasks()
    
    def log_output(self, message, clear=False):
        """Добавить сообщение в вывод"""
        self.output_text.configure(state='normal')
        if clear:
            self.output_text.delete('1.0', tk.END)
        
        # Добавляем timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        self.output_text.configure(state='disabled')
        self.output_text.see(tk.END)
    
    def update_memory_dump(self, dump_data):
        """Обновить дамп памяти"""
        self.memory_text.configure(state='normal')
        self.memory_text.delete('1.0', tk.END)
        
        if isinstance(dump_data, dict):
            for addr, value in sorted(dump_data.items(), key=lambda x: int(x[0])):
                self.memory_text.insert(tk.END, f"MEM[{addr}] = {value}\n")
        elif isinstance(dump_data, str):
            self.memory_text.insert(tk.END, dump_data)
        
        self.memory_text.configure(state='disabled')
        self.memory_text.see(tk.END)
    
    def load_example(self):
        """Загрузить пример программы"""
        example_program = {
            "program": [
                {
                    "opcode": "LOAD_CONST",
                    "operand": 520,
                    "comment": "Тест из спецификации: A=10, B=520"
                },
                {
                    "opcode": "LOAD_MEM",
                    "operand": 133,
                    "comment": "Тест из спецификации: A=0, B=133"
                },
                {
                    "opcode": "STORE_MEM",
                    "operand": 167,
                    "comment": "Тест из спецификации: A=14, B=167"
                },
                {
                    "opcode": "SQRT",
                    "operand": 954,
                    "comment": "Тест из спецификации: A=2, B=954"
                }
            ]
        }
        
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', json.dumps(example_program, indent=2))
        self.log_output("Загружен пример программы")
    
    def load_program(self):
        """Загрузить программу из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл программы",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    program_data = json.load(f)
                
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', json.dumps(program_data, indent=2))
                self.asm_file = file_path
                self.log_output(f"Загружена программа из: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def save_program(self):
        """Сохранить программу в файл"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить программу",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                program_text = self.code_editor.get('1.0', tk.END).strip()
                
                # Проверяем JSON
                json.loads(program_text)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(program_text)
                
                self.asm_file = file_path
                self.log_output(f"Программа сохранена в: {file_path}")
                messagebox.showinfo("Успех", "Программа успешно сохранена")
                
            except json.JSONDecodeError as e:
                messagebox.showerror("Ошибка", f"Некорректный JSON:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def clear_editor(self):
        """Очистить редактор"""
        if messagebox.askyesno("Подтверждение", "Очистить редактор кода?"):
            self.code_editor.delete('1.0', tk.END)
            self.log_output("Редактор очищен")
    
    def validate_program(self):
        """Проверить программу на валидность"""
        try:
            program_text = self.code_editor.get('1.0', tk.END).strip()
            
            if not program_text:
                messagebox.showwarning("Предупреждение", "Редактор пуст!")
                return None
            
            program_data = json.loads(program_text)
            
            if 'program' not in program_data:
                messagebox.showerror("Ошибка", "JSON должен содержать поле 'program'")
                return None
            
            return program_data
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка", f"Некорректный JSON:\n{str(e)}")
            return None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при проверке:\n{str(e)}")
            return None
    
    def assemble_program(self):
        """Ассемблировать программу"""
        program_data = self.validate_program()
        if not program_data:
            return
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                       encoding='utf-8', delete=False) as f:
            json.dump(program_data, f, ensure_ascii=False)
            json_file = f.name
        
        # Создаем временный бинарный файл
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
            bin_file = f.name
        
        self.temp_files.extend([json_file, bin_file])
        
        try:
            self.update_status("Ассемблирование...")
            self.log_output("Начало ассемблирования...", clear=True)
            
            if not HAS_MODULES:
                # Демо-режим
                self.log_output("(Демо) Программа успешно ассемблирована")
                self.log_output("(Демо) Создан бинарный файл")
                self.bin_file = bin_file
                messagebox.showinfo("Успех", "Программа ассемблирована (демо-режим)")
            else:
                # Режим с реальными модулями
                assembler = UVMAssembler()
                intermediate = assembler.assemble(json_file, None, False)
                assembler.encode_to_binary(intermediate, bin_file)
                
                self.log_output(f"Программа ассемблирована: {len(intermediate)} команд")
                self.log_output(f"Бинарный файл создан: {bin_file}")
                
                # Показываем промежуточное представление
                self.log_output("\nПромежуточное представление:")
                for cmd in intermediate:
                    self.log_output(f"  {cmd}")
                
                self.bin_file = bin_file
                messagebox.showinfo("Успех", f"Программа успешно ассемблирована!\n{len(intermediate)} команд")
            
            self.update_status("Ассемблирование завершено")
            
        except Exception as e:
            self.log_output(f"❌ Ошибка ассемблирования: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка ассемблирования:\n{str(e)}")
            self.update_status("Ошибка ассемблирования")
        finally:
            # Удаляем временный JSON файл
            if os.path.exists(json_file):
                os.unlink(json_file)
                self.temp_files.remove(json_file)
    
    def run_program(self):
        """Выполнить программу"""
        if not hasattr(self, 'bin_file') or not self.bin_file:
            messagebox.showwarning("Предупреждение", 
                                 "Сначала ассемблируйте программу!")
            return
        
        if not os.path.exists(self.bin_file):
            messagebox.showerror("Ошибка", "Бинарный файл не найден!")
            return
        
        # Получаем параметры
        try:
            start_addr = int(self.start_addr.get())
            end_addr = int(self.end_addr.get())
            
            if start_addr >= end_addr:
                messagebox.showerror("Ошибка", "Начальный адрес должен быть меньше конечного!")
                return
                
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные адреса памяти!")
            return
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self._run_program_thread, 
                                args=(start_addr, end_addr))
        thread.daemon = True
        thread.start()
    
    def _run_program_thread(self, start_addr, end_addr):
        """Поток выполнения программы"""
        try:
            self.update_status("Выполнение программы...")
            self.log_output("\n" + "="*50, clear=False)
            self.log_output("НАЧАЛО ВЫПОЛНЕНИЯ ПРОГРАММЫ")
            self.log_output("="*50)
            
            # Создаем временный файл для дампа
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
                dump_file = f.name
            
            self.temp_files.append(dump_file)
            
            if not HAS_MODULES:
                # Демо-режим
                self.log_output("(Демо) Загрузка программы...")
                self.log_output("(Демо) Выполнение команд...")
                self.log_output("(Демо) Программа выполнена успешно!")
                
                # Создаем демо-дамп
                demo_dump = {
                    "100": 42,
                    "200": 100,
                    "300": 25,
                    "400": 5,   # √25
                    "500": 10   # √100
                }
                
                with open(dump_file, 'w') as f:
                    json.dump(demo_dump, f, indent=2)
                
            else:
                # Режим с реальными модулями
                interpreter = UVMInterpreter()
                
                # Инициализация памяти если нужно
                if self.init_memory_var.get():
                    test_data = {
                        100: 25,
                        200: 100,
                        300: 144,
                        400: 0,
                        500: 0
                    }
                    interpreter.initialize_memory_with_values(test_data)
                    self.log_output("Память инициализирована тестовыми данными")
                
                # Загрузка и выполнение
                interpreter.load_program(self.bin_file)
                interpreter.run(verbose=self.verbose_var.get())
                
                # Получение дампа
                dump = interpreter.dump_memory(start_addr, end_addr)
                
                with open(dump_file, 'w') as f:
                    json.dump(dump, f, indent=2)
                
                self.log_output(f"Дамп памяти сохранен ({len(dump)} значений)")
            
            # Читаем и отображаем дамп
            with open(dump_file, 'r') as f:
                dump_data = json.load(f)
            
            self.update_memory_dump(dump_data)
            self.log_output(f"\nДАМП ПАМЯТИ ({len(dump_data)} значений)")
            self.log_output(f"Диапазон: {start_addr}-{end_addr}")
            
            # Переключаемся на вкладку памяти
            self.notebook.select(1)  # Вкладка памяти
            
            self.update_status("Выполнение завершено")
            messagebox.showinfo("Успех", "Программа успешно выполнена!")
            
        except Exception as e:
            self.log_output(f"\n❌ ОШИБКА ВЫПОЛНЕНИЯ: {str(e)}")
            self.update_status("Ошибка выполнения")
            messagebox.showerror("Ошибка", f"Ошибка выполнения:\n{str(e)}")
        
        finally:
            # Удаляем временный файл дампа
            if 'dump_file' in locals() and os.path.exists(dump_file):
                os.unlink(dump_file)
                if dump_file in self.temp_files:
                    self.temp_files.remove(dump_file)
    
    def cleanup_temp_files(self):
        """Очистка временных файлов при закрытии"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass
    
    def run(self):
        """Запустить GUI"""
        try:
            self.root.mainloop()
        finally:
            self.cleanup_temp_files()

def main():
    """Основная функция"""
    root = tk.Tk()
    
    # Настройка иконки (если есть)
    try:
        root.iconbitmap('uvm_icon.ico')
    except:
        pass
    
    app = UVMGUI(root)
    
    # Обработка закрытия окна
    def on_closing():
        app.cleanup_temp_files()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    app.run()

if __name__ == "__main__":
    main()
