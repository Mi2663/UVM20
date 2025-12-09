#!/usr/bin/env python3
"""
Тесты для интерпретатора УВМ - Этап 4 (АЛУ, команда sqrt)
"""

import unittest
import tempfile
import json
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uvm_interp import UVMInterpreter
from uvm_asm import UVMAssembler

class TestUVMInterpreterStage4(unittest.TestCase):
    """Тесты для Этапа 4 (команда sqrt)"""
    
    def setUp(self):
        self.interpreter = UVMInterpreter(mem_size=2000)
        self.assembler = UVMAssembler()
    
    def test_sqrt_operation_basic(self):
        """Тест базовой операции sqrt"""
        # Устанавливаем значение в памяти
        self.interpreter.memory[100] = 25
        
        # Устанавливаем аккумулятор на адрес источника
        self.interpreter.acc = 100
        
        # Выполняем sqrt
        self.interpreter.execute_sqrt(200)
        
        # Проверяем результат
        self.assertEqual(self.interpreter.memory[200], 5)  # √25 = 5
        self.assertEqual(self.interpreter.sqrt_operations, 1)
        print("✓ Базовая операция sqrt работает")
    
    def test_sqrt_multiple_values(self):
        """Тест sqrt для нескольких значений"""
        test_cases = [
            (0, 0),     # √0 = 0
            (1, 1),     # √1 = 1
            (4, 2),     # √4 = 2
            (9, 3),     # √9 = 3
            (16, 4),    # √16 = 4
            (25, 5),    # √25 = 5
            (100, 10),  # √100 = 10
            (144, 12),  # √144 = 12
            (225, 15),  # √225 = 15
        ]
        
        for i, (value, expected) in enumerate(test_cases):
            src_addr = 300 + i
            dst_addr = 400 + i
            
            # Записываем значение
            self.interpreter.memory[src_addr] = value
            self.interpreter.acc = src_addr
            
            # Выполняем sqrt
            self.interpreter.execute_sqrt(dst_addr)
            
            # Проверяем
            self.assertEqual(self.interpreter.memory[dst_addr], expected,
                           f"√{value} должно быть {expected}, а получилось {self.interpreter.memory[dst_addr]}")
        
        print("✓ sqrt для нескольких значений работает")
    
    def test_sqrt_negative_number(self):
        """Тест sqrt для отрицательного числа"""
        # Для отрицательных чисел берем модуль
        self.interpreter.memory[150] = -36
        self.interpreter.acc = 150
        self.interpreter.execute_sqrt(250)
        
        # √(-36) = 6i, но мы берем модуль: √36 = 6
        self.assertEqual(self.interpreter.memory[250], 6)
        print("✓ sqrt для отрицательных чисел (берется модуль)")
    
    def test_sqrt_large_number(self):
        """Тест sqrt для большого числа"""
        self.interpreter.memory[160] = 10000
        self.interpreter.acc = 160
        self.interpreter.execute_sqrt(260)
        
        self.assertEqual(self.interpreter.memory[260], 100)  # √10000 = 100
        print("✓ sqrt для больших чисел работает")
    
    def test_sqrt_program_execution(self):
        """Тест выполнения программы с командой sqrt"""
        # Создаем тестовую программу
        test_program = {
            "program": [
                {"opcode": "LOAD_CONST", "operand": 100},
                {"opcode": "SQRT", "operand": 200}
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
            # Инициализируем память
            self.interpreter.memory[100] = 49  # √49 = 7
            
            # Ассемблирование
            intermediate = self.assembler.assemble(json_file, None, False)
            self.assembler.encode_to_binary(intermediate, bin_file)
            
            # Загрузка и выполнение
            self.interpreter.load_program(bin_file)
            self.interpreter.run(verbose=False)
            
            # Проверка результатов
            self.assertEqual(self.interpreter.memory[200], 7)
            self.assertEqual(self.interpreter.sqrt_operations, 1)
            
            print("✓ Выполнение программы с sqrt работает")
            
        finally:
            # Удаление временных файлов
            if os.path.exists(json_file):
                os.unlink(json_file)
            if os.path.exists(bin_file):
                os.unlink(bin_file)
    
    def test_vector_sqrt_simulation(self):
        """Тестирование поэлементного sqrt над вектором"""
        # Создаем вектор из 10 элементов
        vector_values = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
        expected_results = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        # Записываем вектор в память (адреса 500-509)
        for i, value in enumerate(vector_values):
            self.interpreter.memory[500 + i] = value
        
        # Симулируем вычисление sqrt для каждого элемента
        for i in range(10):
            src_addr = 500 + i
            self.interpreter.acc = src_addr
            self.interpreter.execute_sqrt(src_addr)  # Записываем результат обратно
            
            # Проверяем
            result = self.interpreter.memory[src_addr]
            expected = expected_results[i]
            self.assertEqual(result, expected,
                           f"Элемент {i}: √{vector_values[i]} = {result}, ожидалось {expected}")
        
        print("✓ Поэлементное вычисление sqrt над вектором работает")
    
    def test_sqrt_edge_cases(self):
        """Тест граничных случаев для sqrt"""
        edge_cases = [
            (0, 0),      # √0
            (1, 1),      # √1
            (2, 1),      # √2 ≈ 1.414 → целая часть = 1
            (3, 1),      # √3 ≈ 1.732 → целая часть = 1
            (15, 3),     # √15 ≈ 3.873 → целая часть = 3
            (255, 15),   # √255 ≈ 15.968 → целая часть = 15
            (1000, 31),  # √1000 ≈ 31.622 → целая часть = 31
        ]
        
        for i, (value, expected) in enumerate(edge_cases):
            src_addr = 600 + i
            dst_addr = 700 + i
            
            self.interpreter.memory[src_addr] = value
            self.interpreter.acc = src_addr
            self.interpreter.execute_sqrt(dst_addr)
            
            result = self.interpreter.memory[dst_addr]
            self.assertEqual(result, expected,
                           f"√{value} = {result}, ожидалось {expected}")
        
        print("✓ Граничные случаи sqrt обрабатываются правильно")

def run_stage4_tests():
    """Запуск всех тестов Этапа 4"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИНТЕРПРЕТАТОРА - ЭТАП 4 (АЛУ, SQRT)")
    print("=" * 60)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUVMInterpreterStage4)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ ЭТАПА 4:")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ЭТАПА 4 ПРОЙДЕНЫ!")
        print("Команда sqrt() реализована корректно.")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_stage4_tests()
    
    if success:
        print("\n" + "=" * 60)
        print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ КОМАНДЫ SQRT:")
        print("=" * 60)
        print("1. Тестирование sqrt:")
        print("   python uvm_interp.py --test-sqrt")
        print()
        print("2. Создание тестовой программы:")
        print("   python uvm_asm.py sqrt_test.json sqrt.bin --binary")
        print()
        print("3. Запуск с инициализацией памяти:")
        print("   python uvm_interp.py sqrt.bin result.json 0 300 --init-memory init_memory.json --verbose")
        print()
        print("4. Обработка вектора:")
        print("   python uvm_asm.py vector_sqrt.json vector.bin --binary")
        print("   python uvm_interp.py vector.bin vector_result.json 0 600 --init-memory init_memory.json")
    
    sys.exit(0 if success else 1)
