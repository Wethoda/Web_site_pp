import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('courses.db')
cursor = conn.cursor()

# Добавляем тестовые курсы
courses = [
    ("Python для начинающих", "10 часов", "Начинающий", "Изучите основы Python: синтаксис, типы данных, функции и многое другое."),
    ("Flask: создание веб-приложений", "15 часов", "Средний", "Научитесь создавать сайты на Flask: маршруты, шаблоны, базы данных."),
    ("SQL и базы данных", "20 часов", "Тяжелый", "Основы работы с базами данных: SQL-запросы, проектирование баз данных."),
]

# Функция для проверки существования курса по названию
def course_exists(title):
    cursor.execute('SELECT id FROM courses WHERE title = ?', (title,))
    return cursor.fetchone() is not None

# Вставляем данные в таблицу, если курс с таким названием еще не существует
for course in courses:
    title, duration, difficulty, description = course
    if not course_exists(title):
        cursor.execute('''
        INSERT INTO courses (title, duration, difficulty, description) VALUES (?, ?, ?, ?)
        ''', (title, duration, difficulty, description))
        print(f"Курс '{title}' успешно добавлен.")
    else:
        print(f"Курс '{title}' уже существует и не будет добавлен.")

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Добавление курсов завершено.")