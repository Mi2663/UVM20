#!/usr/bin/env python3
"""
Интерпретатор УВМ - Этапы 3 и 4
Реализация модели памяти и АЛУ (команда sqrt)
"""

import json
import sys
import argparse
import math
from typing import List, Optional, Tuple

class UVMInterpreter:
    """Интерпретатор УВМ с раздельной памятью и АЛУ"""
    
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
        self.sqrt_operations = 0
    
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
    
    # === КОМАНДЫ АЛУ ===
    
    def execute_load_const(self, operand: int):
        """Выполнение команды LOAD_CONST (A=10)"""
        self.acc = operand
        self.commands_executed += 1
    
    def execute_load_mem(self, operand: int):
        """Выполнение команды LOAD_MEM (A=0)"""
        addr = self.acc + operand
        if 0 <= addr < len(self.memory):
            self.acc = self.memory[addr]
            self.memory_accesses += 1
        else:
            print(f"⚠ Ошибка: адрес {addr} вне диапазона памяти")
            self.acc = 0
    
    def execute_store_mem(self, operand: int):
        """Выполнение команды STORE_MEM (A=14)"""
        if 0 <= operand < len(self.memory):
            self.memory[operand] = self.acc
            self.memory_accesses += 1
        else:
            print(f"⚠ Ошибка: адрес {operand} вне диапазона памяти")
    
    def execute_sqrt(self, operand: int):
        """
        Выполнение команды SQRT (A=2)
        
        Формат: MEM[B] = sqrt(MEM[ACC])
        ACC содержит адрес источника
        B - адрес назначения
        """
        src_addr = self.acc
        dst_addr = operand
        
        if 0 <= src_addr < len(self.memory) and 0 <= dst_addr < len(self.memory):
            value = self.memory[src_addr]
            
            # Вычисление квадратного корня
            if value < 0:
                # Для отрицательных чисел берем модуль
                result = int(math.sqrt(-value))
                print(f"  SQRT: √({value}) = √({-value})i → {result} (взят модуль)")
            else:
                result = int(math.sqrt(value))
                print(f"  SQRT: MEM[{dst_addr}] = √(MEM[{src_addr}]={value}) = {result}")
            
            # Сохранение результата
            self.memory[dst_addr] = result
            self.memory_accesses += 2
            self.sqrt_operations += 1
            self.commands_executed += 1
        else:
            print(f"⚠ Ошибка SQRT: неверные адреса src={src_addr}, dst={dst_addr}")
    
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
    
    def run(self, verbose: bool = False):
        """
        Основной цикл выполнения программы
        
        Args:
            verbose: подробный вывод выполнения команд
        """
        if verbose:
            print("Начало выполнения программы...")
            print("-" * 50)
        
        while self.running and self.pc < len(self.program):
            # Декодирование команды
            decoded = self.decode_command(self.pc)
            if decoded is None:
                break
            
            opcode, operand = decoded
            
            # Подробный вывод
            if verbose:
                cmd_names = {10: "LOAD_CONST", 0: "LOAD_MEM", 
                           14: "STORE_MEM", 2: "SQRT"}
                cmd_name = cmd_names.get(opcode, f"CMD[{opcode}]")
                print(f"[{self.pc:04X}] {cmd_name} {operand}")
            
            # Выполнение команды
            self.execute_command(opcode, operand)
            
            # Переход к следующей команде
            self.pc += 3
            
            # Безопасное ограничение
            if self.commands_executed > 10000:
                print("⚠ Прервано: слишком много команд (возможно бесконечный цикл)")
                break
        
        if verbose:
            print("-" * 50)
        
        print(f"Выполнение завершено.")
        print(f"Статистика: {self.commands_executed} команд, "
              f"{self.memory_accesses} обращений к памяти, "
              f"{self.sqrt_operations} операций sqrt")
    
    # === РАБОТА С ПАМЯТЬЮ ===
    
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
    
    def initialize_memory_with_values(self, values: dict):
        """
        Инициализация памяти заданными значениями
        
        Args:
            values: словарь {адрес: значение}
        """
        for addr, value in values.items():
            if 0 <= addr < len(self.memory):
                self.memory[addr] = value
        
        print(f"Память инициализирована {len(values)} значениями")
    
    # === УТИЛИТЫ ДЛЯ ТЕСТИРОВАНИЯ SQRT ===
    
    def test_sqrt_operation(self, test_values: List[Tuple[int, int, int]]):
        """
        Тестирование операции sqrt на заданных данных
        
        Args:
            test_values: список (src_addr, value, expected_result)
        """
        print("\n" + "=" * 50)
        print("ТЕСТИРОВАНИЕ КОМАНДЫ SQRT")
        print("=" * 50)
        
        for src_addr, value, expected in test_values:
            # Записываем тестовое значение в память
            self.memory[src_addr] = value
            
            # Устанавливаем аккумулятор на адрес источника
            self.acc = src_addr
            
            # Выполняем sqrt в ячейку 1000 (для теста)
            self.execute_sqrt(1000)
            
            # Проверяем результат
            result = self.memory[1000]
            status = "✓" if result == expected else "✗"
            print(f"{status} √({value}) = {result} (ожидалось {expected})")
            
            # Очищаем тестовую ячейку
            self.memory[1000] = 0
        
        print("=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description='Интерпретатор УВМ - Этапы 3 и 4',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  Базовый запуск:     python uvm_interp.py program.bin dump.json 0 100
  Подробный вывод:    python uvm_interp.py program.bin dump.json 0 100 --verbose
  Тест sqrt:          python uvm_interp.py --test-sqrt
  
Тестовые программы для sqrt:
  1. python uvm_asm.py sqrt_test.json sqrt.bin --binary
  2. python uvm_interp.py sqrt.bin result.json 0 200 --verbose
        """
    )
    
    parser.add_argument('program', nargs='?', help='Бинарный файл с программой')
    parser.add_argument('dump', nargs='?', help='Файл для сохранения дампа памяти (JSON)')
    parser.add_argument('start', nargs='?', type=int, help='Начальный адрес дампа')
    parser.add_argument('end', nargs='?', type=int, help='Конечный адрес дампа')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод выполнения')
    parser.add_argument('--test-sqrt', action='store_true',
                       help='Запустить тестирование команды sqrt')
    parser.add_argument('--init-memory', type=str,
                       help='Инициализировать память из JSON файла')
    
    args = parser.parse_args()
    
    # Создание интерпретатора
    interpreter = UVMInterpreter()
    
    # Тестирование sqrt (если указано)
    if args.test_sqrt:
        # Тестовые значения: (адрес, значение, ожидаемый результат)
        test_cases = [
            (100, 0, 0),      # √0 = 0
            (101, 1, 1),      # √1 = 1
            (102, 4, 2),      # √4 = 2
            (103, 9, 3),      # √9 = 3
            (104, 16, 4),     # √16 = 4
            (105, 25, 5),     # √25 = 5
            (106, 100, 10),   # √100 = 10
            (107, 144, 12),   # √144 = 12
            (108, 225, 15),   # √225 = 15
            (109, 10000, 100),# √10000 = 100
            (110, -25, 5),    # √(-25) = 5i → 5 (берем модуль)
        ]
        
        interpreter.test_sqrt_operation(test_cases)
        return
    
    # Обычный режим выполнения программы
    if not all([args.program, args.dump, args.start is not None, args.end is not None]):
        parser.print_help()
        print("\n❌ Ошибка: для обычного режима нужны все аргументы: program dump start end")
        sys.exit(1)
    
    # Проверка аргументов
    if args.start >= args.end:
        print("❌ Ошибка: start должен быть меньше end")
        sys.exit(1)
    
    # Инициализация памяти (если указано)
    if args.init_memory:
        try:
            with open(args.init_memory, 'r') as f:
                init_data = json.load(f)
            
            # Преобразуем строковые ключи в int
            init_data_int = {int(k): v for k, v in init_data.items()}
            interpreter.initialize_memory_with_values(init_data_int)
        except Exception as e:
            print(f"❌ Ошибка инициализации памяти: {e}")
    
    # Загрузка программы
    interpreter.load_program(args.program)
    
    # Выполнение программы
    interpreter.run(verbose=args.verbose)
    
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
