#!/usr/bin/env python3
"""
Ассемблер УВМ (Этап 1) - Перевод в промежуточное представление
"""

import json
import sys
import argparse
from typing import List, Dict, Tuple

class UVMIntermediate:
    """Промежуточное представление команды"""
    def __init__(self, opcode: int, operand: int, comment: str = ""):
        self.opcode = opcode  # Поле A
        self.operand = operand  # Поле B
        self.comment = comment
    
    def __repr__(self):
        return f"A={self.opcode}, B={self.operand}  # {self.comment}"

class UVMAssemblerStage1:
    """Ассемблер для Этапа 1"""
    
    # Таблица мнемоник -> коды операций
    OPCODES = {
        'LOAD_CONST': 10,
        'LOAD_MEM': 0,
        'STORE_MEM': 14,
        'SQRT': 2
    }
    
    def __init__(self):
        self.intermediate_code: List[UVMIntermediate] = []
    
    def parse_json_program(self, json_file: str) -> List[Dict]:
        """Парсинг JSON программы"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'program' not in data:
                raise ValueError("JSON должен содержать поле 'program'")
            
            return data['program']
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Файл не найден: {json_file}")
            sys.exit(1)
    
    def translate_to_intermediate(self, program: List[Dict]) -> List[UVMIntermediate]:
        """Трансляция в промежуточное представление"""
        intermediate = []
        
        for i, instr in enumerate(program):
            mnemonic = instr.get('opcode', '').upper()
            
            if mnemonic not in self.OPCODES:
                raise ValueError(f"Неизвестная команда: {mnemonic}")
            
            opcode = self.OPCODES[mnemonic]
            operand = instr.get('operand', 0)
            comment = instr.get('comment', f'команда {i+1}')
            
            # Проверка диапазонов операндов
            if mnemonic in ['LOAD_CONST', 'LOAD_MEM']:
                # 13 бит: 0-8191
                if not (0 <= operand <= 8191):
                    print(f"Предупреждение: операнд {operand} выходит за 13-битный диапазон")
            else:
                # 12 бит: 0-4095
                if not (0 <= operand <= 4095):
                    print(f"Предупреждение: операнд {operand} выходит за 12-битный диапазон")
            
            intermediate.append(UVMIntermediate(opcode, operand, comment))
        
        return intermediate
    
    def display_intermediate(self, intermediate: List[UVMIntermediate]):
        """Вывод промежуточного представления (режим тестирования)"""
        print("Промежуточное представление программы:")
        print("-" * 40)
        for cmd in intermediate:
            print(cmd)
        print("-" * 40)
        print(f"Всего команд: {len(intermediate)}")
    
    def save_intermediate(self, intermediate: List[UVMIntermediate], output_file: str):
        """Сохранение промежуточного представления в файл"""
        data = []
        for cmd in intermediate:
            data.append({
                'A': cmd.opcode,
                'B': cmd.operand,
                'comment': cmd.comment
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Промежуточное представление сохранено в: {output_file}")
    
    def assemble(self, input_file: str, output_file: str = None, test_mode: bool = False):
        """Основной метод ассемблирования"""
        # 1. Парсинг JSON
        program = self.parse_json_program(input_file)
        
        # 2. Трансляция в промежуточное представление
        intermediate = self.translate_to_intermediate(program)
        self.intermediate_code = intermediate
        
        # 3. Вывод в тестовом режиме
        if test_mode:
            self.display_intermediate(intermediate)
        
        # 4. Сохранение (если указан выходной файл)
        if output_file:
            if output_file.endswith('.json'):
                self.save_intermediate(intermediate, output_file)
            else:
                print("Для Этапа 1 выходной файл должен быть .json")
        
        return intermediate

def main():
    parser = argparse.ArgumentParser(description='Ассемблер УВМ - Этап 1')
    parser.add_argument('input', help='Входной JSON файл с программой')
    parser.add_argument('output', nargs='?', help='Выходной файл для промежуточного представления')
    parser.add_argument('--test', action='store_true', help='Режим тестирования')
    
    args = parser.parse_args()
    
    assembler = UVMAssemblerStage1()
    intermediate = assembler.assemble(args.input, args.output, args.test)
    
    # Проверка тестов из спецификации
    if args.test:
        print("\nПроверка тестовых случаев из спецификации:")
        test_cases = [
            (10, 520, "LOAD_CONST"),
            (0, 133, "LOAD_MEM"),
            (14, 167, "STORE_MEM"),
            (2, 954, "SQRT")
        ]
        
        for i, (expected_a, expected_b, mnemonic) in enumerate(test_cases):
            if i < len(intermediate):
                cmd = intermediate[i]
                if cmd.opcode == expected_a and cmd.operand == expected_b:
                    print(f"✓ Тест {mnemonic}: A={cmd.opcode}, B={cmd.operand} - OK")
                else:
                    print(f"✗ Тест {mnemonic}: ожидалось A={expected_a}, B={expected_b}, получено A={cmd.opcode}, B={cmd.operand}")

if __name__ == '__main__':
    main()
