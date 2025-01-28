import sqlite3

# Подключаемся к базе данных (если файла нет, он будет создан)
conn = sqlite3.connect('courses.db')
cursor = conn.cursor()

# Создаем таблицу courses, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    duration TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    description TEXT NOT NULL
)
''')

# Создаем таблицу users, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
)
''')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Таблицы 'courses' и 'users' успешно созданы.")