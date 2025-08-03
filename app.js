// Telegram Web App API
let tg = window.Telegram.WebApp;

// Инициализация приложения
tg.ready();
tg.expand();

// Настройка темы
tg.setHeaderColor('#667eea');
tg.setBackgroundColor('#667eea');

// Глобальные переменные
let currentUser = null;
let currentPet = null;
let currentCouple = null;

// Конфигурация
const PET_TYPES = {
    cat: { emoji: '🐱', name: 'Котик' },
    dog: { emoji: '🐕', name: 'Пёсик' },
    rabbit: { emoji: '🐰', name: 'Кролик' }
};

const ACTIONS = {
    feed: { emoji: '🍽️', name: 'Покормить', hunger: 30, happiness: 5, energy: 0 },
    play: { emoji: '🎾', name: 'Поиграть', hunger: -5, happiness: 25, energy: -10 },
    sleep: { emoji: '😴', name: 'Уложить спать', hunger: -2, happiness: 0, energy: 40 },
    pet: { emoji: '🤗', name: 'Погладить', hunger: 0, happiness: 15, energy: 0 }
};

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

// Инициализация скрипта приветствия
const welcomeScript = new WelcomeScript();

// Инициализация приложения
async function initApp() {
    try {
        // Получаем данные пользователя
        currentUser = tg.initDataUnsafe?.user || {
            id: Math.floor(Math.random() * 1000000),
            first_name: 'Пользователь'
        };
        
        // Показываем ID пользователя
        document.getElementById('my-id').textContent = currentUser.id;
        
        // Загружаем данные пользователя с сервера
        await loadUserData();
        
        // Загружаем данные питомца
        await loadPetData();
        
        // Обновляем интерфейс
        updatePetDisplay();
        
        // Показываем приветственное сообщение
        showWelcomeMessage();
        
    } catch (error) {
        console.error('Ошибка инициализации:', error);
        showError('Ошибка загрузки данных');
    }
}

// Загрузка данных пользователя
async function loadUserData() {
    try {
        // Используем относительный URL для работы на GitHub Pages
        const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://your-api-domain.com';
        const response = await fetch(`${apiUrl}/api/user?user_id=${currentUser.id}`);
        if (response.ok) {
            const userData = await response.json();
            currentUser.hasCouple = userData.has_couple;
            currentUser.coupleId = userData.couple_id;
            
            if (userData.has_couple) {
                await loadCoupleData();
            }
        }
    } catch (error) {
        console.error('Ошибка загрузки данных пользователя:', error);
        // Используем демо-данные если сервер недоступен
        console.log('API недоступен, используем демо-данные');
        
        // Проверяем, есть ли сохраненная пара в localStorage
        const savedCouple = localStorage.getItem('couple_data');
        if (savedCouple) {
            currentCouple = JSON.parse(savedCouple);
            currentUser.hasCouple = true;
            currentUser.coupleId = currentCouple.id;
        } else {
            currentUser.hasCouple = false;
        }
    }
}

// Загрузка данных пары
async function loadCoupleData() {
    try {
        const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://your-api-domain.com';
        const response = await fetch(`${apiUrl}/api/couple?user_id=${currentUser.id}`);
        if (response.ok) {
            currentCouple = await response.json();
        }
    } catch (error) {
        console.error('Ошибка загрузки данных пары:', error);
    }
}

// Загрузка данных питомца
async function loadPetData() {
    try {
        // Если у пользователя есть пара, загружаем питомца с сервера
        if (currentUser.hasCouple && currentUser.coupleId) {
            const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://your-api-domain.com';
            const response = await fetch(`${apiUrl}/api/pet?couple_id=${currentUser.coupleId}`);
            if (response.ok) {
                const petData = await response.json();
                currentPet = {
                    id: petData.id,
                    name: petData.name,
                    type: petData.type,
                    hunger: petData.hunger,
                    happiness: petData.happiness,
                    energy: petData.energy,
                    level: petData.level,
                    experience: petData.experience,
                    lastUpdated: petData.last_updated
                };
                return;
            }
        }
        
        // Если сервер недоступен или нет пары, используем демо-данные
        const savedPet = localStorage.getItem('pet_data');
        if (savedPet) {
            currentPet = JSON.parse(savedPet);
        } else {
            currentPet = createDemoPet();
        }
        
    } catch (error) {
        console.error('Ошибка загрузки питомца:', error);
        currentPet = createDemoPet();
    }
}

