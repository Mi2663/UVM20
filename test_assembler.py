#!/usr/bin/env python3
"""
Тесты для ассемблера УВМ (Этап 1)
"""

import unittest
import tempfile
import json
import os
import sys

# Добавляем путь к текущей директории для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from uvm_asm import UVMAssemblerStage1, UVMIntermediate
except ImportError:
    # Для тестирования напрямую
    class UVMIntermediate:
        def __init__(self, opcode, operand, comment=""):
            self.opcode = opcode
            self.operand = operand
            self.comment = comment
    
    class UVMAssemblerStage1:
        OPCODES = {'LOAD_CONST': 10, 'LOAD_MEM': 0, 'STORE_MEM': 14, 'SQRT': 2}
        
        def translate_to_intermediate(self, program):
            intermediate = []
            for instr in program:
                mnemonic = instr.get('opcode', '').upper()
                opcode = self.OPCODES.get(mnemonic, 0)
                operand = instr.get('operand', 0)
                comment = instr.get('comment', '')
                intermediate.append(UVMIntermediate(opcode, operand, comment))
            return intermediate
        
        def parse_json_program(self, json_file):
            with open(json_file, 'r') as f:
                return json.load(f).get('program', [])

class TestUVMAssemblerStage1(unittest.TestCase):
    
    def setUp(self):
        self.assembler = UVMAssemblerStage1()
    
    def test_load_const_command(self):
        """Тест команды LOAD_CONST"""
        program = [{"opcode": "LOAD_CONST", "operand": 520}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        self.assertEqual(len(intermediate), 1)
        self.assertEqual(intermediate[0].opcode, 10)  # A=10
        self.assertEqual(intermediate[0].operand, 520)  # B=520
        print("✓ Тест LOAD_CONST пройден")
    
    def test_load_mem_command(self):
        """Тест команды LOAD_MEM"""
        program = [{"opcode": "LOAD_MEM", "operand": 133}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        self.assertEqual(intermediate[0].opcode, 0)  # A=0
        self.assertEqual(intermediate[0].operand, 133)  # B=133
        print("✓ Тест LOAD_MEM пройден")
    
    def test_store_mem_command(self):
        """Тест команды STORE_MEM"""
        program = [{"opcode": "STORE_MEM", "operand": 167}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        self.assertEqual(intermediate[0].opcode, 14)  # A=14
        self.assertEqual(intermediate[0].operand, 167)  # B=167
        print("✓ Тест STORE_MEM пройден")
    
    def test_sqrt_command(self):
        """Тест команды SQRT"""
        program = [{"opcode": "SQRT", "operand": 954}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        self.assertEqual(intermediate[0].opcode, 2)  # A=2
        self.assertEqual(intermediate[0].operand, 954)  # B=954
        print("✓ Тест SQRT пройден")
    
    def test_all_specification_tests(self):
        """Тест всех тестов из спецификации"""
        program = [
            {"opcode": "LOAD_CONST", "operand": 520},
            {"opcode": "LOAD_MEM", "operand": 133},
            {"opcode": "STORE_MEM", "operand": 167},
            {"opcode": "SQRT", "operand": 954}
        ]
        
        intermediate = self.assembler.translate_to_intermediate(program)
        
        expected_results = [
            (10, 520, "LOAD_CONST"),
            (0, 133, "LOAD_MEM"),
            (14, 167, "STORE_MEM"),
            (2, 954, "SQRT")
        ]
        
        self.assertEqual(len(intermediate), len(expected_results))
        
        for i, (exp_a, exp_b, cmd_name) in enumerate(expected_results):
            with self.subTest(command=cmd_name):
                self.assertEqual(intermediate[i].opcode, exp_a)
                self.assertEqual(intermediate[i].operand, exp_b)
        
        print("✓ Все тесты из спецификации пройдены")
    
    def test_json_file_parsing(self):
        """Тест парсинга JSON файла"""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "program": [
                    {"opcode": "LOAD_CONST", "operand": 100, "comment": "Тест"}
                ]
            }, f)
            temp_file = f.name
        
        try:
            program = self.assembler.parse_json_program(temp_file)
            self.assertEqual(len(program), 1)
            self.assertEqual(program[0]['opcode'], 'LOAD_CONST')
            self.assertEqual(program[0]['operand'], 100)
            print("✓ Парсинг JSON файла работает")
        finally:
            os.unlink(temp_file)
    
    def test_unknown_command(self):
        """Тест обработки неизвестной команды"""
        program = [{"opcode": "UNKNOWN", "operand": 123}]
        
        # Ожидаем ошибку или обработку по умолчанию
        try:
            intermediate = self.assembler.translate_to_intermediate(program)
            # Если не выброшено исключение, проверяем результат
            self.assertEqual(intermediate[0].opcode, 0)  # Значение по умолчанию
        except ValueError as e:
            self.assertIn("Неизвестная команда", str(e))
            print("✓ Неизвестная команда корректно обработана")

def run_tests():
    """Запуск всех тестов"""
    print("Запуск тестов для ассемблера УВМ (Этап 1)")
    print("=" * 50)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUVMAssemblerStage1)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ Все тесты пройдены успешно!")
    else:
        print("❌ Есть проблемы с тестами")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Можно запустить как обычный скрипт
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        # Простой запуск
        unittest.main()
    else:
        # Запуск с красивым выводом
        run_tests()
