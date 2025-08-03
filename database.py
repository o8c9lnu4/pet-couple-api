import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str = "pets.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица пар
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS couples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    user1_name TEXT,
                    user2_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user1_id, user2_id)
                )
            ''')
            
            # Таблица питомцев
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    couple_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    pet_type TEXT NOT NULL,
                    hunger INTEGER DEFAULT 100,
                    happiness INTEGER DEFAULT 100,
                    energy INTEGER DEFAULT 100,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (couple_id) REFERENCES couples (id)
                )
            ''')
            
            # Таблица действий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pet_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pet_id) REFERENCES pets (id)
                )
            ''')
            
            conn.commit()
    
    def create_couple(self, user1_id: int, user2_id: int, user1_name: str, user2_name: str) -> int:
        """Создание новой пары"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO couples (user1_id, user2_id, user1_name, user2_name)
                VALUES (?, ?, ?, ?)
            ''', (user1_id, user2_id, user1_name, user2_name))
            conn.commit()
            return cursor.lastrowid
    
    def get_couple(self, user1_id: int, user2_id: int) -> Optional[Dict]:
        """Получение информации о паре"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM couples 
                WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
            ''', (user1_id, user2_id, user2_id, user1_id))
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def get_user_couple(self, user_id: int) -> Optional[Dict]:
        """Получение пары пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM couples 
                WHERE user1_id = ? OR user2_id = ?
            ''', (user_id, user_id))
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def create_pet(self, couple_id: int, name: str, pet_type: str) -> int:
        """Создание нового питомца"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pets (couple_id, name, pet_type)
                VALUES (?, ?, ?)
            ''', (couple_id, name, pet_type))
            conn.commit()
            return cursor.lastrowid
    
    def get_pet(self, couple_id: int) -> Optional[Dict]:
        """Получение питомца пары"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM pets WHERE couple_id = ?
            ''', (couple_id,))
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def update_pet_stats(self, pet_id: int, hunger: int = None, happiness: int = None, 
                        energy: int = None, level: int = None, experience: int = None):
        """Обновление статистики питомца"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            updates = []
            values = []
            
            if hunger is not None:
                updates.append("hunger = ?")
                values.append(max(0, min(100, hunger)))
            
            if happiness is not None:
                updates.append("happiness = ?")
                values.append(max(0, min(100, happiness)))
            
            if energy is not None:
                updates.append("energy = ?")
                values.append(max(0, min(100, energy)))
            
            if level is not None:
                updates.append("level = ?")
                values.append(level)
            
            if experience is not None:
                updates.append("experience = ?")
                values.append(experience)
            
            if updates:
                updates.append("last_updated = CURRENT_TIMESTAMP")
                values.append(pet_id)
                
                query = f"UPDATE pets SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
    
    def log_action(self, pet_id: int, user_id: int, action_type: str):
        """Логирование действия с питомцем"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO actions (pet_id, user_id, action_type)
                VALUES (?, ?, ?)
            ''', (pet_id, user_id, action_type))
            conn.commit()
    
    def get_recent_actions(self, pet_id: int, limit: int = 10) -> List[Dict]:
        """Получение последних действий с питомцем"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM actions 
                WHERE pet_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (pet_id, limit))
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    def update_couple_names(self, couple_id: int, user1_name: str, user2_name: str):
        """Обновление имен в паре"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE couples 
                SET user1_name = ?, user2_name = ?
                WHERE id = ?
            ''', (user1_name, user2_name, couple_id))
            conn.commit() 