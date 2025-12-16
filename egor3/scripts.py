import sqlite3  # Імпортуємо модуль для роботи з базою даних SQLite
from werkzeug.security import generate_password_hash, check_password_hash  # Імпортуємо функції для хешування та перевірки паролів
import os  # Імпортуємо модуль для взаємодії з операційною системою (наприклад, для перевірки існування файлу)

DATABASE = 'users.db'  # Визначаємо константу для імені файлу бази даних користувачів
QUIZ_DATABASE = 'quiz.sqlite'  # Визначаємо константу для імені файлу бази даних вікторин

def get_db_connection():  # Функція для отримання з'єднання з основною базою даних користувачів
    conn = sqlite3.connect(DATABASE)  # Встановлюємо з'єднання з базою даних
    conn.row_factory = sqlite3.Row  # Встановлюємо row_factory, щоб можна було отримувати результати як словники (за іменами стовпців)
    return conn  # Повертаємо об'єкт з'єднання

def init_db():  # Функція для ініціалізації (створення) основної бази даних користувачів, якщо вона не існує
    if not os.path.exists(DATABASE):  # Перевіряємо, чи існує файл бази даних
        conn = get_db_connection()  # Отримуємо з'єднання з базою даних
        conn.execute('''  
            CREATE TABLE name_user (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                name TEXT NOT NULL,  
                password TEXT NOT NULL 
            )
        ''')
        conn.commit()  # Зберігаємо зміни (створення таблиці)
        conn.close()  # Закриваємо з'єднання

def get_quiz_connection():  # Функція для отримання з'єднання з базою даних вікторин
    conn = sqlite3.connect(QUIZ_DATABASE)  # Встановлюємо з'єднання з базою даних вікторин
    conn.row_factory = sqlite3.Row  # Встановлюємо row_factory для зручного доступу до даних
    return conn  # Повертаємо об'єкт з'єднання

def init_quiz_db():  # Функція для ініціалізації бази даних вікторин
    if not os.path.exists(QUIZ_DATABASE):  # Перевіряємо, чи існує файл бази даних вікторин
        create_quiz_tables()  # Якщо не існує, створюємо необхідні таблиці
        add_sample_quizzes()  # Додаємо зразки вікторин
        add_sample_questions()  # Додаємо зразки запитань
        auto_add_links()  # Автоматично зв'язуємо запитання з вікторинами

