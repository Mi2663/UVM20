#!/usr/bin/env python3
"""
Демонстрация работы ассемблера и интерпретатора УВМ
"""

import subprocess
import os

def run_command(cmd):
    """Запустить команду и вывести результат"""
    print(f"▶ Выполняю: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Ошибка: {result.stderr}")
    print()

def main():
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ УВМ - ЭТАПЫ 1 и 2")
    print("=" * 60)
    
    # 1. Тестирование ассемблера (Этап 1)
    print("\n1. ТЕСТИРОВАНИЕ АССЕМБЛЕРА (ЭТАП 1):")
    run_command("python uvm_asm.py test_specification.json --test")
    
    # 2. Генерация промежуточного представления
    print("\n2. СОХРАНЕНИЕ ПРОМЕЖУТОЧНОГО ПРЕДСТАВЛЕНИЯ:")
    run_command("python uvm_asm.py test_specification.json intermediate.json")
    
    # 3. Генерация бинарного файла с тестированием (Этап 2)
    print("\n3. ГЕНЕРАЦИЯ БИНАРНОГО ФАЙЛА С ТЕСТИРОВАНИЕМ (ЭТАП 2):")
    run_command("python uvm_asm.py test_specification.json program.bin --binary --test")
    
    # 4. Проверка размера бинарного файла
    if os.path.exists("program.bin"):
        size = os.path.getsize("program.bin")
        print(f"\n4. РАЗМЕР БИНАРНОГО ФАЙЛА: {size} байт")
        print(f"   Команд в файле: {size // 3}")
    
    # 5. Запуск интерпретатора
    print("\n5. ЗАПУСК ИНТЕРПРЕТАТОРА:")
    print("   (Создайте тестовую программу для интерпретатора)")
    
    # 6. Запуск всех тестов
    print("\n6. ЗАПУСК ВСЕХ ТЕСТОВ:")
    run_command("python test_assembler.py")
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)

if __name__ == "__main__":
    main()
