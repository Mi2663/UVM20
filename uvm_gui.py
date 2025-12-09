#!/usr/bin/env python3
"""
Простое GUI приложение для УВМ
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json

class SimpleUVMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("УВМ - Простой GUI")
        self.root.geometry("800x500")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая часть - редактор
        left_frame = ttk.LabelFrame(main_frame, text="Программа", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.editor = scrolledtext.ScrolledText(left_frame, height=20)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Загрузить пример", 
                  command=self.load_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Ассемблировать",
                  command=self.assemble).pack(side=tk.LEFT, padx=2)
        
        # Правая часть - вывод
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Вкладки
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вывод
        self.output_text = scrolledtext.ScrolledText(self.notebook, height=10)
        self.notebook.add(self.output_text, text="Вывод")
        
        # Память
        self.memory_text = scrolledtext.ScrolledText(self.notebook, height=10)
        self.notebook.add(self.memory_text, text="Память")
        
        # Загружаем пример
        self.load_example()
        
    def load_example(self):
        example = {
            "program": [
                {"opcode": "LOAD_CONST", "operand": 520},
                {"opcode": "LOAD_MEM", "operand": 133},
                {"opcode": "STORE_MEM", "operand": 167},
                {"opcode": "SQRT", "operand": 954}
            ]
        }
        
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', json.dumps(example, indent=2))
        self.log("Загружен пример программы")
        
    def assemble(self):
        try:
            code = self.editor.get('1.0', tk.END).strip()
            data = json.loads(code)
            
            self.log("Программа ассемблирована")
            self.log(f"Команд: {len(data.get('program', []))}")
            
            # Демо-дамп памяти
            demo_memory = {
                "100": 42,
                "200": 100,
                "300": 25,
                "400": 5
            }
            
            self.memory_text.delete('1.0', tk.END)
            for addr, value in demo_memory.items():
                self.memory_text.insert(tk.END, f"MEM[{addr}] = {value}\n")
                
            messagebox.showinfo("Успех", "Программа ассемблирована!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")
            
    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

def main():
    root = tk.Tk()
    app = SimpleUVMGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
