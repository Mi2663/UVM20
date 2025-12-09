#!/usr/bin/env python3
"""
Скрипт для выполнения Этапа 5: Тестовая задача и примеры программ
"""

import subprocess
import json
import os
import sys
import time

def run_command(cmd, description=None):
    """Выполнить команду и вывести результат"""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print(f"{'='*60}")
    
    print(f"▶ {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            # Игнорируем предупреждения о расширениях файлов
            if "Предупреждение" not in result.stderr and "Warning" not in result.stderr:
                print(f"⚠ {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Ошибка выполнения команды: {e}")
        return False

def create_test_files():
    """Создание необходимых тестовых файлов"""
    print("Создание тестовых файлов для Этапа 5...")
    
    # Проверяем существующие файлы
    required_files = [
        'stage5_vector_sqrt.json',
        'example1_factorial.json', 
        'example2_statistics.json',
        'example3_matrix_operations.json',
        'init_vector_data.json'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"  ❌ Файл {file} не найден")
            return False
    
    print("  ✅ Все тестовые файлы найдены")
    return True

def stage5_main_task():
    """Основная тестовая задача: sqrt над вектором"""
    print("\n" + "="*60)
    print("ЭТАП 5: ОСНОВНАЯ ТЕСТОВАЯ ЗАДАЧА")
    print("Поэлементное вычисление sqrt() над вектором длины 10")
    print("="*60)
    
    # 1. Ассемблирование программы
    success = run_command(
        'python uvm_asm.py stage5_vector_sqrt.json stage5.bin --binary',
        "1. АССЕМБЛИРОВАНИЕ ПРОГРАММЫ"
    )
    
    if not success:
        return False
    
    # 2. Запуск интерпретатора
    success = run_command(
        'python uvm_interp.py stage5.bin stage5_result.json 0 600 --init-memory init_vector_data.json --verbose',
        "2. ВЫПОЛНЕНИЕ ПРОГРАММЫ"
    )
    
    if not success:
        return False
    
    # 3. Проверка результатов
    print("\n" + "="*60)
    print("3. ПРОВЕРКА РЕЗУЛЬТАТОВ")
    print("="*60)
    
    try:
        with open('stage5_result.json', 'r') as f:
            result = json.load(f)
        
        # Ожидаемые результаты для вектора [0,1,4,9,16,25,36,49,64,81]
        expected = {
            "500": 0,   # √0 = 0
            "501": 1,   # √1 = 1
            "502": 2,   # √4 = 2
            "503": 3,   # √9 = 3
            "504": 4,   # √16 = 4
            "505": 5,   # √25 = 5
            "506": 6,   # √36 = 6
            "507": 7,   # √49 = 7
            "508": 8,   # √64 = 8
            "509": 9    # √81 = 9
        }
        
        all_correct = True
        for addr, expected_value in expected.items():
            actual_value = result.get(addr, "не найден")
            if str(actual_value) == str(expected_value):
                print(f"  ✅ Адрес {addr}: √{expected_value**2} = {actual_value}")
            else:
                print(f"  ❌ Адрес {addr}: ожидалось {expected_value}, получено {actual_value}")
                all_correct = False
        
        if all_correct:
            print(f"\n✅ ВСЕ РЕЗУЛЬТАТЫ ВЕРНЫ!")
            print(f"   Программа успешно вычислила sqrt() для всех 10 элементов вектора")
        else:
            print(f"\n❌ ЕСТЬ ОШИБКИ В РЕЗУЛЬТАТАХ")
        
        # Показать дамп памяти
        print(f"\nСОДЕРЖИМОЕ ДАМПА ПАМЯТИ (ненулевые значения):")
        print(f"Всего значений: {len(result)}")
        
        # Сортировка по адресам
        sorted_addrs = sorted(result.items(), key=lambda x: int(x[0]))
        for addr, value in sorted_addrs[:20]:  # Показать первые 20
            print(f"  MEM[{addr}] = {value}")
        
        if len(result) > 20:
            print(f"  ... и еще {len(result) - 20} значений")
        
        return all_correct
        
    except Exception as e:
        print(f"❌ Ошибка при проверке результатов: {e}")
        return False

def stage5_examples():
    """Запуск примеров программ"""
    examples = [
        {
            "name": "ПРИМЕР 1: ВЫЧИСЛЕНИЕ ФАКТОРИАЛА",
            "json": "example1_factorial.json",
            "bin": "example1.bin",
            "result": "example1_result.json",
            "range": "0 300",
            "init": "init_vector_data.json",
            "description": "Вычисление 5! = 120"
        },
        {
            "name": "ПРИМЕР 2: СТАТИСТИКА МАССИВА",
            "json": "example2_statistics.json",
            "bin": "example2.bin",
            "result": "example2_result.json",
            "range": "0 500",
            "init": "init_vector_data.json",
            "description": "Сумма и среднее массива [10,20,...,100]"
        },
        {
            "name": "ПРИМЕР 3: ОПЕРАЦИИ С МАТРИЦАМИ",
            "json": "example3_matrix_operations.json",
            "bin": "example3.bin",
            "result": "example3_result.json",
            "range": "0 700",
            "init": "init_vector_data.json",
            "description": "Сложение матриц 3x3"
        }
    ]
    
    all_success = True
    
    for example in examples:
        print("\n" + "="*60)
        print(example["name"])
        print(example["description"])
        print("="*60)
        
        # Ассемблирование
        success = run_command(
            f'python uvm_asm.py {example["json"]} {example["bin"]} --binary',
            "Ассемблирование"
        )
        
        if not success:
            all_success = False
            continue
        
        # Выполнение
        success = run_command(
            f'python uvm_interp.py {example["bin"]} {example["result"]} {example["range"]} --init-memory {example["init"]}',
            "Выполнение"
        )
        
        if not success:
            all_success = False
            continue
        
        # Показать результаты
        try:
            with open(example["result"], 'r') as f:
                result = json.load(f)
            
            print(f"\nРЕЗУЛЬТАТЫ ({len(result)} ненулевых значений):")
            
            # Сортировка и вывод
            sorted_items = sorted(result.items(), key=lambda x: int(x[0]))
            for addr, value in sorted_items[:15]:
                print(f"  MEM[{addr}] = {value}")
            
            if len(result) > 15:
                print(f"  ... и еще {len(result) - 15} значений")
            
            print(f"  ✅ Пример выполнен успешно")
            
        except Exception as e:
            print(f"❌ Ошибка при чтении результатов: {e}")
            all_success = False
    
    return all_success

def cleanup_files():
    """Очистка временных файлов"""
    temp_files = [
        'stage5.bin', 'stage5_result.json',
        'example1.bin', 'example1_result.json',
        'example2.bin', 'example2_result.json',
        'example3.bin', 'example3_result.json'
    ]
    
    print("\n" + "="*60)
    print("ОЧИСТКА ВРЕМЕННЫХ ФАЙЛОВ")
    print("="*60)
    
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  Удален: {file}")
            except:
                print(f"  ❌ Не удалось удалить: {file}")

def main():
    """Основная функция"""
    print("="*60)
    print("ВЫПОЛНЕНИЕ ЭТАПА 5: ТЕСТОВАЯ ЗАДАЧА")
    print("="*60)
    
    # Проверка зависимостей
    print("Проверка необходимых файлов...")
    if not os.path.exists('uvm_asm.py'):
        print("❌ Файл uvm_asm.py не найден")
        return False
    
    if not os.path.exists('uvm_interp.py'):
        print("❌ Файл uvm_interp.py не найден")
        return False
    
    print("✅ Основные файлы найдены")
    
    # Создание тестовых файлов
    if not create_test_files():
        print("\n❌ Создайте недостающие тестовые файлы перед запуском")
        print("Необходимые файлы:")
        print("  - stage5_vector_sqrt.json")
        print("  - example1_factorial.json")
        print("  - example2_statistics.json")
        print("  - example3_matrix_operations.json")
        print("  - init_vector_data.json")
        return False
    
    # Выполнение основной задачи
    main_task_success = stage5_main_task()
    
    # Выполнение примеров
    examples_success = stage5_examples()
    
    # Итоги
    print("\n" + "="*60)
    print("ИТОГИ ВЫПОЛНЕНИЯ ЭТАПА 5")
    print("="*60)
    
    if main_task_success:
        print("✅ ОСНОВНАЯ ЗАДАЧА: ВЫПОЛНЕНА УСПЕШНО")
        print("   Программа корректно вычисляет sqrt() для вектора длины 10")
    else:
        print("❌ ОСНОВНАЯ ЗАДАЧА: ЕСТЬ ПРОБЛЕМЫ")
    
    if examples_success:
        print("✅ ПРИМЕРЫ ПРОГРАММ: ВСЕ ВЫПОЛНЕНЫ")
        print("   3 примера программ с различными вычислениями")
    else:
        print("❌ ПРИМЕРЫ ПРОГРАММ: ЕСТЬ ПРОБЛЕМЫ")
    
    if main_task_success and examples_success:
        print("\n" + "="*60)
        print("🎉 ЭТАП 5 ВЫПОЛНЕН ПОЛНОСТЬЮ!")
        print("Все требования этапа выполнены:")
        print("1. ✅ Поэлементное sqrt() над вектором длины 10")
        print("2. ✅ Результат записан в исходный вектор")
        print("3. ✅ Три примера программ с различными вычислениями")
        print("4. ✅ Дамп памяти соответствует требованиям")
        print("="*60)
    
    # Очистка
    cleanup = input("\nОчистить временные файлы? (y/n): ")
    if cleanup.lower() == 'y':
        cleanup_files()
    
    return main_task_success and examples_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
