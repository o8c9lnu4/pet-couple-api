#!/usr/bin/env python3
"""
API сервер для Telegram Mini App
Обрабатывает запросы от веб-приложения и работает с базой данных бота
"""

import json
import sqlite3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
import os

# Добавляем путь к родительской папке для импорта модулей бота
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from pet_manager import PetManager
from config import PET_TYPES, ACTIONS

class MiniAppAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = Database('pets.db')
        self.pm = PetManager(self.db)
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
            if path == '/api/user':
                self.handle_get_user(query_params)
            elif path == '/api/couple':
                self.handle_get_couple(query_params)
            elif path == '/api/pet':
                self.handle_get_pet(query_params)
            elif path == '/api/stats':
                self.handle_get_stats(query_params)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Обработка POST запросов"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
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
    
    def handle_get_user(self, params):
        """Получение информации о пользователе"""
        user_id = int(params.get('user_id', [0])[0])
        
        if user_id == 0:
            self.send_error(400, "user_id required")
            return
        
        # Проверяем, есть ли пользователь в базе
        couple = self.db.get_user_couple(user_id)
        
        response = {
            'user_id': user_id,
            'has_couple': couple is not None,
            'couple_id': couple['id'] if couple else None
        }
        
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_get_couple(self, params):
        """Получение информации о паре"""
        user_id = int(params.get('user_id', [0])[0])
        
        if user_id == 0:
            self.send_error(400, "user_id required")
            return
        
        couple = self.db.get_user_couple(user_id)
        
        if not couple:
            self.send_error(404, "Couple not found")
            return
        
        response = {
            'id': couple['id'],
            'user1_id': couple['user1_id'],
            'user2_id': couple['user2_id'],
            'user1_name': couple['user1_name'],
            'user2_name': couple['user2_name'],
            'created_at': couple['created_at']
        }
        
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_get_pet(self, params):
        """Получение информации о питомце"""
        couple_id = int(params.get('couple_id', [0])[0])
        
        if couple_id == 0:
            self.send_error(400, "couple_id required")
            return
        
        pet = self.db.get_couple_pet(couple_id)
        
        if not pet:
            self.send_error(404, "Pet not found")
            return
        
        # Обновляем статистику питомца
        updated_pet = self.pm._update_pet_stats_over_time(pet)
        
        response = {
            'id': updated_pet['id'],
            'name': updated_pet['name'],
            'type': updated_pet['pet_type'],
            'hunger': updated_pet['hunger'],
            'happiness': updated_pet['happiness'],
            'energy': updated_pet['energy'],
            'level': updated_pet['level'],
            'experience': updated_pet['experience'],
            'last_updated': updated_pet['last_updated']
        }
        
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_get_stats(self, params):
        """Получение статистики"""
        couple_id = int(params.get('couple_id', [0])[0])
        
        if couple_id == 0:
            self.send_error(400, "couple_id required")
            return
        
        actions = self.db.get_couple_actions(couple_id, limit=10)
        
        response = {
            'actions': actions
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
            couple_id = self.db.create_couple(user1_id, user2_id, user1_name, user2_name)
            
            response = {
                'success': True,
                'couple_id': couple_id,
                'message': 'Пара создана успешно!'
            }
            
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {
                'success': False,
                'error': str(e)
            }
            
            self.send_response(400)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
    
    def handle_create_pet(self, data):
        """Создание питомца"""
        couple_id = data.get('couple_id')
        pet_type = data.get('pet_type')
        name = data.get('name', 'Питомец')
        
        if not couple_id or not pet_type:
            self.send_error(400, "couple_id and pet_type required")
            return
        
        try:
            pet_id = self.db.create_pet(couple_id, pet_type, name)
            
            response = {
                'success': True,
                'pet_id': pet_id,
                'message': 'Питомец создан успешно!'
            }
            
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {
                'success': False,
                'error': str(e)
            }
            
            self.send_response(400)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
    
    def handle_pet_action(self, data):
        """Выполнение действия с питомцем"""
        couple_id = data.get('couple_id')
        action_type = data.get('action_type')
        user_id = data.get('user_id')
        
        if not couple_id or not action_type or not user_id:
            self.send_error(400, "couple_id, action_type and user_id required")
            return
        
        try:
            # Получаем питомца
            pet = self.db.get_couple_pet(couple_id)
            if not pet:
                self.send_error(404, "Pet not found")
                return
            
            # Выполняем действие
            updated_pet = self.pm.perform_action(couple_id, action_type, user_id)
            
            response = {
                'success': True,
                'pet': {
                    'id': updated_pet['id'],
                    'name': updated_pet['name'],
                    'type': updated_pet['pet_type'],
                    'hunger': updated_pet['hunger'],
                    'happiness': updated_pet['happiness'],
                    'energy': updated_pet['energy'],
                    'level': updated_pet['level'],
                    'experience': updated_pet['experience']
                },
                'action': action_type,
                'message': f'Действие "{ACTIONS[action_type]["name"]}" выполнено!'
            }
            
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {
                'success': False,
                'error': str(e)
            }
            
            self.send_response(400)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

def run_api_server(port=8000):
    """Запуск API сервера"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MiniAppAPIHandler)
    print(f"🌐 API сервер запущен на порту {port}")
    print(f"📡 URL: http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_api_server() 