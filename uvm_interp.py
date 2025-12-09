#!/usr/bin/env python3
"""
Интерпретатор УВМ - Этап 3
Реализация модели памяти и базовых команд
"""

import json
import sys
import argparse
import struct
import math
from typing import List, Optional, Tuple

class UVMInterpreter:
    """Интерпретатор УВМ с раздельной памятью"""
    
    def __init__(self, mem_size: int = 65536):
        """
        Инициализация интерпретатора
        
        Args:
            mem_size: размер памяти данных (по умолчанию 64KB)
        """
        self.memory = [0] * mem_size  # Память данных
        self.acc = 0                  # Регистр-аккумулятор
        self.pc = 0                   # Счетчик команд
        self.program = bytearray()    # Память команд
        self.running = True           # Флаг выполнения
        
        # Статистика
        self.commands_executed = 0
        self.memory_accesses = 0
    
    def load_program(self, binary_file: str) -> int:
        """
        Загрузка программы из бинарного файла
        
        Args:
            binary_file: путь к бинарному файлу
            
        Returns:
            Размер загруженной программы в байтах
        """
        try:
            with open(binary_file, 'rb') as f:
                self.program = bytearray(f.read())
            
            size = len(self.program)
            print(f"Загружена программа: {size} байт ({size // 3} команд)")
            
            if size % 3 != 0:
                print(f"⚠ Предупреждение: размер программы {size} не кратен 3")
            
            return size
            
        except FileNotFoundError:
            print(f"❌ Ошибка: файл {binary_file} не найден")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Ошибка загрузки программы: {e}")
            sys.exit(1)
    
    def decode_command(self, offset: int) -> Optional[Tuple[int, int]]:
        """
        Декодирование команды по смещению
        
        Args:
            offset: смещение в памяти команд
            
        Returns:
            Кортеж (opcode, operand) или None если конец программы
        """
        if offset + 3 > len(self.program):
            return None
        
        # Чтение 3 байтов команды
        byte1 = self.program[offset]
        byte2 = self.program[offset + 1]
        byte3 = self.program[offset + 2]  # Пока не используется
        
        # Декодирование: [AAAA BBBB] [BBBB BBBB] [BBBB BBBB]
        opcode = byte1 >> 4               # Биты 0-3: код операции
        operand = ((byte1 & 0x0F) << 8) | byte2  # Биты 4-15/16: операнд
        
        return opcode, operand
    
    def execute_load_const(self, operand: int):
        """Выполнение команды LOAD_CONST (A=10)"""
        self.acc = operand
        self.commands_executed += 1
        if self.pc == 0:  # Первая команда для демонстрации
            print(f"  LOAD_CONST: ACC = {operand}")
    
    def execute_load_mem(self, operand: int):
        """Выполнение команды LOAD_MEM (A=0)"""
        addr = self.acc + operand
        if 0 <= addr < len(self.memory):
            self.acc = self.memory[addr]
            self.memory_accesses += 1
            if self.pc == 3:  # Для демонстрации
                print(f"  LOAD_MEM: ACC = MEM[{addr}] = {self.acc}")
        else:
            print(f"⚠ Ошибка: адрес {addr} вне диапазона памяти")
    
    def execute_store_mem(self, operand: int):
        """Выполнение команды STORE_MEM (A=14)"""
        if 0 <= operand < len(self.memory):
            self.memory[operand] = self.acc
            self.memory_accesses += 1
            if self.pc == 6:  # Для демонстрации
                print(f"  STORE_MEM: MEM[{operand}] = {self.acc}")
        else:
            print(f"⚠ Ошибка: адрес {operand} вне диапазона памяти")
    
    def execute_sqrt(self, operand: int):
        """Выполнение команды SQRT (A=2) - заглушка для Этапа 4"""
        src_addr = self.acc
        dst_addr = operand
        
        if 0 <= src_addr < len(self.memory) and 0 <= dst_addr < len(self.memory):
            value = self.memory[src_addr]
            result = int(math.sqrt(abs(value)))  # Будет реализовано в Этапе 4
            self.memory[dst_addr] = result
            self.memory_accesses += 2
            print(f"  SQRT: MEM[{dst_addr}] = sqrt(MEM[{src_addr}]) = {result}")
        else:
            print(f"⚠ Ошибка SQRT: неверные адреса {src_addr} -> {dst_addr}")
    
    def execute_command(self, opcode: int, operand: int):
        """Выполнение одной команды"""
        if opcode == 10:  # LOAD_CONST
            self.execute_load_const(operand)
        elif opcode == 0:  # LOAD_MEM
            self.execute_load_mem(operand)
        elif opcode == 14:  # STORE_MEM
            self.execute_store_mem(operand)
        elif opcode == 2:  # SQRT
            self.execute_sqrt(operand)
        else:
            print(f"⚠ Неизвестный код операции: {opcode}")
            self.running = False
    
    def run(self):
        """Основной цикл выполнения программы"""
        print("Начало выполнения программы...")
        print("-" * 40)
        
        while self.running and self.pc < len(self.program):
            # Декодирование команды
            decoded = self.decode_command(self.pc)
            if decoded is None:
                break
            
            opcode, operand = decoded
            
            # Выполнение команды
            self.execute_command(opcode, operand)
            
            # Переход к следующей команде
            self.pc += 3
            
            # Ограничение для демонстрации (убрать в финальной версии)
            if self.commands_executed > 100:
                print("⚠ Прервано: слишком много команд")
                break
        
        print("-" * 40)
        print(f"Выполнение завершено.")
        print(f"Статистика: {self.commands_executed} команд, "
              f"{self.memory_accesses} обращений к памяти")
    
    def dump_memory(self, start_addr: int, end_addr: int) -> dict:
        """
        Дамп памяти в указанном диапазоне
        
        Args:
            start_addr: начальный адрес
            end_addr: конечный адрес
            
        Returns:
            Словарь с содержимым памяти
        """
        dump = {}
        
        # Корректировка диапазона
        start = max(0, start_addr)
        end = min(end_addr, len(self.memory))
        
        for addr in range(start, end):
            value = self.memory[addr]
            if value != 0:  # Сохраняем только ненулевые значения
                dump[str(addr)] = value
        
        return dump
    
    def save_dump(self, dump: dict, output_file: str):
        """Сохранение дампа памяти в JSON файл"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dump, f, indent=2, ensure_ascii=False)
            
            print(f"Дамп памяти сохранен в: {output_file}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения дампа: {e}")
    
    def initialize_test_memory(self):
        """Инициализация тестовой памяти для демонстрации"""
        # Заполняем память тестовыми данными
        for i in range(100, 110):
            self.memory[i] = i * 10  # Значения 1000, 1010, 1020...
        
        print("Тестовая память инициализирована (адреса 100-109)")

def main():
    parser = argparse.ArgumentParser(
        description='Интерпретатор УВМ - Этап 3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  Базовый запуск: python uvm_interp.py program.bin dump.json 0 100
  С тестовой программой: python uvm_interp.py test.bin memory.json 0 200
  
Тестовые программы:
  1. Создайте программу: python uvm_asm.py array_copy.json copy.bin --binary
  2. Запустите: python uvm_interp.py copy.bin result.json 0 300
        """
    )
    
    parser.add_argument('program', help='Бинарный файл с программой')
    parser.add_argument('dump', help='Файл для сохранения дампа памяти (JSON)')
    parser.add_argument('start', type=int, help='Начальный адрес дампа')
    parser.add_argument('end', type=int, help='Конечный адрес дампа')
    parser.add_argument('--test', action='store_true', 
                       help='Инициализировать тестовую память')
    parser.add_argument('--verbose', action='store_true',
                       help='Подробный вывод выполнения')
    
    args = parser.parse_args()
    
    # Проверка аргументов
    if args.start >= args.end:
        print("❌ Ошибка: start должен быть меньше end")
        sys.exit(1)
    
    if args.end - args.start > 10000:
        print("⚠ Предупреждение: большой диапазон дампа (>10000 адресов)")
    
    # Создание и настройка интерпретатора
    interpreter = UVMInterpreter()
    
    # Инициализация тестовой памяти (если нужно)
    if args.test:
        interpreter.initialize_test_memory()
    
    # Загрузка программы
    interpreter.load_program(args.program)
    
    # Выполнение программы
    interpreter.run()
    
    # Создание и сохранение дампа памяти
    dump = interpreter.dump_memory(args.start, args.end)
    
    if dump:
        interpreter.save_dump(dump, args.dump)
        print(f"Дамп содержит {len(dump)} ненулевых значений")
    else:
        print("⚠ Дамп пуст (все значения нулевые)")
        # Все равно сохраняем пустой JSON
        with open(args.dump, 'w') as f:
            json.dump({}, f)

if __name__ == '__main__':
    main()
