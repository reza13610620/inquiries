# auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3

auth_bp = Blueprint('auth', __name__)

DB_PATH = 'inquiries.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        if not phone or not password:
            flash('تمامی فیلدها الزامی هستند')
            return redirect(url_for('auth.register'))

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE phone = ?', (phone,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('این شماره موبایل قبلاً ثبت شده است')
            return redirect(url_for('auth.register'))

        cur.execute('INSERT INTO users (phone, password) VALUES (?, ?)', (phone, password))
        conn.commit()
        conn.close()
        flash('ثبت‌نام با موفقیت انجام شد. لطفا وارد شوید.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        if not phone or not password:
            flash('تمامی فیلدها الزامی هستند')
            return redirect(url_for('auth.login'))

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE phone = ? AND password = ?', (phone, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['phone'] = user['phone']
            flash('خوش آمدید!')
            return redirect(url_for('profile'))

        flash('اطلاعات وارد شده نادرست است')
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('با موفقیت خارج شدید')
    return redirect(url_for('auth.login'))
