#!/usr/bin/env python3
"""
Тесты для ассемблера (Этап 1)
"""

import unittest
import tempfile
import json
import os
from uvm_asm import UVMAssemblerStage1

class TestUVMAssemblerStage1(unittest.TestCase):
    
    def setUp(self):
        self.assembler = UVMAssemblerStage1()
    
    def test_load_const(self):
        """Тест команды LOAD_CONST"""
        program = [{"opcode": "LOAD_CONST", "operand": 520}]
        intermediate = self.assembler.translate_to_intermediate(program)
        
        self.assertEqual(len(intermediate), 1)
        self.assertEqual(intermediate[0].opcode, 10)  # A=10
        self.assertEqual(intermediate[0].operand, 520)  # B=520
    
    def test_all_commands(self):
        """Тест всех команд из спецификации"""
        program = [
            {"opcode": "LOAD_CONST", "operand": 520},
            {"opcode": "LOAD_MEM", "operand": 133},
            {"opcode": "STORE_MEM", "operand": 167},
            {"opcode": "SQRT", "operand": 954}
        ]
        
        intermediate = self.assembler.translate_to_intermediate(program)
        
        expected = [(10, 520), (0, 133), (14, 167), (2, 954)]
        
        for i, (exp_a, exp_b) in enumerate(expected):
            self.assertEqual(intermediate[i].opcode, exp_a)
            self.assertEqual(intermediate[i].operand, exp_b)
    
    def test_json_parsing(self):
        """Тест парсинга JSON файла"""
        # Создаем временный JSON файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "program": [
                    {"opcode": "LOAD_CONST", "operand": 100}
                ]
            }, f)
            temp_file = f.name
        
        try:
            program = self.assembler.parse_json_program(temp_file)
            self.assertEqual(len(program), 1)
            self.assertEqual(program[0]['opcode'], 'LOAD_CONST')
            self.assertEqual(program[0]['operand'], 100)
        finally:
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main()
