#!/usr/bin/env python3
"""
Интерпретатор для УВМ (вариант 20)
"""

import json
import struct
import sys
import math

class UVMInterpreter:
    def __init__(self, mem_size=65536):
        self.memory = [0] * mem_size  # Память данных
        self.acc = 0  # Аккумулятор
        self.pc = 0   # Счетчик команд
        
    def load_program(self, binary_file):
        """Загрузить программу из бинарного файла"""
        with open(binary_file, 'rb') as f:
            self.program = f.read()
        return len(self.program)
    
    def decode_command(self, offset):
        """Декодировать команду по смещению"""
        if offset + 3 > len(self.program):
            return None
        
        byte1, byte2, byte3 = self.program[offset:offset+3]
        opcode = byte1 >> 4
        operand = ((byte1 & 0x0F) << 8) | byte2
        
        return opcode, operand
    
    def execute(self):
        """Выполнить программу"""
        while self.pc < len(self.program):
            cmd = self.decode_command(self.pc)
            if cmd is None:
                break
                
            opcode, operand = cmd
            
            if opcode == 10:  # LOAD_CONST
                self.acc = operand
            elif opcode == 0:  # LOAD_MEM
                addr = self.acc + operand
                self.acc = self.memory[addr] if addr < len(self.memory) else 0
            elif opcode == 14:  # STORE_MEM
                if operand < len(self.memory):
                    self.memory[operand] = self.acc
            elif opcode == 2:  # SQRT
                src_addr = self.acc
                dst_addr = operand
                if src_addr < len(self.memory) and dst_addr < len(self.memory):
                    value = self.memory[src_addr]
                    self.memory[dst_addr] = int(math.sqrt(abs(value)))
            
            self.pc += 3
    
    def dump_memory(self, start_addr, end_addr):
        """Дамп памяти в указанном диапазоне"""
        dump = {}
        for addr in range(start_addr, min(end_addr, len(self.memory))):
            if self.memory[addr] != 0:
                dump[addr] = self.memory[addr]
        return dump

def main():
    if len(sys.argv) < 4:
        print("Использование: python uvm_interp.py <program.bin> <dump.json> <start> <end>")
        sys.exit(1)
    
    binary_file = sys.argv[1]
    dump_file = sys.argv[2]
    start_addr = int(sys.argv[3])
    end_addr = int(sys.argv[4])
    
    interpreter = UVMInterpreter()
    size = interpreter.load_program(binary_file)
    print(f"Загружена программа: {size} байт")
    
    interpreter.execute()
    print("Программа выполнена")
    
    dump = interpreter.dump_memory(start_addr, end_addr)
    
    with open(dump_file, 'w') as f:
        json.dump(dump, f, indent=2)
    
    print(f"Дамп памяти сохранен в {dump_file}")

if __name__ == '__main__':
    main()
