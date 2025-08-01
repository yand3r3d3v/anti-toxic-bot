# AntiToxicBot 🤖🚫

AntiToxicBot — это Telegram-бот, который борется с токсичностью в чатах. Он использует [Perspective API](https://www.perspectiveapi.com/) для анализа сообщений и выдает муты за токсичное поведение.

## Как это работает 💡

Perspective API использует модели машинного обучения для идентификации оскорбительных комментариев.

Perspective предоставляют оценки для нескольких различных атрибутов. Помимо основного атрибута Toxicity, Perspective может предоставлять оценки для следующих атрибутов:

- Severe Toxicity
- Insult
- Profanity
- Identity attack
- Threat
- Sexually explicit

### Доступность языков 🌐

Perspective API бесплатен и доступен для использования на арабском, китайском, чешском, нидерландском, английском, французском, немецком, хинди, индонезийском, итальянском, японском, корейском, польском, португальском, русском, испанском и шведском языках.

## Новые функции 🌟

### Накопление поинтов токсичности

- Старым участникам накапливаются поинты токсичности за каждое токсичное сообщение.
- При достижении 3 поинтов, пользователь получает мут на определенное время.
- Поинты сбрасываются после выдачи мута.

### Увеличение времени мута для частых нарушителей

- Пользователи, которые часто нарушают правила, будут получать увеличенное время мута.
- Мут увеличивается на 2 часа за каждые 3 накопленных поинта.

### История мутов и выдачи поинтов

- Бот хранит историю всех мутов и накопленных поинтов для каждого пользователя.
- История доступна через команду `/mute_history`.

### Специальные правила для новых участников

- Новые участники (менее 3 часов в чате) имеют более низкий порог токсичности для выдачи мута.
- Порог токсичности для новых участников снижен на 10%, чтобы быстрее реагировать на их поведение.

## Установка и настройка 🛠️

### С использованием Poetry

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/0niel/anti-toxic-bot.git
   ```
2. Перейдите в директорию проекта:
   ```bash
   cd anti-toxic-bot
   ```
3. Установите зависимости:
   ```bash
   poetry install
   ```
4. Создайте файл `.env` и добавьте ваши ключи API:
   ```env
   PERSPECTIVE_API_KEY=your_perspective_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

### С использованием Docker

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yand3r3d3v/anti-toxic-bot.git
   ```
2. Перейдите в директорию проекта:
   ```bash
   cd anti-toxic-bot
   ```
3. Соберите Docker-образ:
   ```bash
   docker build -t antitoxicbot .
   ```
4. Создайте файл `.env` и добавьте ваши ключи API:
   ```env
   PERSPECTIVE_API_KEY=your_perspective_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

## Запуск 🚀

### С использованием Poetry

1. Запустите бота:
   ```bash
   poetry run python main.py
   ```

### С использованием Docker

1. Запустите контейнер:
   ```bash
   docker run --env-file .env --name bot antitoxicbot
   ```

## Команды 📋

- `/start` — приветственное сообщение.
- `/muted_users` — получить список замученных пользователей.
- `/unmute <user_id>` — размутить пользователя.
- `/toxic_users` — получить антирейтинг самых токсичных пользователей.
- `/mute_history` — получить историю мутов и выдачи поинтов.

## Makefile команды 🛠️

- `make format` — Запуск инструментов форматирования кода.
- `make build` — Сборка Docker-образа.
- `make run` — Запуск Docker-контейнера.
- `make stop` — Остановка и удаление Docker-контейнера.
- `make restart` — Остановка, пересборка и запуск Docker-контейнера.
- `make clean` — Удаление Docker-образа.
- `make logs` — Показ логов работающего контейнера.
- `make shell` — Открытие шелла внутри работающего контейнера.
- `make prune` — Удаление всех неиспользуемых объектов Docker.

## Лицензия 📜

Этот проект лицензируется на условиях лицензии MIT.
