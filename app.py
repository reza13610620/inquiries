from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'my_secret_key'

DB_NAME = 'inquiries.db'

# ایجاد دیتابیس و جدول کاربران
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# صفحه‌ی خانه
@app.route('/')
def index():
    return render_template('index.html')

# ثبت‌نام
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        if not phone or not password:
            flash('شماره موبایل و رمز عبور الزامی هستند.')
            return redirect(url_for('register'))

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, password))
            conn.commit()
            flash('ثبت‌نام با موفقیت انجام شد. حالا وارد شوید.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('این شماره قبلاً ثبت‌نام کرده است.')
        finally:
            conn.close()

    return render_template('register.html')

# ورود
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (phone, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['phone'] = user[1]
            flash('ورود با موفقیت انجام شد.')
            return redirect(url_for('profile'))
        else:
            flash('شماره یا رمز اشتباه است.')

    return render_template('login.html')

# پروفایل کاربر
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('ابتدا وارد شوید.')
        return redirect(url_for('login'))
    return render_template('profile.html', phone=session['phone'])

# خروج
@app.route('/logout')
def logout():
    session.clear()
    flash('با موفقیت خارج شدید.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
