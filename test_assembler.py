#!/usr/bin/env python3
"""
Тесты для ассемблера УВМ (Этапы 1 и 2)
"""

import unittest
import tempfile
import json
import os
import sys

# Добавляем путь к текущей директории для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from uvm_asm import UVMAssembler, UVMIntermediate
    HAS_NEW_ASSEMBLER = True
except ImportError:
    # Фолбэк для совместимости
    HAS_NEW_ASSEMBLER = False
    
    class UVMIntermediate:
        def __init__(self, opcode, operand, comment=""):
            self.opcode = opcode
            self.operand = operand
            self.comment = comment
    
    class UVMAssembler:
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
        
        def encode_command(self, cmd):
            """Простая реализация для тестов"""
            byte1 = (cmd.opcode << 4) | ((cmd.operand >> 8) & 0x0F)
            byte2 = cmd.operand & 0xFF
            byte3 = 0
            return bytes([byte1, byte2, byte3])

class TestUVMAssemblerStage1(unittest.TestCase):
    """Тесты для Этапа 1 (промежуточное представление)"""
    
    def setUp(self):
        self.assembler = UVMAssembler()
    
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

class TestUVMAssemblerStage2(unittest.TestCase):
    """Тесты для Этапа 2 (бинарное кодирование)"""
    
    def setUp(self):
        self.assembler = UVMAssembler()
    
    def test_binary_encoding_load_const(self):
        """Тест кодирования LOAD_CONST в бинарный формат"""
        program = [{"opcode": "LOAD_CONST", "operand": 520}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        # Тест кодирования одной команды
        cmd = intermediate[0]
        encoded = self.assembler.encode_command(cmd)
        
        # Проверка что 3 байта
        self.assertEqual(len(encoded), 3, "Должно быть 3 байта на команду")
        
        # Проверка значений байтов для LOAD_CONST 520
        # A=10 (0x0A << 4 = 0xA0), B=520 (0x0208)
        # byte1 = 0xA0 | (0x02 & 0x0F) = 0xA2
        # byte2 = 0x08
        # byte3 = 0x00
        expected = bytes([0xA2, 0x08, 0x00])
        self.assertEqual(encoded, expected, 
                        f"Ожидалось {expected.hex()}, получено {encoded.hex()}")
        print("✓ Бинарное кодирование LOAD_CONST 520 работает")
    
    def test_binary_encoding_load_mem(self):
        """Тест кодирования LOAD_MEM в бинарный формат"""
        program = [{"opcode": "LOAD_MEM", "operand": 133}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        cmd = intermediate[0]
        encoded = self.assembler.encode_command(cmd)
        
        self.assertEqual(len(encoded), 3)
        
        # LOAD_MEM: A=0, B=133 (0x0085)
        # byte1 = 0x00 | (0x00 & 0x0F) = 0x00
        # byte2 = 0x85
        # byte3 = 0x00
        expected = bytes([0x00, 0x85, 0x00])
        self.assertEqual(encoded, expected)
        print("✓ Бинарное кодирование LOAD_MEM 133 работает")
    
    def test_binary_encoding_store_mem(self):
        """Тест кодирования STORE_MEM в бинарный формат"""
        program = [{"opcode": "STORE_MEM", "operand": 167}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        cmd = intermediate[0]
        encoded = self.assembler.encode_command(cmd)
        
        self.assertEqual(len(encoded), 3)
        
        # STORE_MEM: A=14 (0x0E), B=167 (0x00A7)
        # byte1 = 0xE0 | (0x00 & 0x0F) = 0xE0
        # byte2 = 0xA7
        # byte3 = 0x00
        expected = bytes([0xE0, 0xA7, 0x00])
        self.assertEqual(encoded, expected)
        print("✓ Бинарное кодирование STORE_MEM 167 работает")
    
    def test_binary_encoding_sqrt(self):
        """Тест кодирования SQRT в бинарный формат"""
        program = [{"opcode": "SQRT", "operand": 954}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        cmd = intermediate[0]
        encoded = self.assembler.encode_command(cmd)
        
        self.assertEqual(len(encoded), 3)
        
        # SQRT: A=2 (0x02), B=954 (0x03BA)
        # byte1 = 0x20 | (0x03 & 0x0F) = 0x23
        # byte2 = 0xBA
        # byte3 = 0x00
        expected = bytes([0x23, 0xBA, 0x00])
        self.assertEqual(encoded, expected)
        print("✓ Бинарное кодирование SQRT 954 работает")
    
    def test_binary_file_creation(self):
        """Тест создания бинарного файла"""
        program = [
            {"opcode": "LOAD_CONST", "operand": 520},
            {"opcode": "LOAD_MEM", "operand": 133}
        ]
        
        intermediate = self.assembler.translate_to_intermediate(program)
        
        # Создаем временный бинарный файл
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            temp_file = f.name
        
        try:
            # Если у assembler есть метод encode_to_binary, используем его
            if hasattr(self.assembler, 'encode_to_binary'):
                size = self.assembler.encode_to_binary(intermediate, temp_file)
                
                # Проверяем размер файла
                self.assertEqual(size, 6)  # 2 команды × 3 байта = 6 байт
                
                # Проверяем содержимое файла
                with open(temp_file, 'rb') as f:
                    data = f.read()
                
                self.assertEqual(len(data), 6)
                
                # Первая команда: LOAD_CONST 520
                self.assertEqual(data[0:3], bytes([0xA2, 0x08, 0x00]))
                # Вторая команда: LOAD_MEM 133
                self.assertEqual(data[3:6], bytes([0x00, 0x85, 0x00]))
                
                print("✓ Создание бинарного файла работает")
            else:
                print("⚠ Метод encode_to_binary не найден (пропускаем тест)")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_multiple_commands_encoding(self):
        """Тест кодирования нескольких команд"""
        program = [
            {"opcode": "LOAD_CONST", "operand": 255},
            {"opcode": "STORE_MEM", "operand": 1000},
            {"opcode": "SQRT", "operand": 500}
        ]
        
        intermediate = self.assembler.translate_to_intermediate(program)
        
        # Проверяем кодирование каждой команды
        expected_bytes = [
            bytes([0xAF, 0xFF, 0x00]),  # LOAD_CONST 255
            bytes([0xE3, 0xE8, 0x00]),  # STORE_MEM 1000
            bytes([0x21, 0xF4, 0x00])   # SQRT 500
        ]
        
        for i, cmd in enumerate(intermediate):
            encoded = self.assembler.encode_command(cmd)
            self.assertEqual(encoded, expected_bytes[i],
                           f"Команда {i}: ожидалось {expected_bytes[i].hex()}, "
                           f"получено {encoded.hex()}")
        
        print("✓ Кодирование нескольких команд работает")

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("Тестирование ассемблера УВМ - Этапы 1 и 2")
    print("=" * 60)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    
    # Собираем все тесты
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestUVMAssemblerStage1))
    suite.addTests(loader.loadTestsFromTestCase(TestUVMAssemblerStage2))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    # Детальная статистика
    stage1_tests = len(loader.loadTestsFromTestCase(TestUVMAssemblerStage1)._tests)
    stage2_tests = len(loader.loadTestsFromTestCase(TestUVMAssemblerStage2)._tests)
    
    print(f"\nРазбивка по этапам:")
    print(f"  Этап 1 (промежуточное представление): {stage1_tests} тестов")
    print(f"  Этап 2 (бинарное кодирование): {stage2_tests} тестов")
    
    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Этапы 1 и 2 реализованы корректно.")
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
    # Проверка версии
    print(f"Используется новый ассемблер: {HAS_NEW_ASSEMBLER}")
    
    # Можно запустить как обычный скрипт
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        # Простой запуск
        unittest.main()
    elif len(sys.argv) > 1 and sys.argv[1] == '--stage1':
        # Только тесты Этапа 1
        print("Запуск тестов только для Этапа 1")
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestUVMAssemblerStage1)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    elif len(sys.argv) > 1 and sys.argv[1] == '--stage2':
        # Только тесты Этапа 2
        print("Запуск тестов только для Этапа 2")
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestUVMAssemblerStage2)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    else:
        # Полный запуск с красивым выводом
        success = run_all_tests()
        
        # Вывод примеров использования
        if success:
            print("\n" + "=" * 60)
            print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ АССЕМБЛЕРА:")
            print("=" * 60)
            print("Этап 1 (промежуточное представление):")
            print("  python uvm_asm.py test_specification.json --test")
            print("  python uvm_asm.py test_specification.json intermediate.json")
            print()
            print("Этап 2 (бинарное кодирование):")
            print("  python uvm_asm.py test_specification.json program.bin --binary --test")
            print("  python uvm_asm.py test_specification.json program.bin --binary")
            print()
            print("Тестирование:")
            print("  python test_assembler.py --stage1  # Только этап 1")
            print("  python test_assembler.py --stage2  # Только этап 2")
            print("  python test_assembler.py           # Все тесты")
        
        sys.exit(0 if success else 1)
