import random
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import PET_TYPES, ACTIONS, PET_NAMES

class PetManager:
    def __init__(self, database):
        self.db = database
    
    def create_pet_for_couple(self, couple_id: int, pet_type: str = None, name: str = None) -> Dict:
        """Создание питомца для пары"""
        if not pet_type:
            pet_type = random.choice(list(PET_TYPES.keys()))
        
        if not name:
            name = random.choice(PET_NAMES)
        
        pet_id = self.db.create_pet(couple_id, name, pet_type)
        
        return {
            "id": pet_id,
            "name": name,
            "type": pet_type,
            "hunger": 100,
            "happiness": 100,
            "energy": 100,
            "level": 1,
            "experience": 0
        }
    
    def get_pet_status(self, couple_id: int) -> Optional[Dict]:
        """Получение статуса питомца с обновленными показателями"""
        pet = self.db.get_pet(couple_id)
        if not pet:
            return None
        
        # Обновляем показатели на основе времени
        updated_pet = self._update_pet_stats_over_time(pet)
        
        return updated_pet
    
    def _update_pet_stats_over_time(self, pet: Dict) -> Dict:
        """Обновление статистики питомца на основе прошедшего времени"""
        last_updated = datetime.fromisoformat(pet['last_updated'].replace('Z', '+00:00'))
        now = datetime.now()
        time_diff = now - last_updated
        hours_passed = time_diff.total_seconds() / 3600
        
        if hours_passed < 0.1:  # Меньше 6 минут
            return pet
        
        pet_type = PET_TYPES[pet['pet_type']]
        
        # Рассчитываем изменения
        hunger_decrease = int(hours_passed * pet_type['hunger_rate'])
        happiness_decrease = int(hours_passed * pet_type['happiness_rate'])
        energy_decrease = int(hours_passed * pet_type['energy_rate'])
        
        new_hunger = max(0, pet['hunger'] - hunger_decrease)
        new_happiness = max(0, pet['happiness'] - happiness_decrease)
        new_energy = max(0, pet['energy'] - energy_decrease)
        
        # Обновляем в базе данных
        self.db.update_pet_stats(
            pet['id'],
            hunger=new_hunger,
            happiness=new_happiness,
            energy=new_energy
        )
        
        # Возвращаем обновленные данные
        pet.update({
            'hunger': new_hunger,
            'happiness': new_happiness,
            'energy': new_energy
        })
        
        return pet
    
    def perform_action(self, couple_id: int, user_id: int, action_type: str) -> Dict:
        """Выполнение действия с питомцем"""
        pet = self.get_pet_status(couple_id)
        if not pet:
            return {"error": "Питомец не найден"}
        
        if action_type not in ACTIONS:
            return {"error": "Неизвестное действие"}
        
        action = ACTIONS[action_type]
        
        # Применяем изменения
        new_hunger = max(0, min(100, pet['hunger'] + action['hunger']))
        new_happiness = max(0, min(100, pet['happiness'] + action['happiness']))
        new_energy = max(0, min(100, pet['energy'] + action['energy']))
        
        # Рассчитываем опыт
        experience_gain = self._calculate_experience_gain(action_type, pet)
        new_experience = pet['experience'] + experience_gain
        new_level = pet['level']
        
        # Проверяем повышение уровня
        if new_experience >= pet['level'] * 100:
            new_level = pet['level'] + 1
            new_experience = 0
        
        # Обновляем в базе данных
        self.db.update_pet_stats(
            pet['id'],
            hunger=new_hunger,
            happiness=new_happiness,
            energy=new_energy,
            level=new_level,
            experience=new_experience
        )
        
        # Логируем действие
        self.db.log_action(pet['id'], user_id, action_type)
        
        return {
            "success": True,
            "action": action_type,
            "pet": {
                "name": pet['name'],
                "type": pet['pet_type'],
                "hunger": new_hunger,
                "happiness": new_happiness,
                "energy": new_energy,
                "level": new_level,
                "experience": new_experience
            },
            "experience_gain": experience_gain,
            "level_up": new_level > pet['level']
        }
    
    def _calculate_experience_gain(self, action_type: str, pet: Dict) -> int:
        """Расчет получаемого опыта за действие"""
        base_exp = {
            "feed": 5,
            "play": 15,
            "sleep": 10,
            "pet": 8
        }
        
        # Бонус за высокое счастье
        happiness_bonus = pet['happiness'] // 20  # 0-5 бонусных очков
        
        return base_exp.get(action_type, 5) + happiness_bonus
    
    def get_pet_emoji_status(self, pet: Dict) -> str:
        """Получение эмодзи статуса питомца"""
        pet_type = PET_TYPES[pet['pet_type']]
        base_emoji = pet_type['emoji']
        
        # Определяем общее состояние
        avg_stats = (pet['hunger'] + pet['happiness'] + pet['energy']) / 3
        
        if avg_stats >= 80:
            mood = "😊"
        elif avg_stats >= 60:
            mood = "😐"
        elif avg_stats >= 40:
            mood = "😔"
        else:
            mood = "😢"
        
        return f"{base_emoji}{mood}"
    
    def get_pet_description(self, pet: Dict) -> str:
        """Получение описания состояния питомца"""
        descriptions = []
        
        if pet['hunger'] <= 20:
            descriptions.append("очень голоден")
        elif pet['hunger'] <= 40:
            descriptions.append("голоден")
        
        if pet['happiness'] <= 20:
            descriptions.append("очень грустный")
        elif pet['happiness'] <= 40:
            descriptions.append("грустный")
        elif pet['happiness'] >= 80:
            descriptions.append("очень счастливый")
        
        if pet['energy'] <= 20:
            descriptions.append("очень устал")
        elif pet['energy'] <= 40:
            descriptions.append("устал")
        elif pet['energy'] >= 80:
            descriptions.append("полон энергии")
        
        if not descriptions:
            descriptions.append("чувствует себя хорошо")
        
        return ", ".join(descriptions)
    
    def can_perform_action(self, action_type: str, pet: Dict) -> bool:
        """Проверка возможности выполнения действия"""
        if action_type == "play" and pet['energy'] < 10:
            return False
        if action_type == "sleep" and pet['energy'] > 80:
            return False
        return True 