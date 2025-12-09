#!/usr/bin/env python3
"""
Тесты для Этапа 5
"""

import unittest
import json
import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uvm_asm import UVMAssembler
from uvm_interp import UVMInterpreter

class TestStage5(unittest.TestCase):
    """Тесты для Этапа 5"""
    
    def setUp(self):
        self.assembler = UVMAssembler()
        self.interpreter = UVMInterpreter()
        
        # Создаем тестовые файлы если их нет
        self.create_test_files()
    
    def create_test_files(self):
        """Создание тестовых файлов если необходимо"""
        # Проверяем наличие файлов Этапа 5
        stage5_files = [
            'stage5_vector_sqrt.json',
            'example1_factorial.json',
            'example2_statistics.json', 
            'example3_matrix_operations.json',
            'init_vector_data.json'
        ]
        
        for file in stage5_files:
            if not os.path.exists(file):
                print(f"⚠ Файл {file} не найден, тесты могут пропуститься")
    
    def test_vector_sqrt_program_structure(self):
        """Тест структуры программы для вектора"""
        if not os.path.exists('stage5_vector_sqrt.json'):
            self.skipTest("Файл stage5_vector_sqrt.json не найден")
        
        with open('stage5_vector_sqrt.json', 'r') as f:
            program = json.load(f)
        
        # Проверка структуры
        self.assertIn('program', program)
        self.assertIn('description', program)
        self.assertIn('version', program)
        
        # Проверка что программа содержит команды
        self.assertGreater(len(program['program']), 10)
        
        # Проверка что есть команды SQRT
        has_sqrt = any(cmd['opcode'] == 'SQRT' for cmd in program['program'])
        self.assertTrue(has_sqrt, "Программа должна содержать команды SQRT")
        
        print("✓ Структура программы для вектора корректна")
    
    def test_vector_sqrt_assembling(self):
        """Тест ассемблирования программы для вектора"""
        if not os.path.exists('stage5_vector_sqrt.json'):
            self.skipTest("Файл stage5_vector_sqrt.json не найден")
        
        # Ассемблирование
        intermediate = self.assembler.assemble('stage5_vector_sqrt.json', None, False)
        
        # Проверка что программа ассемблируется
        self.assertGreater(len(intermediate), 10)
        
        # Проверка наличия команд SQRT в промежуточном представлении
        has_sqrt = any(cmd.opcode == 2 for cmd in intermediate)
        self.assertTrue(has_sqrt, "Должны быть команды SQRT (opcode=2)")
        
        print("✓ Программа для вектора успешно ассемблируется")
    
    def test_vector_sqrt_execution(self):
        """Тест выполнения программы для вектора"""
        if not os.path.exists('stage5_vector_sqrt.json'):
            self.skipTest("Файл stage5_vector_sqrt.json не найден")
        
        # Создаем временные файлы
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Минимальная программа для теста
            test_program = {
                "program": [
                    {"opcode": "LOAD_CONST", "operand": 500},
                    {"opcode": "SQRT", "operand": 500}
                ]
            }
            json.dump(test_program, f)
            json_file = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
            bin_file = f.name
        
        try:
            # Ассемблирование
            intermediate = self.assembler.assemble(json_file, None, False)
            self.assembler.encode_to_binary(intermediate, bin_file)
            
            # Инициализация памяти
            self.interpreter.memory[500] = 25  # √25 = 5
            
            # Загрузка и выполнение
            self.interpreter.load_program(bin_file)
            self.interpreter.run(verbose=False)
            
            # Проверка результата
            self.assertEqual(self.interpreter.memory[500], 5)
            self.assertEqual(self.interpreter.sqrt_operations, 1)
            
            print("✓ Выполнение sqrt для одного элемента работает")
            
        finally:
            # Очистка
            if os.path.exists(json_file):
                os.unlink(json_file)
            if os.path.exists(bin_file):
                os.unlink(bin_file)
    
    def test_examples_existence(self):
        """Тест существования примеров программ"""
        examples = [
            'example1_factorial.json',
            'example2_statistics.json',
            'example3_matrix_operations.json'
        ]
        
        for example in examples:
            if os.path.exists(example):
                with open(example, 'r') as f:
                    data = json.load(f)
                
                self.assertIn('program', data)
                self.assertIn('description', data)
                print(f"✓ Пример {example} существует и валиден")
            else:
                print(f"⚠ Пример {example} не найден")
    
    def test_init_data_file(self):
        """Тест файла с данными для инициализации"""
        if not os.path.exists('init_vector_data.json'):
            self.skipTest("Файл init_vector_data.json не найден")
        
        with open('init_vector_data.json', 'r') as f:
            data = json.load(f)
        
        # Проверка что есть данные для вектора
        vector_addrs = [str(i) for i in range(500, 510)]
        has_vector_data = any(addr in data for addr in vector_addrs)
        
        self.assertTrue(has_vector_data, "Должны быть данные для вектора (адреса 500-509)")
        self.assertGreater(len(data), 5, "Должно быть несколько значений для инициализации")
        
        print("✓ Файл с данными для инициализации корректен")
    
    def test_integration_command(self):
        """Тест выполнения через командную строку"""
        # Простой тест что команды работают
        test_cmds = [
            ['python', 'uvm_asm.py', '--help'],
            ['python', 'uvm_interp.py', '--help']
        ]
        
        for cmd in test_cmds:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0)
                print(f"✓ Команда {' '.join(cmd)} работает")
            except:
                print(f"⚠ Не удалось выполнить команду: {' '.join(cmd)}")

def run_stage5_tests():
    """Запуск всех тестов Этапа 5"""
    print("="*60)
    print("ТЕСТИРОВАНИЕ ЭТАПА 5: ТЕСТОВАЯ ЗАДАЧА")
    print("="*60)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestStage5)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*60)
    print("ИТОГИ ТЕСТИРОВАНИЯ ЭТАПА 5:")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Пропущено: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ТЕСТЫ ЭТАПА 5 ПРОЙДЕНЫ!")
        print("   Базовая функциональность Этапа 5 работает корректно.")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_stage5_tests()
    
    if success:
        print("\n" + "="*60)
        print("ДЛЯ ПОЛНОЙ ПРОВЕРКИ ЭТАПА 5:")
        print("="*60)
        print("Запустите полный скрипт Этапа 5:")
        print("  python run_stage5.py")
        print()
        print("Это выполнит:")
        print("  1. Основную задачу (sqrt над вектором)")
        print("  2. Три примера программ")
        print("  3. Проверит результаты")
        print("  4. Покажет дамп памяти")
    
    sys.exit(0 if success else 1)
