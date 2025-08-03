#!/usr/bin/env python3
"""
API сервер для Telegram Mini App (Продакшен версия)
"""

import json
import sqlite3
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Database
    from pet_manager import PetManager
    from config import PET_TYPES, ACTIONS
except ImportError:
    print("⚠️ Модули не найдены, используем демо-режим")
    # Демо-версия без зависимостей
    PET_TYPES = {"cat": {"emoji": "🐱", "name": "Котик"}}
    ACTIONS = {"feed": {"name": "Покормить"}}

class MiniAppAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Инициализируем базу данных при создании обработчика
        try:
            self.db = Database('pets.db')
            self.pm = PetManager(self.db)
            print("✅ База данных инициализирована")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации БД: {e}")
            self.db = None
            self.pm = None
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def send_cors_headers(self):
        """Отправка CORS заголовков"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-Type', 'application/json')
    
    def do_GET(self):
        """Обработка GET запросов"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        try:
            if path == '/api/health':
                self.handle_health()
            elif path == '/api/user':
                self.handle_get_user(query_params)
            elif path == '/api/couple':
                self.handle_get_couple(query_params)
            elif path == '/api/pet':
                self.handle_get_pet(query_params)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Обработка POST запросов"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            if path == '/api/couple/create':
                self.handle_create_couple(data)
            elif path == '/api/pet/create':
                self.handle_create_pet(data)
            elif path == '/api/pet/action':
                self.handle_pet_action(data)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_health(self):
        """Проверка здоровья сервера"""
        response = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_get_user(self, params):
        """Получение информации о пользователе"""
        user_id = int(params.get('user_id', [0])[0])
        
        if user_id == 0:
            self.send_error(400, "user_id required")
            return
        
        if not self.db:
            # Демо-режим
            response = {
                'user_id': user_id,
                'has_couple': False,
                'couple_id': None,
                'demo_mode': True
            }
        else:
            # Реальный режим
            couple = self.db.get_user_couple(user_id)
            response = {
                'user_id': user_id,
                'has_couple': couple is not None,
                'couple_id': couple['id'] if couple else None,
                'demo_mode': False
            }
        
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_create_couple(self, data):
        """Создание пары"""
        user1_id = data.get('user1_id')
        user2_id = data.get('user2_id')
        user1_name = data.get('user1_name', 'Пользователь 1')
        user2_name = data.get('user2_name', 'Пользователь 2')
        
        if not user1_id or not user2_id:
            self.send_error(400, "user1_id and user2_id required")
            return
        
        try:
            if not self.db:
                # Демо-режим
                couple_id = int(f"{user1_id}{user2_id}")
                response = {
                    'success': True,
                    'couple_id': couple_id,
                    'message': 'Пара создана успешно! (Демо-режим)',
                    'demo_mode': True
                }
            else:
                # Реальный режим
                couple_id = self.db.create_couple(user1_id, user2_id, user1_name, user2_name)
                response = {
                    'success': True,
                    'couple_id': couple_id,
                    'message': 'Пара создана успешно!',
                    'demo_mode': False
                }
            
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {
                'success': False,
                'error': str(e),
                'demo_mode': self.db is None
            }
            
            self.send_response(400)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

def run_api_server(port=None):
    """Запуск API сервера"""
    if port is None:
        port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Запуск API сервера на порту {port}")
    print(f"📡 Переменные окружения: PORT={os.environ.get('PORT', 'не задан')}")
    
    try:
        server_address = ('0.0.0.0', port)
        httpd = HTTPServer(server_address, MiniAppAPIHandler)
        print(f"✅ API сервер запущен на {server_address}")
        print(f"🔗 Health check: http://0.0.0.0:{port}/api/health")
        httpd.serve_forever()
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        raise

if __name__ == '__main__':
    run_api_server()
