#!/usr/bin/env python3
"""
GUI для УВМ - Этап 6 (исправленная версия)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import sys
import math


class UVMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("УВМ - Вариант 20 (Этап 6)")
        self.root.geometry("800x600")

        # Создаем интерфейс
        self.create_widgets()

        # Загружаем пример
        self.load_example()

        # Показываем статус
        self.log_output("✅ GUI приложение УВМ загружено")
        self.log_output("Этап 6: Кроссплатформенное GUI приложение")

    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель - редактор
        editor_frame = ttk.LabelFrame(main_frame, text="Программа (JSON)", padding="10")
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Редактор кода
        self.editor = scrolledtext.ScrolledText(editor_frame, height=20, width=40)
        self.editor.pack(fill=tk.BOTH, expand=True)

        # Кнопки управления
        btn_frame = ttk.Frame(editor_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Загрузить пример",
                   command=self.load_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Ассемблировать",
                   command=self.assemble_program).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Выполнить",
                   command=self.run_program).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Очистить",
                   command=self.clear_editor).pack(side=tk.LEFT, padx=2)

        # Правая панель - вывод
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Вкладки
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка вывода
        output_tab = ttk.Frame(self.notebook)
        self.output_text = scrolledtext.ScrolledText(output_tab, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(output_tab, text="Вывод")

        # Вкладка памяти
        memory_tab = ttk.Frame(self.notebook)
        self.memory_text = scrolledtext.ScrolledText(memory_tab, height=10)
        self.memory_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(memory_tab, text="Память")

        # Вкладка справки
        help_tab = ttk.Frame(self.notebook)
        help_text = scrolledtext.ScrolledText(help_tab, height=10)
        help_text.pack(fill=tk.BOTH, expand=True)

        # Заполняем справку
        help_content = """КОМАНДЫ УВМ:

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
}"""

        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')
        self.notebook.add(help_tab, text="Справка")

    def load_example(self):
        """Загружает пример программы"""
        example = {
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

        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', json.dumps(example, indent=2))
        self.log_output("Загружен пример программы")

    def clear_editor(self):
        """Очищает редактор"""
        self.editor.delete('1.0', tk.END)
        self.log_output("Редактор очищен")

    def log_output(self, message):
        """Записывает сообщение в вывод"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

    def update_memory(self, memory_data):
        """Обновляет дамп памяти"""
        self.memory_text.delete('1.0', tk.END)

        if isinstance(memory_data, dict):
            for addr, value in sorted(memory_data.items(), key=lambda x: int(x[0])):
                self.memory_text.insert(tk.END, f"MEM[{addr}] = {value}\n")
        elif isinstance(memory_data, str):
            self.memory_text.insert(tk.END, memory_data)

    def assemble_program(self):
        """Ассемблирует программу (Этапы 1-2)"""
        try:
            code = self.editor.get('1.0', tk.END).strip()
            if not code:
                messagebox.showwarning("Предупреждение", "Редактор пуст!")
                return

            program = json.loads(code)

            self.output_text.delete('1.0', tk.END)
            self.log_output("=== АССЕМБЛИРОВАНИЕ (Этапы 1-2) ===")

            # Таблица кодов операций
            opcodes = {
                'LOAD_CONST': 10,
                'LOAD_MEM': 0,
                'STORE_MEM': 14,
                'SQRT': 2
            }

            # Парсим программу
            commands = program.get('program', [])
            self.log_output(f"Найдено команд: {len(commands)}")
            self.log_output("")
            self.log_output("Промежуточное представление:")
            self.log_output("-" * 40)

            for i, cmd in enumerate(commands):
                opcode = cmd.get('opcode', '').upper()
                operand = cmd.get('operand', 0)
                comment = cmd.get('comment', '')

                if opcode in opcodes:
                    self.log_output(f"Команда {i}: A={opcodes[opcode]}, B={operand} # {comment}")
                else:
                    self.log_output(f"Команда {i}: НЕИЗВЕСТНАЯ КОМАНДА '{opcode}'")

            self.log_output("-" * 40)
            self.log_output("✅ Ассемблирование завершено")

            # Показываем байтовое представление
            self.log_output("")
            self.log_output("Байтовое представление (3 байта на команду):")
            for cmd in commands:
                opcode = opcodes.get(cmd.get('opcode', '').upper(), 0)
                operand = cmd.get('operand', 0)

                # Формируем 3 байта
                byte1 = (opcode << 4) | ((operand >> 8) & 0x0F)
                byte2 = operand & 0xFF
                byte3 = 0

                self.log_output(f"  {byte1:02X} {byte2:02X} {byte3:02X}")

            messagebox.showinfo("Успех", "Программа ассемблирована!")

        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка", f"Некорректный JSON:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка ассемблирования:\n{str(e)}")

    def run_program(self):
        """Выполняет программу (Этапы 3-5)"""
        try:
            code = self.editor.get('1.0', tk.END).strip()
            if not code:
                messagebox.showwarning("Предупреждение", "Редактор пуст!")
                return

            program = json.loads(code)

            self.output_text.delete('1.0', tk.END)
            self.log_output("=== ВЫПОЛНЕНИЕ ПРОГРАММЫ (Этапы 3-5) ===")

            # Инициализируем память (64KB)
            memory_size = 65536
            memory = [0] * memory_size

            # Инициализируем тестовые данные (как в Этапе 5)
            memory[500] = 25  # √25 = 5
            memory[501] = 100  # √100 = 10
            memory[502] = 225  # √225 = 15
            memory[520] = 100  # Для LOAD_CONST теста
            memory[133] = 42  # Для LOAD_MEM теста

            acc = 0  # Аккумулятор

            # Таблица кодов операций
            opcodes = {
                'LOAD_CONST': 10,
                'LOAD_MEM': 0,
                'STORE_MEM': 14,
                'SQRT': 2
            }

            # Выполняем команды
            commands = program.get('program', [])
            for i, cmd in enumerate(commands):
                opcode = cmd.get('opcode', '').upper()
                operand = cmd.get('operand', 0)
                comment = cmd.get('comment', '')

                if opcode == 'LOAD_CONST':
                    acc = operand
                    self.log_output(f"Команда {i}: LOAD_CONST {operand} → ACC={acc}")

                elif opcode == 'LOAD_MEM':
                    addr = acc + operand
                    if 0 <= addr < memory_size:
                        acc = memory[addr]
                        self.log_output(f"Команда {i}: LOAD_MEM {operand} → MEM[{addr}]={acc}")
                    else:
                        self.log_output(f"Команда {i}: ОШИБКА - адрес {addr} вне памяти")

                elif opcode == 'STORE_MEM':
                    if 0 <= operand < memory_size:
                        memory[operand] = acc
                        self.log_output(f"Команда {i}: STORE_MEM {operand} ← ACC={acc}")
                    else:
                        self.log_output(f"Команда {i}: ОШИБКА - адрес {operand} вне памяти")

                elif opcode == 'SQRT':
                    src_addr = acc
                    dst_addr = operand

                    if 0 <= src_addr < memory_size and 0 <= dst_addr < memory_size:
                        value = memory[src_addr]
                        result = int(math.sqrt(abs(value)))  # Берем модуль для отрицательных
                        memory[dst_addr] = result
                        self.log_output(f"Команда {i}: SQRT MEM[{src_addr}]={value} → MEM[{dst_addr}]={result}")
                    else:
                        self.log_output(f"Команда {i}: ОШИБКА SQRT - неверные адреса")

                else:
                    self.log_output(f"Команда {i}: НЕИЗВЕСТНАЯ КОМАНДА '{opcode}'")

            self.log_output("")
            self.log_output("✅ Выполнение завершено")

            # Создаем дамп памяти (как в Этапе 5)
            self.log_output("")
            self.log_output("=== ДАМП ПАМЯТИ (ненулевые значения) ===")

            memory_dump = {}
            for addr in range(1000):  # Первые 1000 ячеек
                if memory[addr] != 0:
                    memory_dump[str(addr)] = memory[addr]
                    self.log_output(f"MEM[{addr}] = {memory[addr]}")

            # Показываем дамп во вкладке памяти
            self.update_memory(memory_dump)

            # Переключаемся на вкладку памяти
            self.notebook.select(1)  # Вторая вкладка (память)

            messagebox.showinfo("Успех", "Программа выполнена!\nПроверьте вкладку 'Память'")

        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка", f"Некорректный JSON:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения:\n{str(e)}")


def main():
    root = tk.Tk()
    app = UVMGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
