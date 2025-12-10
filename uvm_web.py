#!/usr/bin/env python3
"""
Web интерфейс для УВМ - Вариант 20
"""

from flask import Flask, render_template, request, jsonify
import json
import math

app = Flask(__name__)

class UVMWeb:
    def __init__(self):
        self.memory_size = 65536
        self.memory = [0] * self.memory_size
        self.acc = 0  # Аккумулятор
        
        # Таблица кодов операций
        self.opcodes = {
            'LOAD_CONST': 10,
            'LOAD_MEM': 0,
            'STORE_MEM': 14,
            'SQRT': 2
        }
        
        # Описания команд
        self.descriptions = {
            'LOAD_CONST': "Размер команды: 3 байт. Операнд: поле В. Результат: регистр-аккумулятор.",
            'LOAD_MEM': "Размер команды: 3 байт. Операнд: значение в памяти по адресу, которым является сумма адреса (регистр-аккумулятор) и смещения (поле В). Результат: регистр-аккумулятор.",
            'STORE_MEM': "Размер команды: 3 байт. Операнд: регистр-аккумулятор. Результат: значение в памяти по адресу, которым является поле В.",
            'SQRT': "Размер команды: 3 байт. Операнд: значение в памяти по адресу, которым является регистр-аккумулятор. Результат: значение в памяти по адресу, которым является поле В."
        }
        
        # Инициализируем тестовые данные
        self.initialize_memory()
    
    def initialize_memory(self):
        """Инициализирует память тестовыми данными"""
        self.memory[500] = 25   # √25 = 5
        self.memory[501] = 100  # √100 = 10
        self.memory[502] = 225  # √225 = 15
        self.memory[520] = 100  # Для LOAD_CONST теста
        self.memory[133] = 42   # Для LOAD_MEM теста
    
    def reset(self):
        """Сброс состояния"""
        self.memory = [0] * self.memory_size
        self.acc = 0
        self.initialize_memory()
    
    def assemble_program(self, program_json):
        """Ассемблирует программу"""
        try:
            program = json.loads(program_json)
            commands = program.get('program', [])
            
            result = {
                'success': True,
                'commands': [],
                'output': [],
                'hex_bytes': []
            }
            
            for i, cmd in enumerate(commands):
                opcode = cmd.get('opcode', '').upper()
                operand = cmd.get('operand', 0)
                
                if opcode in self.opcodes:
                    # Формируем байты
                    byte1 = (self.opcodes[opcode] << 4) | ((operand >> 8) & 0x0F)
                    byte2 = operand & 0xFF
                    byte3 = 0
                    
                    hex_str = f"0x{byte1:02X}, 0x{byte2:02X}, 0x{byte3:02X}"
                    
                    command_info = {
                        'index': i,
                        'opcode': opcode,
                        'operand': operand,
                        'description': self.descriptions[opcode],
                        'test': f"Тест (A={self.opcodes[opcode]}, B={operand}):",
                        'hex_bytes': hex_str,
                        'comment': cmd.get('comment', '')
                    }
                    
                    result['commands'].append(command_info)
                    result['output'].append(f"Команда {i}: {opcode} {operand}")
                    result['hex_bytes'].append(hex_str)
                else:
                    result['output'].append(f"ОШИБКА: Неизвестная команда '{opcode}'")
            
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_program(self, program_json):
        """Выполняет программу"""
        try:
            program = json.loads(program_json)
            commands = program.get('program', [])
            
            # Сбрасываем состояние
            self.reset()
            
            result = {
                'success': True,
                'steps': [],
                'memory_dump': {},
                'final_acc': self.acc,
                'output': []
            }
            
            for i, cmd in enumerate(commands):
                opcode = cmd.get('opcode', '').upper()
                operand = cmd.get('operand', 0)
                
                step_info = {
                    'index': i,
                    'opcode': opcode,
                    'operand': operand,
                    'before_acc': self.acc
                }
                
                if opcode == 'LOAD_CONST':
                    self.acc = operand
                    step_info['after_acc'] = self.acc
                    step_info['description'] = f"LOAD_CONST {operand} → ACC={self.acc}"
                    
                elif opcode == 'LOAD_MEM':
                    addr = self.acc + operand
                    if 0 <= addr < self.memory_size:
                        self.acc = self.memory[addr]
                        step_info['after_acc'] = self.acc
                        step_info['address'] = addr
                        step_info['value'] = self.memory[addr]
                        step_info['description'] = f"LOAD_MEM {operand} → MEM[{addr}]={self.acc}"
                    else:
                        step_info['error'] = f"Адрес {addr} вне памяти"
                        
                elif opcode == 'STORE_MEM':
                    if 0 <= operand < self.memory_size:
                        self.memory[operand] = self.acc
                        step_info['address'] = operand
                        step_info['value'] = self.acc
                        step_info['after_acc'] = self.acc
                        step_info['description'] = f"STORE_MEM {operand} ← ACC={self.acc}"
                    else:
                        step_info['error'] = f"Адрес {operand} вне памяти"
                        
                elif opcode == 'SQRT':
                    src_addr = self.acc
                    dst_addr = operand
                    
                    if 0 <= src_addr < self.memory_size and 0 <= dst_addr < self.memory_size:
                        value = self.memory[src_addr]
                        result_val = int(math.sqrt(abs(value)))
                        self.memory[dst_addr] = result_val
                        step_info['src_addr'] = src_addr
                        step_info['dst_addr'] = dst_addr
                        step_info['src_value'] = value
                        step_info['result'] = result_val
                        step_info['after_acc'] = self.acc
                        step_info['description'] = f"SQRT MEM[{src_addr}]={value} → MEM[{dst_addr}]={result_val}"
                    else:
                        step_info['error'] = "Неверные адреса"
                        
                else:
                    step_info['error'] = f"Неизвестная команда '{opcode}'"
                
                result['steps'].append(step_info)
                result['output'].append(step_info.get('description', f"Команда {i}: {opcode} {operand}"))
            
            # Формируем дамп памяти
            for addr in range(1000):
                if self.memory[addr] != 0:
                    result['memory_dump'][str(addr)] = self.memory[addr]
            
            result['final_acc'] = self.acc
            
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Создаем экземпляр УВМ
uvm = UVMWeb()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/assemble', methods=['POST'])
def api_assemble():
    """API для ассемблирования"""
    data = request.get_json()
    program = data.get('program', '')
    
    result = uvm.assemble_program(program)
    return jsonify(result)

@app.route('/api/execute', methods=['POST'])
def api_execute():
    """API для выполнения программы"""
    data = request.get_json()
    program = data.get('program', '')
    
    result = uvm.execute_program(program)
    return jsonify(result)

@app.route('/api/reset', methods=['POST'])
def api_reset():
    """API для сброса состояния"""
    uvm.reset()
    return jsonify({'success': True, 'message': 'Состояние сброшено'})

@app.route('/api/example', methods=['GET'])
def api_example():
    """API для получения примера программы"""
    example = {
        "program": [
            {
                "opcode": "LOAD_CONST",
                "operand": 520,
                "comment": "Тест из спецификации: A=10, B=520"
            },
            {
                "opcode": "LOAD_MEM",
                "operand": 133,
                "comment": "Тест из спецификации: A=0, B=133"
            },
            {
                "opcode": "STORE_MEM",
                "operand": 167,
                "comment": "Тест из спецификации: A=14, B=167"
            },
            {
                "opcode": "SQRT",
                "operand": 954,
                "comment": "Тест из спецификации: A=2, B=954"
            }
        ]
    }
    return jsonify(example)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
