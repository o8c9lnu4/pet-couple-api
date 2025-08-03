#!/usr/bin/env python3
"""
Простой HTTP сервер для тестирования Telegram Mini App
"""

import http.server
import socketserver
import os
import ssl
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Добавляем CORS заголовки для разработки
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Обработка preflight запросов
        self.send_response(200)
        self.end_headers()

def create_ssl_context():
    """Создание SSL контекста для HTTPS"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # Генерируем самоподписанный сертификат
    try:
        context.load_cert_chain('cert.pem', 'key.pem')
        return context
    except FileNotFoundError:
        print("⚠️ SSL сертификаты не найдены. Запускаем без HTTPS.")
        return None

def generate_self_signed_cert():
    """Генерация самоподписанного сертификата"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from datetime import datetime, timedelta
        
        # Генерируем приватный ключ
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Создаем сертификат
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Moscow"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Moscow"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Pet Tamagotchi"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Сохраняем сертификат и ключ
        with open("cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open("key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ Самоподписанный сертификат создан!")
        return True
        
    except ImportError:
        print("❌ Для создания SSL сертификата установите cryptography:")
        print("pip install cryptography")
        return False

def main():
    PORT = 8000
    HTTPS_PORT = 8443
    
    print("🐾 Запуск сервера для Telegram Mini App")
    print("=" * 50)
    
    # Проверяем наличие файлов
    if not os.path.exists('index.html'):
        print("❌ Файл index.html не найден!")
        print("Убедитесь, что вы запускаете сервер из папки mini_app/")
        return
    
    # Создаем SSL сертификат если нужно
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("🔐 Создание SSL сертификата...")
        if generate_self_signed_cert():
            print("✅ Сертификат создан успешно!")
        else:
            print("⚠️ Продолжаем без HTTPS")
    
    # Запускаем HTTP сервер
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🌐 HTTP сервер запущен на http://localhost:{PORT}")
            print(f"📱 Откройте в браузере: http://localhost:{PORT}")
            
            # Запускаем HTTPS сервер если есть сертификат
            if os.path.exists('cert.pem') and os.path.exists('key.pem'):
                try:
                    with socketserver.TCPServer(("", HTTPS_PORT), CustomHTTPRequestHandler) as httpsd:
                        context = create_ssl_context()
                        if context:
                            httpsd.socket = context.wrap_socket(httpsd.socket, server_side=True)
                            print(f"🔒 HTTPS сервер запущен на https://localhost:{HTTPS_PORT}")
                            print(f"📱 Для Telegram Mini App используйте: https://localhost:{HTTPS_PORT}")
                            
                            # Запускаем оба сервера в разных потоках
                            import threading
                            https_thread = threading.Thread(target=httpsd.serve_forever)
                            https_thread.daemon = True
                            https_thread.start()
                            
                            print("\n💡 Для тестирования в Telegram:")
                            print("1. Используйте ngrok для туннелирования:")
                            print("   ngrok http 8443")
                            print("2. Скопируйте HTTPS URL из ngrok")
                            print("3. Укажите его в BotFather")
                            
                except Exception as e:
                    print(f"⚠️ HTTPS сервер не запущен: {e}")
            
            print("\n🛑 Для остановки нажмите Ctrl+C")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    main() 