// Создание демо-питомца
function createDemoPet() {
    return {
        id: 1,
        name: 'Мурзик',
        type: 'cat',
        hunger: 80,
        happiness: 90,
        energy: 75,
        level: 1,
        experience: 25,
        lastUpdated: new Date().toISOString()
    };
}

// Обновление отображения питомца
function updatePetDisplay() {
    if (!currentPet) return;
    
    const petType = PET_TYPES[currentPet.type];
    
    // Обновляем карточку питомца
    document.getElementById('pet-emoji').textContent = petType.emoji;
    document.getElementById('pet-name').textContent = currentPet.name;
    document.getElementById('pet-description').textContent = getPetDescription(currentPet);
    
    // Обновляем статистику
    document.getElementById('hunger-bar').style.width = currentPet.hunger + '%';
    document.getElementById('hunger-value').textContent = currentPet.hunger + '/100';
    
    document.getElementById('happiness-bar').style.width = currentPet.happiness + '%';
    document.getElementById('happiness-value').textContent = currentPet.happiness + '/100';
    
    document.getElementById('energy-bar').style.width = currentPet.energy + '%';
    document.getElementById('energy-value').textContent = currentPet.energy + '/100';
    
    // Обновляем уровень
    document.getElementById('pet-level').textContent = currentPet.level;
    document.getElementById('pet-exp').textContent = currentPet.experience;
    document.getElementById('pet-exp-max').textContent = currentPet.level * 100;
    
    // Обновляем статистику
    document.getElementById('stat-level').textContent = currentPet.level;
    document.getElementById('stat-exp').textContent = currentPet.experience + '/' + (currentPet.level * 100);
}

// Получение описания питомца
function getPetDescription(pet) {
    const descriptions = [];
    
    if (pet.hunger <= 20) {
        descriptions.push('очень голоден');
    } else if (pet.hunger <= 40) {
        descriptions.push('голоден');
    }
    
    if (pet.happiness <= 20) {
        descriptions.push('очень грустный');
    } else if (pet.happiness <= 40) {
        descriptions.push('грустный');
    } else if (pet.happiness >= 80) {
        descriptions.push('очень счастливый');
    }
    
    if (pet.energy <= 20) {
        descriptions.push('очень устал');
    } else if (pet.energy <= 40) {
        descriptions.push('устал');
    } else if (pet.energy >= 80) {
        descriptions.push('полон энергии');
    }
    
    if (descriptions.length === 0) {
        descriptions.push('чувствует себя хорошо');
    }
    
    return descriptions.join(', ');
}

// Переключение экранов
function showScreen(screenId) {
    // Скрываем все экраны
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Показываем нужный экран
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
    }
    
    // Обновляем данные при показе экранов
    if (screenId === 'pet-status' || screenId === 'statistics') {
        updatePetDisplay();
    }
}

// Копирование ID
function copyMyId() {
    const myId = document.getElementById('my-id').textContent;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(myId).then(() => {
            showSuccess('ID скопирован!');
        });
    } else {
        // Fallback для старых браузеров
        const textArea = document.createElement('textarea');
        textArea.value = myId;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showSuccess('ID скопирован!');
    }
}

