#!/usr/bin/env python3
"""
Упрощенный API сервер для Render.com
"""

import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class SimpleAPIHandler(BaseHTTPRequestHandler):
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
        
        try:
            if path == '/api/health':
                self.handle_health()
            elif path == '/':
                self.handle_root()
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
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_root(self):
        """Главная страница"""
        response = {
            'message': 'Pet Couple API',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_health(self):
        """Проверка здоровья сервера"""
        response = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'platform': 'render'
        }
        
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_create_couple(self, data):
        """Создание пары (демо-режим)"""
        user1_id = data.get('user1_id')
        user2_id = data.get('user2_id')
        
        if not user1_id or not user2_id:
            self.send_error(400, "user1_id and user2_id required")
            return
        
        # Демо-режим - просто возвращаем успех
        couple_id = int(f"{user1_id}{user2_id}")
        response = {
            'success': True,
            'couple_id': couple_id,
            'message': 'Пара создана успешно! (Демо-режим)',
            'demo_mode': True
        }
        
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def run_server():
    """Запуск сервера"""
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Запуск упрощенного API сервера на порту {port}")
    print(f"📡 Переменные окружения: PORT={os.environ.get('PORT', 'не задан')}")
    
    try:
        server_address = ('0.0.0.0', port)
        httpd = HTTPServer(server_address, SimpleAPIHandler)
        print(f"✅ Сервер запущен на {server_address}")
        print(f"🔗 Health check: http://0.0.0.0:{port}/api/health")
        httpd.serve_forever()
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        raise

if __name__ == '__main__':
    run_server() 