def create_quiz_tables():  # Функція для створення таблиць у базі даних вікторин
    conn = get_quiz_connection()  # Отримуємо з'єднання з базою даних вікторин
    cursor = conn.cursor()  # Створюємо об'єкт курсора для виконання запитів
    
    cursor.execute('PRAGMA foreign_keys=on')  # Вмикаємо підтримку зовнішніх ключів
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS quiz ( 
            id INTEGER PRIMARY KEY,  
            name VARCHAR)''')  # Назва вікторини
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS question (
            id INTEGER PRIMARY KEY,  
            question VARCHAR,  
            answer VARCHAR,  
            wrong1 VARCHAR,  
            wrong2 VARCHAR,  
            wrong3 VARCHAR)''') 
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_content (  
            id INTEGER PRIMARY KEY, 
            quiz_id INTEGER,  
            question_id INTEGER,  
            FOREIGN KEY (quiz_id) REFERENCES quiz (id),  
            FOREIGN KEY (question_id) REFERENCES question (id))''')  
    
    conn.commit()  # Зберігаємо зміни
    conn.close()  # Закриваємо з'єднання

def add_sample_quizzes():  # Функція для додавання зразків вікторин
    quizes = [  # Список кортежів з назвами вікторин
        ('Вікторина 1 — Географія', ),
        ('Вікторина 2 — Тварини', ),
        ('Вікторина 3 — Логіка', )
    ]
    
    conn = get_quiz_connection()  # Отримуємо з'єднання
    cursor = conn.cursor()  # Отримуємо курсор
    cursor.executemany('INSERT INTO quiz (name) VALUES (?)', quizes)  # Вставляємо дані у таблицю quiz
    conn.commit()  # Зберігаємо зміни
    conn.close()  # Закриваємо з'єднання

def add_sample_questions():  # Функція для додавання зразків запитань
    '''Додає нові запитання'''  # Документальний рядок
    questions = [  # Список кортежів із запитаннями та відповідями
        ('Скільки океанів на Землі?', '5', '2', '4', '7'),  # Запитання з 1 по 5 для Вікторини 1
        ('Який континент найбільший?', 'Євразія', 'Північна Америка', 'Південна Америка', 'Африка'),
        ('Яка найвища гора у світі?', 'Еверест', 'Кіліманджаро', 'Монблан', 'Арарат'),
        ('Яка найбільша пустеля у світі?', 'Сахара', 'Гобі', 'Калахарі', 'Атакама'),
        ('Яка країна має найбільше населення?', 'Китай', 'Індія', 'США', 'Бразилія'),

        ('Яка тварина є найвищою у світі?', 'Жираф', 'Слон', 'Верблюд', 'Кінь'),  # Запитання з 6 по 10 для Вікторини 2
        ('Яка тварина відкладає яйця, але є ссавцем?', 'Качкодзьоб', 'Їжак', 'Кролик', 'Кіт'),
        ('Який птах не вміє літати?', 'Пінгвін', 'Орел', 'Лелека', 'Ворон'),
        ('Яка тварина має найдовший язик?', 'Мурахоїд', 'Жираф', 'Лев', 'Кенгуру'),
        ('Хто є "царем звірів"?', 'Лев', 'Тигр', 'Ведмідь', 'Слон'),

        ('Що можна зламати, але не можна торкнутися?', 'Обіцянку', 'Скло', 'Палицю', 'Тінь'),  # Запитання з 11 по 15 для Вікторини 3
        ('Що завжди йде, але ніколи не рухається?', 'Час', 'Вітер', 'Дорога', 'Тінь'),
        ('Що зранку має чотири ноги, вдень — дві, а ввечері — три?', 'Людина', 'Слон', 'Кішка', 'Пес'),
        ('Що має шию, але не має голови?', 'Пляшка', 'Сорочка', 'Слон', 'Риба'),
        ('Що завжди перед нами, але ми його не бачимо?', 'Майбутнє', 'Повітря', 'Дим', 'Дорога')
    ]

    conn = get_quiz_connection()  # Отримуємо з'єднання
    cursor = conn.cursor()  # Отримуємо курсор
    # Вставляємо дані у таблицю question
    cursor.executemany('INSERT INTO question (question, answer, wrong1, wrong2, wrong3) VALUES (?,?,?,?,?)', questions)
    conn.commit()  # Зберігаємо зміни
    conn.close()  # Закриваємо з'єднання

def auto_add_links():  # Функція для автоматичного зв'язування запитань з вікторинами
    '''Ручне з’єднання запитань з вікторинами'''  # Документальний рядок
    conn = get_quiz_connection()  # Отримуємо з'єднання
    cursor = conn.cursor()  # Отримуємо курсор
    cursor.execute('PRAGMA foreign_keys=on')  # Вмикаємо зовнішні ключі

    links = []  # Створюємо порожній список для зв'язків
    for quiz_id in range(1, 4):  # Проходимо по ID вікторин (1, 2, 3)
        # Проходимо по ID запитань, які належать поточній вікторині (по 5 запитань на вікторину)
        for question_id in range((quiz_id - 1) * 5 + 1, quiz_id * 5 + 1):
            links.append((quiz_id, question_id))  # Додаємо кортеж (ID вікторини, ID запитання) до списку зв'язків

    # Вставляємо дані у таблицю quiz_content
    cursor.executemany('INSERT INTO quiz_content (quiz_id, question_id) VALUES (?,?)', links)
    conn.commit()  # Зберігаємо зміни
    conn.close()  # Закриваємо з'єднання

def get_question_after(last_id=0, vict_id=1):  # Функція для отримання наступного запитання

    conn = get_quiz_connection()  # Отримуємо з'єднання
    cursor = conn.cursor()  # Отримуємо курсор
    
    query = '''  
    SELECT quiz_content.id, question.question, question.answer, question.wrong1, question.wrong2, question.wrong3
    FROM question, quiz_content  
    WHERE quiz_content.question_id == question.id  
    AND quiz_content.id > ? AND quiz_content.quiz_id == ?  
    ORDER BY quiz_content.id '''  # Сортуємо за ID зв'язку
    
    # Виконуємо запит, передаючи last_id та vict_id
    cursor.execute(query, [last_id, vict_id])
    result = cursor.fetchone()  # Отримуємо перший результат (наступне запитання)
    conn.close()  # Закриваємо з'єднання
    
    return result  # Повертаємо результат (запитання або None)

def get_quises():  # Функція для отримання списку всіх вікторин
    '''Отримати список усіх вікторин'''  # Документальний рядок
    conn = get_quiz_connection()  # Отримуємо з'єднання
    cursor = conn.cursor()  # Отримуємо курсор
    
    cursor.execute('SELECT * FROM quiz ORDER BY id')  # Вибираємо всі вікторини, сортуємо за ID
    result = cursor.fetchall()  # Отримуємо всі знайдені рядки
    conn.close()  # Закриваємо з'єднання
    
    return result  # Повертаємо список вікторин

def start_quiz(quiz_id):  # Функція для початку вікторини
    from flask import session  # Імпортуємо 'session' з Flask
    session['quiz'] = int(quiz_id)  # Зберігаємо ID поточної вікторини у сесії
    session['last_question'] = 0  # Ініціалізуємо ID останнього питання у сесії (0 - означає початок)
    session['correct'] = 0  # Ініціалізуємо лічильник правильних відповідей
    session['total'] = 0  # Ініціалізуємо лічильник загальної кількості відповідей
    session['question_number'] = 1  # Ініціалізуємо поточний номер запитання
    session['question_total'] = count_questions_in_quiz(quiz_id)  # Зберігаємо загальну кількість запитань у вікторині

def end_quiz():  # Функція для завершення вікторини
    from flask import session  # Імпортуємо 'session' з Flask
    if 'quiz' in session:  # Перевіряємо, чи є активна вікторина
        session.pop('quiz', None)  # Видаляємо ID вікторини з сесії
        session.pop('last_question', None)  # Видаляємо ID останнього питання
        session.pop('correct', None)  # Видаляємо лічильник правильних відповідей
        session.pop('total', None)  # Видаляємо лічильник загальної кількості відповідей

def count_questions_in_quiz(quiz_id):  # Функція для підрахунку питань у вікторині
    '''Повертає кількість питань у вибяраній вікторині'''  # Документальний рядок
    conn = get_quiz_connection()  # Отримуємо з'єднання
    cursor = conn.cursor()  # Отримуємо курсор
    # Виконуємо запит для підрахунку рядків у quiz_content за quiz_id
    cursor.execute('SELECT COUNT(*) FROM quiz_content WHERE quiz_id = ?', (quiz_id,))
    count = cursor.fetchone()[0]  # Отримуємо результат підрахунку
    conn.close()  # Закриваємо з'єднання
    return count  # Повертаємо кількість питань