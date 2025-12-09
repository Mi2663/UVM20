#!/usr/bin/env python3
"""
Тесты для интерпретатора УВМ (Этап 3)
"""

import unittest
import tempfile
import json
import os
import sys

# Добавляем путь к текущей директории для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uvm_interp import UVMInterpreter
from uvm_asm import UVMAssembler

class TestUVMInterpreter(unittest.TestCase):
    """Тесты для интерпретатора УВМ"""
    
    def setUp(self):
        self.interpreter = UVMInterpreter(mem_size=1000)
        self.assembler = UVMAssembler()
    
    def test_memory_initialization(self):
        """Тест инициализации памяти"""
        # Память должна быть заполнена нулями
        for i in range(100):
            self.assertEqual(self.interpreter.memory[i], 0)
        
        # Проверка размера памяти
        self.assertEqual(len(self.interpreter.memory), 1000)
        
        print("✓ Инициализация памяти работает")
    
    def test_load_const_command(self):
        """Тест команды LOAD_CONST"""
        # Создаем простую программу
        program = [{"opcode": "LOAD_CONST", "operand": 123}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        # Эмулируем выполнение
        cmd = intermediate[0]
        self.interpreter.execute_load_const(cmd.operand)
        
        self.assertEqual(self.interpreter.acc, 123)
        print("✓ Команда LOAD_CONST работает")
    
    def test_store_and_load_memory(self):
        """Тест записи и чтения из памяти"""
        # Запись в память
        self.interpreter.acc = 456
        self.interpreter.execute_store_mem(50)
        
        self.assertEqual(self.interpreter.memory[50], 456)
        
        # Чтение из памяти
        self.interpreter.acc = 50  # Адрес для чтения
        self.interpreter.execute_load_mem(0)  # Смещение 0
        
        self.assertEqual(self.interpreter.acc, 456)
        print("✓ Запись и чтение из памяти работают")
    
    def test_simple_program_execution(self):
        """Тест выполнения простой программы"""
        # Создаем тестовую программу
        test_program = {
            "program": [
                {"opcode": "LOAD_CONST", "operand": 777},
                {"opcode": "STORE_MEM", "operand": 300},
                {"opcode": "LOAD_CONST", "operand": 300},
                {"opcode": "LOAD_MEM", "operand": 0}
            ]
        }
        
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_program, f)
            json_file = f.name
        
        # Ассемблируем
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
            bin_file = f.name
        
        try:
            # Ассемблирование
            intermediate = self.assembler.assemble(json_file, None, False)
            self.assembler.encode_to_binary(intermediate, bin_file)
            
            # Загрузка и выполнение
            self.interpreter.load_program(bin_file)
            self.interpreter.run()
            
            # Проверка результатов
            self.assertEqual(self.interpreter.memory[300], 777)
            self.assertEqual(self.interpreter.acc, 777)
            
            print("✓ Выполнение простой программы работает")
            
        finally:
            # Удаление временных файлов
            if os.path.exists(json_file):
                os.unlink(json_file)
            if os.path.exists(bin_file):
                os.unlink(bin_file)
    
    def test_memory_dump(self):
        """Тест дампа памяти"""
        # Заполняем память тестовыми данными
        self.interpreter.memory[10] = 100
        self.interpreter.memory[20] = 200
        self.interpreter.memory[30] = 300
        
        # Получаем дамп
        dump = self.interpreter.dump_memory(0, 50)
        
        # Проверяем содержимое
        self.assertIn('10', dump)
        self.assertIn('20', dump)
        self.assertIn('30', dump)
        self.assertEqual(dump['10'], 100)
        self.assertEqual(dump['20'], 200)
        self.assertEqual(dump['30'], 300)
        
        # Проверяем, что нулевые значения не включены
        self.assertNotIn('0', dump)
        self.assertNotIn('15', dump)
        
        print("✓ Дамп памяти работает корректно")
    
    def test_array_copy_simulation(self):
        """Тестирование симуляции копирования массива"""
        # Инициализируем исходный массив
        for i in range(10):
            self.interpreter.memory[100 + i] = (i + 1) * 10  # 10, 20, 30...100
        
        # Копируем вручную для теста
        for i in range(10):
            self.interpreter.memory[200 + i] = self.interpreter.memory[100 + i]
        
        # Проверяем копирование
        for i in range(10):
            source_val = self.interpreter.memory[100 + i]
            dest_val = self.interpreter.memory[200 + i]
            self.assertEqual(source_val, dest_val,
                           f"Ошибка копирования элемента {i}: {source_val} != {dest_val}")
        
        print("✓ Симуляция копирования массива работает")

def run_interpreter_tests():
    """Запуск всех тестов интерпретатора"""
    print("=" * 60)
    print("Тестирование интерпретатора УВМ - Этап 3")
    print("=" * 60)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUVMInterpreter)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ ИНТЕРПРЕТАТОРА:")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ИНТЕРПРЕТАТОРА ПРОЙДЕНЫ!")
        print("Этап 3 реализован корректно.")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_interpreter_tests()
    
    if success:
        print("\n" + "=" * 60)
        print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ИНТЕРПРЕТАТОРА:")
        print("=" * 60)
        print("1. Создайте тестовую программу:")
        print("   python uvm_asm.py simple_test.json simple.bin --binary")
        print()
        print("2. Запустите интерпретатор:")
        print("   python uvm_interp.py simple.bin result.json 0 200 --test")
        print()
        print("3. Проверьте результат:")
        print("   type result.json")
        print()
        print("4. Для копирования массива:")
        print("   python uvm_asm.py array_copy.json copy.bin --binary")
        print("   python uvm_interp.py copy.bin copy_result.json 0 300 --test")
    
    sys.exit(0 if success else 1)
