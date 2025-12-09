#!/usr/bin/env python3
"""
Ассемблер УВМ - Этапы 1 и 2
Этап 1: Перевод в промежуточное представление
Этап 2: Генерация машинного кода
"""

import json
import sys
import argparse
import os
from typing import List, Dict

class UVMIntermediate:
    """Промежуточное представление команды"""
    def __init__(self, opcode: int, operand: int, comment: str = ""):
        self.opcode = opcode  # Поле A
        self.operand = operand  # Поле B
        self.comment = comment
    
    def __repr__(self):
        return f"A={self.opcode}, B={self.operand}  # {self.comment}"

class UVMAssembler:
    """Ассемблер для УВМ (Этапы 1 и 2)"""
    
    # Таблица мнемоник -> коды операций
    OPCODES = {
        'LOAD_CONST': 10,
        'LOAD_MEM': 0,
        'STORE_MEM': 14,
        'SQRT': 2
    }
    
    def __init__(self):
        self.intermediate_code: List[UVMIntermediate] = []
    
    # === ЭТАП 1: ПАРСИНГ И ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ===
    
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
        """Трансляция в промежуточное представление (Этап 1)"""
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
    
    # === ЭТАП 2: ГЕНЕРАЦИЯ МАШИННОГО КОДА ===
    
    def encode_command(self, cmd: UVMIntermediate) -> bytes:
        """Кодирование одной команды в 3 байта"""
        # Формат: [AAAA BBBB] [BBBB BBBB] [BBBB BBBB]
        # A: 4 бита, B: 12-13 бит
        
        # ПРАВИЛЬНЫЙ РАСЧЕТ:
        # byte1 = (opcode << 4) | ((operand >> 8) & 0x0F)
        # byte2 = operand & 0xFF
        # byte3 = 0
        
        byte1 = (cmd.opcode << 4) | ((cmd.operand >> 8) & 0x0F)
        byte2 = cmd.operand & 0xFF
        byte3 = 0
        
        return bytes([byte1, byte2, byte3])
    
    def encode_to_binary(self, intermediate: List[UVMIntermediate], output_file: str) -> int:
        """Кодирование промежуточного представления в бинарный файл"""
        binary_data = bytearray()
        
        for cmd in intermediate:
            cmd_bytes = self.encode_command(cmd)
            binary_data.extend(cmd_bytes)
        
        # Запись в файл
        with open(output_file, 'wb') as f:
            f.write(binary_data)
        
        size = len(binary_data)
        return size
    
    def display_binary(self, binary_file: str):
        """Вывод бинарного файла в байтовом формате"""
        with open(binary_file, 'rb') as f:
            data = f.read()
        
        print("Байтовое представление программы:")
        print("-" * 50)
        
        # Вывод по 3 байта (одна команда)
        for i in range(0, len(data), 3):
            cmd_bytes = data[i:i+3]
            if len(cmd_bytes) == 3:
                hex_str = ' '.join(f'{b:02X}' for b in cmd_bytes)
                print(f"Команда {i//3}: {hex_str}")
        
        print("-" * 50)
        print(f"Всего байт: {len(data)}")
        print(f"Всего команд: {len(data) // 3}")
    
    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    
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
    
    # === ОСНОВНОЙ МЕТОД АССЕМБЛИРОВАНИЯ ===
    
    def assemble(self, input_file: str, output_file: str = None, 
                 test_mode: bool = False, binary_mode: bool = False):
        """Основной метод ассемблирования"""
        # 1. Парсинг JSON
        program = self.parse_json_program(input_file)
        
        # 2. Трансляция в промежуточное представление
        intermediate = self.translate_to_intermediate(program)
        self.intermediate_code = intermediate
        
        # 3. Вывод в тестовом режиме (Этап 1)
        if test_mode:
            if binary_mode:
                # Этап 2: Вывод байтового представления
                print("=== РЕЖИМ ТЕСТИРОВАНИЯ (ЭТАП 2) ===")
                print("Байтовое представление команд:")
                print("-" * 30)
                
                for i, cmd in enumerate(intermediate):
                    cmd_bytes = self.encode_command(cmd)
                    hex_str = ' '.join(f'{b:02X}' for b in cmd_bytes)
                    print(f"Команда {i}: {hex_str}  # A={cmd.opcode}, B={cmd.operand}")
                
                print("-" * 30)
            else:
                # Этап 1: Вывод промежуточного представления
                print("=== РЕЖИМ ТЕСТИРОВАНИЯ (ЭТАП 1) ===")
                self.display_intermediate(intermediate)
                
                # Проверка тестов из спецификации
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
        
        # 4. Генерация выходного файла
        if output_file:
            if binary_mode:
                # Этап 2: Генерация бинарного файла
                size = self.encode_to_binary(intermediate, output_file)
                print(f"\nБинарный файл создан: {output_file}")
                print(f"Размер файла: {size} байт")
                
                if test_mode:
                    self.display_binary(output_file)
            else:
                # Этап 1: Сохранение промежуточного представления
                self.save_intermediate(intermediate, output_file)
        
        return intermediate

def main():
    parser = argparse.ArgumentParser(
        description='Ассемблер УВМ - Этапы 1 и 2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  Этап 1: python uvm_asm.py program.json --test
  Этап 1: python uvm_asm.py program.json intermediate.json
  Этап 2: python uvm_asm.py program.json program.bin --binary --test
  Этап 2: python uvm_asm.py program.json program.bin --binary
        """
    )
    parser.add_argument('input', help='Входной JSON файл с программой')
    parser.add_argument('output', nargs='?', help='Выходной файл')
    parser.add_argument('--test', action='store_true', help='Режим тестирования')
    parser.add_argument('--binary', action='store_true', 
                       help='Генерация бинарного файла (Этап 2)')
    
    args = parser.parse_args()
    
    # Проверка расширения файла
    if args.output and args.binary and not args.output.endswith(('.bin', '.uvm')):
        print("Предупреждение: для бинарного режима рекомендуется использовать расширения .bin или .uvm")
    
    assembler = UVMAssembler()
    assembler.assemble(args.input, args.output, args.test, args.binary)

if __name__ == '__main__':
    main()
