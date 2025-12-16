from flask import Flask, render_template, request, redirect, url_for, session, flash # потужні імпорти чтоби було все ок
from scripts import * # потужні імпорти чтоби було все ок
from werkzeug.security import generate_password_hash, check_password_hash # потужні імпорти чтоби було все ок
from random import shuffle # потужні імпорти чтоби було все ок
import os # потужні імпорти чтоби було все ок

app = Flask(__name__)
app.secret_key = 'TrueKey'


@app.route('/')# це для того щоб при заході на сайт виводилось перше вхід в акаунт
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('index'))


@app.route('/index', methods=['GET', 'POST'])#при заході на акаунт вивод список вікторин
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    quizzes = get_quises()
    return render_template('index.html', username=session['username'], quizzes=quizzes)


@app.route('/registration', methods=['GET', 'POST'])#геристрація
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:#якщо не заповнене одне из полей
            flash('Заповніть всі поля')
            return redirect(url_for('registration'))

        hashed_password = generate_password_hash(password)#шифрування пароля

        try:# виконувать дію 1
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM name_user WHERE name = ?', (username,)).fetchone()
            if user:
                flash('Користувач вже існує')
                return redirect(url_for('registration'))

            conn.execute(# додавання пароля та імені
                'INSERT INTO name_user (name, password) VALUES (?, ?)',
                (username, hashed_password)
            )
            conn.commit()
            flash('Реєстрація успішна! Можете увійти.')
            return redirect(url_for('login'))

        except Exception:# якщо не вийшло зробити дію 1 виконувати дію 2
            flash('Помилка реєстрації')
            return redirect(url_for('registration'))
        finally:
            conn.close()

    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM name_user WHERE name = ?', (username,)).fetchone()

            if user and check_password_hash(user['password'], password):#перевірка чи є співпадає пароль на логін
                session['user_id'] = user['id']
                session['username'] = user['name']
                return redirect(url_for('index'))# якщо так тоді перекидуєм користувачання на вибір вікторини
            else:
                flash('Невірний логін або пароль')
                return redirect(url_for('login'))

        except Exception:
            flash('Помилка входу')
            return redirect(url_for('login'))
        finally:
            conn.close()

    return render_template('login.html')


@app.route('/list')
def list():
    # чи користувач авторизований
    if 'user_id' not in session:
        # Якщо користувач не увійшов, перенаправляємо його на сторінку логіну
        return redirect(url_for('login'))

    # Отримуємо список усіх користувачів бази даних
    users = get_all_users()

    return render_template('list.html', users=users)



@app.route('/quiz_start', methods=['POST'])
def quiz_start():
    if 'user_id' not in session:
        return redirect(url_for('login'))# чи користувач авторизований

    quiz_id = request.form.get('quiz')
    start_quiz(quiz_id)  
    return redirect(url_for('question'))


@app.route('/question', methods=['GET', 'POST'])
def question():
    
    if 'user_id' not in session:# Перевіряємо, чи користувач авторизований
        return redirect(url_for('login'))  
    
    if 'quiz' not in session:# Перевіряємо чи вибрано вікторину
        return redirect(url_for('index'))  

    # Якщо користувач надіслав відповідь 
    if request.method == 'POST':
        # Отримуємо відповідь користувача з форми
        user_answer = request.form.get('answer')

   
        correct_answer = session['current_question'][2]

        # Збільшуємо лічильник загальної кількості питань
        session['total'] += 1
        
        
        if user_answer == correct_answer:# Перевіряємо, чи відповідь правильна
            
            session['correct'] += 1 # Якщо правильно + 1 бал
            result_page = render_template(
                'true.html',
                user_answer=user_answer,
                username=session['username']
            )
        else:
            result_page = render_template(
                'false.html',
                user_answer=user_answer,
                username=session['username']
            )

        
        session['question_number'] += 1# для відображення прогресу
    
        return result_page
    result = get_question_after(session['last_question'], session['quiz'])


    if result is None:# Якщо питань більше немає 
        return redirect(url_for('result'))

    session['last_question'] = result[0] # Зберігаємо ID

    session['current_question'] = tuple(result)# Зберігаємо всю інформацію 

    
    question_text = result[1]# Текст питання

    answers = [result[2], result[3], result[4], result[5]]# Варіанти відповідей 

    
   
    shuffle(answers) # Перемішуємо варіанти

   
    return render_template( # Відображаємо  питання 
        'question.html',
        question=question_text,
        answers=answers,
        username=session['username'],
        current_number=session['question_number'],
        total_questions=session['question_total']
    )
@app.route('/exit_test', methods=['POST'])
def exit_test():
    return redirect(url_for('index'))


@app.route('/next_question', methods=['POST'])
def next_question():
    if 'user_id' not in session:  # чи авторизований користувач
        return redirect(url_for('login'))

    if 'quiz' not in session:  # чи вибрана вікторина
        return redirect(url_for('index'))

    result = get_question_after(session['last_question'], session['quiz'])  # отримати наступне питання

    if result is None:  # якщо питань немає
        return redirect(url_for('result'))

    session['last_question'] = result[0]  # зберегти id питання
    session['current_question'] = tuple(result)  # зберегти дані питання

    question_text = result[1]  # текст питання
    answers = [result[2], result[3], result[4], result[5]]  # варіанти відповідей
    shuffle(answers)  # перемішати варіанти

    return render_template( # Відображаємо  питання 
        'question.html',
        question=question_text,
        answers=answers,
        username=session['username'],
        current_number=session['question_number'],
        total_questions=session['question_total']
    )


@app.route('/result')
def result():
    if 'user_id' not in session:  # чи авторизований користувач
        return redirect(url_for('login'))

    if 'quiz' not in session:  # чи вибрана вікторина
        return redirect(url_for('index'))

    correct = session.get('correct', 0 )  # кількість правильних
    total = session.get('total', 0)      # всього відповідей

    update_user_score(session['user_id'], correct)  # оновити рахунок у БД
    end_quiz()  # очистити дані вікторини

    return render_template('result.html', correct=correct, total=total, username=session['username'])


@app.route('/logout')
def logout():
    end_quiz()       # завершити вікторину
    session.clear()  # очистити сесію
    return redirect(url_for('login'))  # на сторінку логіну


def update_user_score(user_id, correct_answers):
    conn = get_db_connection()
    conn.execute('UPDATE name_user SET score = score + ? WHERE id = ?', (correct_answers, user_id))  # додати бали
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT name, score FROM name_user ORDER BY score DESC').fetchall()  # топ користувачів
    conn.close()
    return users


def add_score_column():
    conn = get_db_connection()
    try:
        conn.execute('ALTER TABLE name_user ADD COLUMN score INTEGER DEFAULT 0')  # додати стовпець score
        conn.commit()
    except:
        pass
    finally:
        conn.close()


def init_db():
    if not os.path.exists(DATABASE):  # якщо БД немає створити
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE name_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                score INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()


if __name__ == '__main__':
    init_db()          # створення БД
    add_score_column() # додати колонку score якщо її нема
    init_quiz_db()     # ініціалізація вікторин
    app.run(debug=True)  # запуск Flask
