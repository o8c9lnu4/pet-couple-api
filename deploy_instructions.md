# 🚀 Развертывание Mini App на GitHub Pages

## Быстрый способ (5 минут):

### 1. Создайте репозиторий на GitHub:
- Зайдите на github.com
- Нажмите "New repository"
- Назовите его `pet-couple-mini-app`
- Сделайте его Public
- НЕ добавляйте README, .gitignore или license

### 2. Загрузите файлы:
```bash
# В папке mini_app выполните:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pet-couple-mini-app.git
git push -u origin main
```

### 3. Включите GitHub Pages:
- В репозитории нажмите "Settings"
- Прокрутите до "Pages"
- В "Source" выберите "Deploy from a branch"
- В "Branch" выберите "main" и "/ (root)"
- Нажмите "Save"

### 4. Получите URL:
- GitHub Pages даст вам URL вида: `https://YOUR_USERNAME.github.io/pet-couple-mini-app/`
- Этот URL используйте в BotFather для Menu Button

## Альтернативные хостинги:

### Netlify (еще проще):
1. Зайдите на netlify.com
2. Перетащите папку `mini_app` в область загрузки
3. Получите URL сразу

### Vercel:
1. Зайдите на vercel.com
2. Подключите GitHub репозиторий
3. Автоматическое развертывание

## 🔧 Настройка в BotFather:

После получения URL:
1. @BotFather → /mybots → Ваш бот
2. Bot Settings → Menu Button
3. Введите полученный URL
4. Готово!

## 📱 Тестирование:

1. Найдите вашего бота в Telegram
2. Нажмите кнопку Menu
3. Mini App откроется прямо в Telegram! 