// Создание пары
async function createCouple() {
    const partnerId = document.getElementById('partner-id').value;
    
    if (!partnerId) {
        showError('Введите ID партнера');
        return;
    }
    
    if (partnerId == currentUser.id) {
        showError('Вы не можете создать пару с самим собой');
        return;
    }
    
    try {
        // Проверяем, можем ли подключиться к API
        const apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://your-railway-app.railway.app';
        
        // Пробуем подключиться к API
        const response = await fetch(`${apiUrl}/api/couple/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user1_id: currentUser.id,
                user2_id: parseInt(partnerId),
                user1_name: currentUser.first_name || 'Пользователь 1',
                user2_name: 'Партнер'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentUser.hasCouple = true;
            currentUser.coupleId = result.couple_id;
            
            showSuccess('Пара создана! Теперь можете создать питомца.');
            showScreen('main-menu');
        } else {
            showError(result.error || 'Ошибка создания пары');
        }
        
    } catch (error) {
        console.error('Ошибка создания пары:', error);
        
        // Если API недоступен, используем демо-режим
        console.log('API недоступен, используем демо-режим');
        
        // Создаем демо-пару
        currentCouple = {
            id: Date.now(),
            user1_id: currentUser.id,
            user2_id: parseInt(partnerId),
            created_at: new Date().toISOString()
        };
        
        currentUser.hasCouple = true;
        currentUser.coupleId = currentCouple.id;
        
        // Сохраняем в localStorage
        localStorage.setItem('couple_data', JSON.stringify(currentCouple));
        
        showSuccess('Пара создана! (Демо-режим) Теперь можете создать питомца.');
        showScreen('main-menu');
    }
}

// Выполнение действия с питомцем
async function performAction(actionType) {
    if (!currentPet) {
        showError('У вас нет питомца');
        return;
    }
    
    const action = ACTIONS[actionType];
    if (!action) {
        showError('Неизвестное действие');
        return;
    }
    
    try {
        // Применяем изменения
        currentPet.hunger = Math.max(0, Math.min(100, currentPet.hunger + action.hunger));
        currentPet.happiness = Math.max(0, Math.min(100, currentPet.happiness + action.happiness));
        currentPet.energy = Math.max(0, Math.min(100, currentPet.energy + action.energy));
        
        // Добавляем опыт
        const expGain = calculateExpGain(actionType, currentPet);
        currentPet.experience += expGain;
        
        // Проверяем повышение уровня
        if (currentPet.experience >= currentPet.level * 100) {
            currentPet.level += 1;
            currentPet.experience = 0;
            showLevelUp();
        }
        
        // Обновляем время
        currentPet.lastUpdated = new Date().toISOString();
        
        // Сохраняем данные
        localStorage.setItem('pet_data', JSON.stringify(currentPet));
        
        // Обновляем отображение
        updatePetDisplay();
        
        // Показываем результат
        showActionResult(action, expGain);
        
    } catch (error) {
        console.error('Ошибка выполнения действия:', error);
        showError('Ошибка выполнения действия');
    }
}

// Расчет получаемого опыта
function calculateExpGain(actionType, pet) {
    const baseExp = {
        feed: 5,
        play: 15,
        sleep: 10,
        pet: 8
    };
    
    const happinessBonus = Math.floor(pet.happiness / 20);
    return baseExp[actionType] + happinessBonus;
}

// Показ результата действия
function showActionResult(action, expGain) {
    const resultDiv = document.getElementById('action-result');
    const resultEmoji = document.getElementById('result-emoji');
    const resultText = document.getElementById('result-text');
    
    resultEmoji.textContent = action.emoji;
    resultText.textContent = `${action.name} выполнено! +${expGain} опыта`;
    
    resultDiv.classList.remove('hidden');
    
    // Скрываем через 3 секунды
    setTimeout(() => {
        resultDiv.classList.add('hidden');
    }, 3000);
}

// Показ повышения уровня
function showLevelUp() {
    tg.showAlert(`🎉 ${currentPet.name} достиг уровня ${currentPet.level}!`);
}

// Показ успешного сообщения
function showSuccess(message) {
    tg.showAlert(message);
}

// Показ ошибки
function showError(message) {
    tg.showAlert('❌ ' + message);
}

// Автоматическое обновление статистики питомца
function updatePetStatsOverTime() {
    if (!currentPet) return;
    
    const lastUpdated = new Date(currentPet.lastUpdated);
    const now = new Date();
    const hoursPassed = (now - lastUpdated) / (1000 * 60 * 60);
    
    if (hoursPassed < 0.1) return; // Меньше 6 минут
    
    // Скорости изменения для разных типов питомцев
    const rates = {
        cat: { hunger: 2, happiness: 1.5, energy: 1.8 },
        dog: { hunger: 2.5, happiness: 1.2, energy: 2.0 },
        rabbit: { hunger: 1.8, happiness: 2.0, energy: 1.5 }
    };
    
    const rate = rates[currentPet.type];
    
    // Рассчитываем изменения
    const hungerDecrease = Math.floor(hoursPassed * rate.hunger);
    const happinessDecrease = Math.floor(hoursPassed * rate.happiness);
    const energyDecrease = Math.floor(hoursPassed * rate.energy);
    
    // Применяем изменения
    currentPet.hunger = Math.max(0, currentPet.hunger - hungerDecrease);
    currentPet.happiness = Math.max(0, currentPet.happiness - happinessDecrease);
    currentPet.energy = Math.max(0, currentPet.energy - energyDecrease);
    
    // Обновляем время
    currentPet.lastUpdated = now.toISOString();
    
    // Сохраняем данные
    localStorage.setItem('pet_data', JSON.stringify(currentPet));
    
    // Обновляем отображение
    updatePetDisplay();
}

// Запуск автоматического обновления
setInterval(updatePetStatsOverTime, 60000); // Каждую минуту

// Обработка событий Telegram
tg.onEvent('viewportChanged', function() {
    // Обработка изменения размера окна
});

tg.onEvent('themeChanged', function() {
    // Обработка изменения темы
});

// Экспорт функций для использования в HTML
window.showScreen = showScreen;
window.copyMyId = copyMyId;
window.createCouple = createCouple;
window.performAction = performAction;

// Показ приветственного сообщения
function showWelcomeMessage() {
    try {
        let message;
        
        // Проверяем, новый ли это пользователь
        const isNewUser = !localStorage.getItem('user_visited');
        localStorage.setItem('user_visited', 'true');
        
        if (isNewUser) {
            message = welcomeScript.getNewUserWelcome(currentUser);
        } else {
            // Проверяем ежедневное сообщение
            const dailyMessage = welcomeScript.getDailyMessage(currentUser, currentPet);
            if (dailyMessage) {
                message = dailyMessage;
            } else {
                message = welcomeScript.getReturnWelcome(currentUser, currentPet);
            }
        }
        
        // Показываем сообщение в красивом модальном окне
        showWelcomeModal(message);
        
    } catch (error) {
        console.error('Ошибка показа приветствия:', error);
    }
}

// Показ модального окна с приветствием
function showWelcomeModal(message) {
    // Создаем модальное окно
    const modal = document.createElement('div');
    modal.className = 'welcome-modal';
    modal.innerHTML = `
        <div class="welcome-content">
            <div class="welcome-header">
                <h2>🐾 Добро пожаловать!</h2>
                <button class="close-btn" onclick="closeWelcomeModal()">×</button>
            </div>
            <div class="welcome-body">
                <p>${message.replace(/\n/g, '<br>')}</p>
            </div>
            <div class="welcome-footer">
                <button class="welcome-btn" onclick="closeWelcomeModal()">Понятно! 🎉</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Анимация появления
    setTimeout(() => {
        modal.classList.add('show');
    }, 100);
}

// Закрытие модального окна
function closeWelcomeModal() {
    const modal = document.querySelector('.welcome-modal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// Экспорт функций приветствия
window.closeWelcomeModal = closeWelcomeModal; 