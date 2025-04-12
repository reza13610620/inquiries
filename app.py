from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

from models import User

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', user=user)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm']

        # اعتبارسنجی اولیه
        if not re.match(r'^09\d{9}$', phone):
            flash("شماره موبایل معتبر نیست!", 'error')
        elif len(password) < 6:
            flash("رمز عبور باید حداقل ۶ کاراکتر باشد.", 'error')
        elif password != confirm:
            flash("رمز عبور و تکرار آن یکسان نیستند.", 'error')
        elif User.query.filter_by(phone=phone).first():
            flash("شماره موبایل قبلاً ثبت شده است.", 'error')
        else:
            new_user = User(phone=phone, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash("ثبت‌نام با موفقیت انجام شد. حالا وارد شوید.", 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = User.query.filter_by(phone=phone).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash("اطلاعات ورود نادرست است.", 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("با موفقیت خارج شدید.", 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
