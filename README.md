# 🐾 Pet Couple API

API сервер для Telegram Mini App "Питомцы для пар"

## 🚀 Развертывание

Этот репозиторий автоматически развертывается на Railway.

### Endpoints

- `GET /api/health` - Проверка здоровья сервера
- `GET /api/user?user_id=123` - Получение информации о пользователе
- `POST /api/couple/create` - Создание пары
- `GET /api/couple?user_id=123` - Получение информации о паре
- `POST /api/pet/create` - Создание питомца
- `GET /api/pet?couple_id=123` - Получение информации о питомце
- `POST /api/pet/action` - Выполнение действия с питомцем

## 🛠️ Технологии

- Python 3.11
- SQLite
- HTTP Server
- python-telegram-bot

## 📦 Зависимости

См. `requirements.txt`

## 🔧 Конфигурация

См. `config.py` 