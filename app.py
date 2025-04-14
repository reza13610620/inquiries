from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime


def get_user_default_city(user_id):
    conn = sqlite3.connect('inquiries.db')
    cursor = conn.cursor()
    cursor.execute("SELECT city_id FROM addresses WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None



from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# 📌 اتصال به پایگاه داده
def get_db_connection():
    conn = sqlite3.connect('inquiries.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🟢 نمایش فرم ثبت محصول
@app.route('/register_product', methods=['GET'])
def register_product_form():
    return render_template('register_product.html')

# 🟢 پردازش ثبت محصول
@app.route('/register_product', methods=['POST'])
def register_product():
    product_name = request.form['product_name']
    product_code = request.form['product_code']
    unit = request.form['unit']
    category = request.form['category']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO products (name, code, unit, category) VALUES (?, ?, ?, ?)',
        (product_name, product_code, unit, category)
    )
    conn.commit()
    conn.close()

    return redirect('/register_product')

# اجرای اپ
if __name__ == '__main__':
    app.run(debug=True)







from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('inquiries.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/inquiry", methods=["GET"])
def inquiry_form():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    cities = conn.execute("SELECT * FROM cities").fetchall()
    
    # فرض بر اینه که کاربر لاگین کرده و ID در session هست
    user_id = session.get("user_id")
    default_city_id = None

    if user_id:
        address = conn.execute("SELECT city_id FROM addresses WHERE user_id = ?", (user_id,)).fetchone()
        if address:
            default_city_id = address["city_id"]
    
    conn.close()
    return render_template("form_inquiry.html", products=products, cities=cities, default_city_id=default_city_id)


@app.route("/submit_inquiry", methods=["POST"])
def submit_inquiry():
    product_id = request.form["product_id"]
    unit = request.form["unit"]
    quantity = request.form["quantity"]
    city_id = request.form["city_id"]
    user_id = session.get("user_id")

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO inquiries (product_id, unit, quantity, city_id, user_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (product_id, unit, quantity, city_id, user_id, datetime.now()))
    conn.commit()
    conn.close()

    return redirect("/inquiry")
