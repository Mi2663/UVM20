#!/usr/bin/env python3
"""
Скрипт для выполнения Этапа 5 - упрощенная версия
"""

import json
import os
import subprocess
import sys

def run_simple_test():
    """Простой тест Этапа 5"""
    print("="*60)
    print("ЭТАП 5: ПРОСТАЯ ПРОВЕРКА")
    print("="*60)
    
    # 1. Создаем тестовую программу
    print("\n1. СОЗДАНИЕ ТЕСТОВОЙ ПРОГРАММЫ...")
    
    test_program = {
        "version": "1.0",
        "description": "Тест sqrt() для 3 элементов",
        "program": [
            {"opcode": "LOAD_CONST", "operand": 500},
            {"opcode": "SQRT", "operand": 500},
            {"opcode": "LOAD_CONST", "operand": 501},
            {"opcode": "SQRT", "operand": 501},
            {"opcode": "LOAD_CONST", "operand": 502},
            {"opcode": "SQRT", "operand": 502}
        ]
    }
    
    with open('test_simple.json', 'w', encoding='utf-8') as f:
        json.dump(test_program, f, indent=2, ensure_ascii=False)
    
    print("   ✅ Создан test_simple.json")
    
    # 2. Создаем данные для инициализации
    print("\n2. СОЗДАНИЕ ДАННЫХ ДЛЯ ПАМЯТИ...")
    
    init_data = {
        "500": 25,   # √25 = 5
        "501": 100,  # √100 = 10
        "502": 225   # √225 = 15
    }
    
    with open('test_init.json', 'w', encoding='utf-8') as f:
        json.dump(init_data, f, indent=2, ensure_ascii=False)
    
    print("   ✅ Создан test_init.json")
    
    # 3. Ассемблирование
    print("\n3. АССЕМБЛИРОВАНИЕ...")
    
    try:
        result = subprocess.run(
            ['python', 'uvm_asm.py', 'test_simple.json', 'test.bin', '--binary'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("   ✅ Программа ассемблирована: test.bin")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        else:
            print(f"   ❌ Ошибка ассемблирования: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    # 4. Выполнение
    print("\n4. ВЫПОЛНЕНИЕ ПРОГРАММЫ...")
    
    try:
        result = subprocess.run(
            ['python', 'uvm_interp.py', 'test.bin', 'test_result.json', 
             '0', '600', '--init-memory', 'test_init.json'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("   ✅ Программа выполнена")
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
        else:
            print(f"   ❌ Ошибка выполнения: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    # 5. Проверка результатов
    print("\n5. ПРОВЕРКА РЕЗУЛЬТАТОВ...")
    
    try:
        with open('test_result.json', 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        
        expected = {
            "500": 5,   # √25
            "501": 10,  # √100
            "502": 15   # √225
        }
        
        all_correct = True
        for addr, expected_value in expected.items():
            actual_value = result_data.get(addr)
            if actual_value == expected_value:
                print(f"   ✅ Адрес {addr}: {actual_value} (ожидалось {expected_value})")
            else:
                print(f"   ❌ Адрес {addr}: {actual_value} (ожидалось {expected_value})")
                all_correct = False
        
        if all_correct:
            print("\n   🎉 ВСЕ РЕЗУЛЬТАТЫ ВЕРНЫ!")
            print("   Этап 5 выполнен успешно!")
        else:
            print("\n   ❌ ЕСТЬ ОШИБКИ В РЕЗУЛЬТАТАХ")
            
        # Показать весь дамп
        print(f"\n   ДАМП ПАМЯТИ (всего {len(result_data)} значений):")
        for addr, value in sorted(result_data.items(), key=lambda x: int(x[0])):
            print(f"      MEM[{addr}] = {value}")
        
        return all_correct
        
    except Exception as e:
        print(f"   ❌ Ошибка чтения результатов: {e}")
        return False

def create_example_programs():
    """Создание примеров программ"""
    print("\n" + "="*60)
    print("СОЗДАНИЕ ПРИМЕРОВ ПРОГРАММ:")
    print("="*60)
    
    examples = [
        {
            "name": "example1_factorial.json",
            "data": {
                "version": "1.0",
                "description": "Пример 1: Упрощенный факториал",
                "program": [
                    {"opcode": "LOAD_CONST", "operand": 5},
                    {"opcode": "STORE_MEM", "operand": 200},
                    {"opcode": "LOAD_CONST", "operand": 1},
                    {"opcode": "STORE_MEM", "operand": 201}
                ]
            }
        },
        {
            "name": "example2_array_sum.json",
            "data": {
                "version": "1.0",
                "description": "Пример 2: Сумма массива",
                "program": [
                    {"opcode": "LOAD_CONST", "operand": 100},
                    {"opcode": "LOAD_MEM", "operand": 0},
                    {"opcode": "STORE_MEM", "operand": 300},
                    {"opcode": "LOAD_CONST", "operand": 101},
                    {"opcode": "LOAD_MEM", "operand": 0},
                    {"opcode": "LOAD_MEM", "operand": 300},
                    {"opcode": "STORE_MEM", "operand": 300}
                ]
            }
        },
        {
            "name": "example3_sqrt_array.json",
            "data": {
                "version": "1.0",
                "description": "Пример 3: sqrt для массива",
                "program": [
                    {"opcode": "LOAD_CONST", "operand": 400},
                    {"opcode": "SQRT", "operand": 400},
                    {"opcode": "LOAD_CONST", "operand": 401},
                    {"opcode": "SQRT", "operand": 401},
                    {"opcode": "LOAD_CONST", "operand": 402},
                    {"opcode": "SQRT", "operand": 402}
                ]
            }
        }
    ]
    
    created = 0
    for example in examples:
        try:
            with open(example["name"], 'w', encoding='utf-8') as f:
                json.dump(example["data"], f, indent=2, ensure_ascii=False)
            print(f"   ✅ Создан {example['name']}")
            created += 1
        except Exception as e:
            print(f"   ❌ Ошибка создания {example['name']}: {e}")
    
    return created

def cleanup():
    """Очистка временных файлов"""
    files_to_remove = [
        'test_simple.json', 'test_init.json', 'test.bin', 'test_result.json',
        'example1_factorial.json', 'example2_array_sum.json', 'example3_sqrt_array.json'
    ]
    
    print("\n" + "="*60)
    print("ОЧИСТКА:")
    print("="*60)
    
    removed = 0
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"   Удален: {file}")
                removed += 1
            except:
                print(f"   ❌ Не удалось удалить: {file}")
    
    print(f"\n   Удалено файлов: {removed}")

def main():
    """Основная функция"""
    print("="*60)
    print("ЭТАП 5: ТЕСТОВАЯ ЗАДАЧА (упрощенная проверка)")
    print("="*60)
    
    # Проверка необходимых файлов
    required = ['uvm_asm.py', 'uvm_interp.py']
    for file in required:
        if not os.path.exists(file):
            print(f"❌ Файл {file} не найден!")
            return False
    
    print("✅ Все необходимые файлы найдены")
    
    # Запуск теста
    test_passed = run_simple_test()
    
    # Создание примеров
    if test_passed:
        examples_created = create_example_programs()
        print(f"\n✅ Создано примеров программ: {examples_created}")
    
    # Очистка
    cleanup_choice = input("\nУдалить временные файлы? (y/n): ")
    if cleanup_choice.lower() == 'y':
        cleanup()
    
    if test_passed:
        print("\n" + "="*60)
        print("🎉 ЭТАП 5 ВЫПОЛНЕН!")
        print("="*60)
        print("Требования этапа выполнены:")
        print("1. ✅ sqrt() работает для элементов вектора")
        print("2. ✅ Программа ассемблируется и выполняется")
        print("3. ✅ Дамп памяти в JSON формате")
        print("4. ✅ Созданы примеры программ")
        print("="*60)
    
    return test_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
