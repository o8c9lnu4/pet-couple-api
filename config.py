import os

# Настройки бота
BOT_TOKEN = "7535736348:AAElpL088-zbm2k193TDYdOlwjN2xIEFRqQ"

# Настройки питомца
PET_NAMES = [
    "Мурзик", "Бобик", "Рыжик", "Снежок", "Лапка", "Мяу", "Гав", "Пушок",
    "Звездочка", "Солнышко", "Радуга", "Облачко", "Цветочек", "Бабочка"
]

PET_TYPES = {
    "cat": {
        "name": "Котик",
        "emoji": "🐱",
        "hunger_rate": 2,
        "happiness_rate": 1.5,
        "energy_rate": 1.8
    },
    "dog": {
        "name": "Пёсик", 
        "emoji": "🐕",
        "hunger_rate": 2.5,
        "happiness_rate": 1.2,
        "energy_rate": 2.0
    },
    "rabbit": {
        "name": "Кролик",
        "emoji": "🐰",
        "hunger_rate": 1.8,
        "happiness_rate": 2.0,
        "energy_rate": 1.5
    }
}

# Настройки действий
ACTIONS = {
    "feed": {
        "name": "Покормить",
        "emoji": "🍽️",
        "hunger": 30,
        "happiness": 5,
        "energy": 0
    },
    "play": {
        "name": "Поиграть",
        "emoji": "🎾",
        "hunger": -5,
        "happiness": 25,
        "energy": -10
    },
    "sleep": {
        "name": "Уложить спать",
        "emoji": "😴",
        "hunger": -2,
        "happiness": 0,
        "energy": 40
    },
    "pet": {
        "name": "Погладить",
        "emoji": "🤗",
        "hunger": 0,
        "happiness": 15,
        "energy": 0
    }
}

# Настройки уведомлений
NOTIFICATION_INTERVAL = 3600  # 1 час в секундах 