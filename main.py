from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'kosxgfelv963'

# Константа для количества курсов на странице
COURSES_PER_PAGE = 5

# Функция для получения данных из базы данных с пагинацией
def get_courses(page=1):
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    offset = (page - 1) * COURSES_PER_PAGE
    cursor.execute('SELECT * FROM courses LIMIT ? OFFSET ?', (COURSES_PER_PAGE, offset))
    courses = cursor.fetchall()  # Получаем курсы для текущей страницы
    conn.close()
    return courses

# Функция для получения общего количества курсов
def get_total_courses():
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM courses')
    total = cursor.fetchone()[0]  # Получаем общее количество курсов
    conn.close()
    return total

# Функция для получения курса по ID
def get_course_by_id(course_id):
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM courses WHERE id = ?', (course_id,))
    course = cursor.fetchone()  # Получаем одну запись
    conn.close()
    return course

# Функция для добавления курса
def add_course(title, duration, difficulty, category, description):
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO courses(title, duration, difficulty, category, description) VALUES (?, ?, ?, ?, ?)",
                   (title, duration, difficulty, category, description,))
    conn.commit()
    conn.close()

def update_course(course_id, title, duration, difficulty, category, description):
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE courses
        SET title = ?, duration = ?, difficulty = ?, category = ?, description = ?
        WHERE id = ?''', (title, duration, difficulty, category, description, course_id))
    conn.commit()
    conn.close()

def register_user(username, password, role='user'):
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    cursor.execute('''INSERT INTO users(username, password, role) VALUES(?, ?, ?)''', (username, hashed_password, role))
    conn.commit()
    conn.close()

def verify_users(username, password):
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT id, password, role FROM users WHERE username = ?''', (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[1], password):
        return user
    return None

# Маршрут для главной страницы
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для страницы со списком курсов
@app.route('/courses')
@app.route('/courses')
def show_courses():
    page = request.args.get('page', 1, type=int)  # Получаем номер страницы из запроса
    query = request.args.get('query', '').strip()  # Получаем поисковый запрос
    category = request.args.get('category', '').strip()  # Получаем категорию

    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()

    # Базовый SQL-запрос
    sql = 'SELECT * FROM courses WHERE 1=1'
    params = []

    # Добавляем условия поиска, если они есть
    if query:
        sql += ' AND title LIKE ?'
        params.append(f'%{query}%')

    if category:
        sql += ' AND category = ?'
        params.append(category)

    # Добавляем пагинацию
    offset = (page - 1) * COURSES_PER_PAGE
    sql += ' LIMIT ? OFFSET ?'
    params.extend([COURSES_PER_PAGE, offset])

    # Выполняем запрос
    cursor.execute(sql, params)
    courses = cursor.fetchall()

    # Получаем общее количество курсов для пагинации
    cursor.execute('SELECT COUNT(*) FROM courses WHERE 1=1' + (' AND title LIKE ?' if query else '') + (
        ' AND category = ?' if category else ''), params[:-2])
    total_courses = cursor.fetchone()[0]
    total_pages = (total_courses + COURSES_PER_PAGE - 1) // COURSES_PER_PAGE

    conn.close()

    return render_template('courses.html', courses=courses, page=page, total_pages=total_pages)

@app.route('/search')
def search_courses():
    query = request.args.get('query', '').strip()  # Получаем поисковый запрос
    category = request.args.get('category', '').strip()  # Получаем категорию
    return redirect(url_for('show_courses', query=query, category=category, page=1))

# Маршрут для страницы с деталями курса
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = get_course_by_id(course_id)
    if course:
        return render_template('course_detail.html', course=course)
    return "Курс не найден", 404

# Маршрут для отображения формы добавления курса
@app.route('/add_course', methods=['GET'])
def show_add_course_form():
    if 'user_id' not in session or session.get('role') != 'admin':  # Проверяем, что пользователь — админ
        flash('Доступ запрещен. Только администраторы могут добавлять курсы.', 'error')
        return redirect(url_for('show_courses'))
    return render_template('add_course.html')

# Маршрут для обработки данных формы
@app.route('/add_course', methods=['POST'])
def add_course_form():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещен. Только администраторы могут добавлять курсы.', 'error')
        return redirect(url_for('show_courses'))

    title = request.form['title']
    duration = request.form['duration']
    difficulty = request.form['difficulty']
    category = request.form['category']
    description = request.form['description']

    add_course(title, duration, difficulty, category, description)
    flash("Курс успешно добавлен", 'success')
    return redirect(url_for('show_courses'))

@app.route('/edit_course/<int:course_id>', methods=['GET'])
def show_edit_course_form(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещен. Только администраторы могут редактировать курсы.', 'error')
        return redirect(url_for('show_courses'))
    course = get_course_by_id(course_id)
    if course:
        return render_template('edit_course.html', course=course)
    return "Курс не найден", 404

@app.route('/edit_course/<int:course_id>', methods=['POST'])
def edit_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Доступ запрещен. Только администраторы могут редактировать курсы.', 'error')
        return redirect(url_for('show_courses'))

    title = request.form['title']
    duration = request.form['duration']
    difficulty = request.form['difficulty']
    category = request.form['category']
    description = request.form['description']

    update_course(course_id, title, duration, difficulty, category, description)
    flash('Успешно вы изменил курс', 'success')
    return redirect(url_for('show_courses'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            register_user(username, password)
            flash('Регистрация прошла успешно. Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Пользователь с таким именем уже существует.", 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = verify_users(username, password)
        if user:
            session['user_id'] = user[0]
            session['role'] = user[2]
            flash('Вход выполнен успешно.', 'success')
            return redirect(url_for('show_courses'))
        else:
            flash('Неверное имя пользователя или пороль', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Вы успешно вышли из системы.', 'success')
    return redirect(url_for('index'))

# Маршрут для страницы "О нас"
@app.route('/about')
def about():
    return render_template('about.html')

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)