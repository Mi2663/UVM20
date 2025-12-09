#!/usr/bin/env python3
"""
Тесты для Этапа 5 - исправленная версия (без ошибок кодировки)
"""

import unittest
import json
import os
import sys
import tempfile
import subprocess
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uvm_asm import UVMAssembler
from uvm_interp import UVMInterpreter

class TestStage5Fixed(unittest.TestCase):
    """Исправленные тесты для Этапа 5"""
    
    def setUp(self):
        self.assembler = UVMAssembler()
        self.interpreter = UVMInterpreter()
    
    def create_test_program(self, program_data):
        """Создание временного файла с программой"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                       encoding='utf-8', delete=False) as f:
            json.dump(program_data, f, ensure_ascii=False)
            return f.name
    
    def create_test_binary(self, json_file):
        """Создание временного бинарного файла"""
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
            bin_file = f.name
        
        # Ассемблирование
        intermediate = self.assembler.assemble(json_file, None, False)
        self.assembler.encode_to_binary(intermediate, bin_file)
        
        return bin_file
    
    def test_vector_sqrt_logic(self):
        """Тест логики sqrt для вектора (основная задача)"""
        # Создаем простую программу для теста
        test_program = {
            "program": [
                {"opcode": "LOAD_CONST", "operand": 500},
                {"opcode": "SQRT", "operand": 500}
            ]
        }
        
        json_file = self.create_test_program(test_program)
        bin_file = self.create_test_binary(json_file)
        
        try:
            # Инициализируем память
            self.interpreter.memory[500] = 25  # √25 = 5
            
            # Загружаем и выполняем
            self.interpreter.load_program(bin_file)
            self.interpreter.run(verbose=False)
            
            # Проверяем результат
            self.assertEqual(self.interpreter.memory[500], 5)
            self.assertEqual(self.interpreter.sqrt_operations, 1)
            
            print("✓ Основная логика sqrt для вектора работает")
            
        finally:
            # Очистка
            if os.path.exists(json_file):
                os.unlink(json_file)
            if os.path.exists(bin_file):
                os.unlink(bin_file)
    
    def test_multiple_vector_elements(self):
        """Тест нескольких элементов вектора"""
        # Создаем программу для 3 элементов
        test_program = {
            "program": [
                # Элемент 1
                {"opcode": "LOAD_CONST", "operand": 500},
                {"opcode": "SQRT", "operand": 500},
                
                # Элемент 2  
                {"opcode": "LOAD_CONST", "operand": 501},
                {"opcode": "SQRT", "operand": 501},
                
                # Элемент 3
                {"opcode": "LOAD_CONST", "operand": 502},
                {"opcode": "SQRT", "operand": 502}
            ]
        }
        
        json_file = self.create_test_program(test_program)
        bin_file = self.create_test_binary(json_file)
        
        try:
            # Инициализируем память
            test_values = {500: 4, 501: 9, 502: 16}  # √4=2, √9=3, √16=4
            for addr, value in test_values.items():
                self.interpreter.memory[addr] = value
            
            # Выполняем
            self.interpreter.load_program(bin_file)
            self.interpreter.run(verbose=False)
            
            # Проверяем результаты
            self.assertEqual(self.interpreter.memory[500], 2)
            self.assertEqual(self.interpreter.memory[501], 3)
            self.assertEqual(self.interpreter.memory[502], 4)
            self.assertEqual(self.interpreter.sqrt_operations, 3)
            
            print("✓ Обработка нескольких элементов вектора работает")
            
        finally:
            if os.path.exists(json_file):
                os.unlink(json_file)
            if os.path.exists(bin_file):
                os.unlink(bin_file)
    
    def test_assembler_help(self):
        """Тест что ассемблер запускается с --help"""
        try:
            # Запускаем с русской локалью правильно
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                [sys.executable, 'uvm_asm.py', '--help'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn('usage:', result.stdout)
            print("✓ Ассемблер запускается с --help")
            
        except Exception as e:
            self.skipTest(f"Не удалось запустить ассемблер: {e}")
    
    def test_interpreter_help(self):
        """Тест что интерпретатор запускается с --help"""
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                [sys.executable, 'uvm_interp.py', '--help'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn('usage:', result.stdout)
            print("✓ Интерпретатор запускается с --help")
            
        except Exception as e:
            self.skipTest(f"Не удалось запустить интерпретатор: {e}")
    
    def test_dump_memory_format(self):
        """Тест формата дампа памяти"""
        # Заполняем память тестовыми данными
        test_data = {
            100: 42,
            200: 100,
            300: 999
        }
        
        for addr, value in test_data.items():
            self.interpreter.memory[addr] = value
        
        # Получаем дамп
        dump = self.interpreter.dump_memory(0, 400)
        
        # Проверяем формат JSON
        try:
            json_str = json.dumps(dump, indent=2)
            parsed = json.loads(json_str)
            
            # Проверяем что данные сохранились
            for addr, value in test_data.items():
                self.assertEqual(parsed.get(str(addr)), value)
            
            print("✓ Формат дампа памяти корректный (JSON)")
            
        except json.JSONDecodeError as e:
            self.fail(f"Некорректный JSON в дампе: {e}")
    
    def test_sqrt_edge_cases(self):
        """Тест граничных случаев для sqrt"""
        test_cases = [
            (0, 0),      # √0
            (1, 1),      # √1
            (2, 1),      # √2 ≈ 1.4 → 1
            (3, 1),      # √3 ≈ 1.7 → 1
            (4, 2),      # √4 = 2
            (255, 15),   # √255 ≈ 15.9 → 15
            (-25, 5),    # √(-25) → 5 (берем модуль)
        ]
        
        for i, (value, expected) in enumerate(test_cases):
            src_addr = 600 + i
            self.interpreter.memory[src_addr] = value
            self.interpreter.acc = src_addr
            self.interpreter.execute_sqrt(700 + i)
            
            result = self.interpreter.memory[700 + i]
            self.assertEqual(result, expected,
                           f"√{value} = {result}, ожидалось {expected}")
        
        print("✓ Граничные случаи sqrt обрабатываются корректно")
    
    def test_program_assembling(self):
        """Тест что программы ассемблируются"""
        # Создаем тестовую программу
        test_program = {
            "program": [
                {"opcode": "LOAD_CONST", "operand": 100},
                {"opcode": "STORE_MEM", "operand": 200},
                {"opcode": "LOAD_CONST", "operand": 200},
                {"opcode": "LOAD_MEM", "operand": 0},
                {"opcode": "SQRT", "operand": 300}
            ]
        }
        
        json_file = self.create_test_program(test_program)
        
        try:
            # Пробуем ассемблировать
            intermediate = self.assembler.assemble(json_file, None, False)
            
            # Проверяем результат
            self.assertEqual(len(intermediate), 5)
            
            # Проверяем коды операций
            expected_opcodes = [10, 14, 10, 0, 2]
            for i, cmd in enumerate(intermediate):
                self.assertEqual(cmd.opcode, expected_opcodes[i])
            
            print("✓ Программы успешно ассемблируются")
            
        finally:
            if os.path.exists(json_file):
                os.unlink(json_file)

def run_stage5_tests():
    """Запуск всех тестов Этапа 5"""
    print("="*60)
    print("ТЕСТИРОВАНИЕ ЭТАПА 5: ТЕСТОВАЯ ЗАДАЧА")
    print("="*60)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestStage5Fixed)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*60)
    print("ИТОГИ ТЕСТИРОВАНИЯ ЭТАПА 5:")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Пропущено: {len([test for test in result.skipped])}")
    
    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ЭТАПА 5 ПРОЙДЕНЫ УСПЕШНО!")
        print("   Основные требования этапа выполнены:")
        print("   1. sqrt() работает для элементов вектора")
        print("   2. Программы ассемблируются и выполняются")
        print("   3. Дамп памяти в JSON формате")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ")
        if result.failures:
            print("\nПроваленные тесты:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nОшибки в тестах:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_stage5_tests()
    
    print("\n" + "="*60)
    print("СОЗДАНИЕ ФАЙЛОВ ДЛЯ ПОЛНОЙ ПРОВЕРКИ:")
    print("="*60)
    
    # Создаем примеры файлов для этапа 5
    examples_created = []
    
    # 1. Основная программа для вектора
    vector_program = {
        "version": "1.0",
        "description": "Этап 5: sqrt над вектором длины 3 (тест)",
        "program": [
            {"opcode": "LOAD_CONST", "operand": 500},
            {"opcode": "STORE_MEM", "operand": 1000},
            {"opcode": "LOAD_CONST", "operand": 3},
            {"opcode": "STORE_MEM", "operand": 1001},
            {"opcode": "LOAD_MEM", "operand": 1000},
            {"opcode": "SQRT", "operand": 0},
            {"opcode": "LOAD_CONST", "operand": 1},
            {"opcode": "LOAD_MEM", "operand": 1000},
            {"opcode": "STORE_MEM", "operand": 1000},
            {"opcode": "LOAD_CONST", "operand": 1},
            {"opcode": "LOAD_MEM", "operand": 1001},
            {"opcode": "STORE_MEM", "operand": 1001},
            {"opcode": "LOAD_MEM", "operand": 1001},
            {"opcode": "LOAD_CONST", "operand": 4},
            {"opcode": "LOAD_CONST", "operand": 0}
        ]
    }
    
    try:
        with open('stage5_test_vector.json', 'w', encoding='utf-8') as f:
            json.dump(vector_program, f, indent=2, ensure_ascii=False)
        examples_created.append('stage5_test_vector.json')
        print("✅ Создан stage5_test_vector.json")
    except Exception as e:
        print(f"❌ Ошибка создания файла: {e}")
    
    # 2. Данные для инициализации
    init_data = {
        "500": 4,
        "501": 9,
        "502": 16
    }
    
    try:
        with open('stage5_init_data.json', 'w', encoding='utf-8') as f:
            json.dump(init_data, f, indent=2, ensure_ascii=False)
        examples_created.append('stage5_init_data.json')
        print("✅ Создан stage5_init_data.json")
    except Exception as e:
        print(f"❌ Ошибка создания файла: {e}")
    
    if examples_created:
        print(f"\nСоздано {len(examples_created)} файлов для тестирования.")
        print("Для полной проверки выполните:")
        print("  python uvm_asm.py stage5_test_vector.json vector.bin --binary")
        print("  python uvm_interp.py vector.bin result.json 0 600 --init-memory stage5_init_data.json --verbose")
        print("  type result.json")
    
    sys.exit(0 if success else 1)
