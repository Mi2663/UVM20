#!/usr/bin/env python3
"""
Ассемблер для УВМ (вариант 20)
"""

import json
import struct
import sys

class UVMAssembler:
    def __init__(self):
        self.commands = {
            'LOAD_CONST': 10,
            'LOAD_MEM': 0,
            'STORE_MEM': 14,
            'SQRT': 2
        }
    
    def assemble(self, input_file, output_file, test_mode=False):
        """Ассемблировать программу из JSON файла"""
        try:
            with open(input_file, 'r') as f:
                program = json.load(f)
            
            binary_code = bytearray()
            
            for instruction in program.get('program', []):
                opcode = self.commands.get(instruction['opcode'])
                operand = instruction['operand']
                
                # Формирование 3-байтовой команды
                cmd_bytes = self._encode_command(opcode, operand)
                binary_code.extend(cmd_bytes)
                
                if test_mode:
                    print(f"A={opcode}, B={operand}")
            
            with open(output_file, 'wb') as f:
                f.write(binary_code)
            
            print(f"Программа успешно ассемблирована: {len(binary_code)} байт")
            return True
            
        except Exception as e:
            print(f"Ошибка ассемблирования: {e}")
            return False
    
    def _encode_command(self, opcode, operand):
        """Кодировать команду в 3 байта"""
        # Формат: [AAAA BBBB] [BBBB BBBB] [BBBB BBBB]
        byte1 = (opcode << 4) | ((operand >> 8) & 0x0F)
        byte2 = operand & 0xFF
        byte3 = 0  # Для 13-битных операндов можно использовать
        
        return bytes([byte1, byte2, byte3])

def main():
    if len(sys.argv) < 3:
        print("Использование: python uvm_asm.py <входной.json> <выходной.bin> [--test]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = '--test' in sys.argv
    
    assembler = UVMAssembler()
    assembler.assemble(input_file, output_file, test_mode)

if __name__ == '__main__':
    main()
