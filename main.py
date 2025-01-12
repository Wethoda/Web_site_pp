from flask import Flask, render_template

app = Flask(__name__)

# Пример данных о курсах (список словарей, где каждый словарь представляет один курс)
courses = [
    {"id": 1, "title": "Python для начинающих", "description": "Изучите основы Python."},
    {"id": 2, "title": "Flask: создание веб-приложений", "description": "Научитесь создавать сайты на Flask."},
    {"id": 3, "title": "SQL и базы данных", "description": "Основы работы с базами данных."},
]


# Маршрут для главной страницы
@app.route('/')
def index():
    # Рендерим шаблон index.html и передаем его в браузер
    return render_template('index.html')


# Маршрут для страницы со списком курсов
@app.route('/courses')
def show_courses():  # Переименовали функцию, чтобы избежать конфликта имен
    # Рендерим шаблон courses.html и передаем в него список курсов
    return render_template('courses.html', courses=courses)


# Маршрут для страницы с деталями курса
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    """
    Ищем курс по его ID в списке courses.
    next() возвращает первый элемент, который соответствует условию.
    Если курс не найден, возвращаем None.
    """
    course = next((course for course in courses if course["id"] == course_id), None)

    # Если курс найден, рендерим шаблон course_detail.html и передаем в него данные о курсе
    if course:
        return render_template('course_detail.html', course=course)

    # Если курс не найден, возвращаем сообщение об ошибке и статус 404
    return "Курс не найден", 404


# Маршрут для страницы "О нас"
@app.route('/about')
def about():
    # Рендерим шаблон about.html
    return render_template('about.html')


# Запуск приложения
if __name__ == '__main__':
    # Включаем режим отладки (debug=True), чтобы видеть ошибки в браузере
    app.run(debug=True)