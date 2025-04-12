from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# اتصال به پایگاه داده MySQL
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='inquiries_db'
    )
    return conn

# صفحه اصلی - فرم ثبت درخواست
@app.route('/', methods=['GET', 'POST'])
def index():
    # خواندن لیست محصولات از پایگاه داده
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])

        # خواندن شهر از session (پروفایل کاربر)
        city = session.get('user_city', 'شهر نامشخص')

        # ذخیره درخواست در پایگاه داده
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO inquiries (product_id, quantity, city)
                VALUES (%s, %s, %s)
            ''', (product_id, quantity, city))
            conn.commit()
        except Exception as e:
            print(f"Error during inquiry save: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))

    return render_template('index.html', products=products)

# صفحه نمایش درخواست‌ها
@app.route('/view', methods=['GET'])
def view_inquiries():
    product_filter = request.args.get('product', '')
    city_filter = request.args.get('city', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = '''
        SELECT i.id, p.name AS product_name, i.quantity, i.city, i.created_at
        FROM inquiries i
        JOIN products p ON i.product_id = p.id
        WHERE 1=1
    '''
    params = []

    if product_filter:
        query += ' AND p.name = %s'
        params.append(product_filter)
    if city_filter:
        query += ' AND i.city = %s'
        params.append(city_filter)

    cursor.execute(query, params)
    inquiries = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('view.html', inquiries=inquiries)

# صفحه ثبت نام
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        password = request.form['password']

        # هش کردن رمز عبور (در اینجا به صورت ساده نگهداری می‌شود، در واقع باید از الگوریتم‌های امنتری مثل bcrypt استفاده کنید)
        password_hash = password  # TODO: استفاده از هشگر رمز عبور امن

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (phone_number, password_hash)
                VALUES (%s, %s)
            ''', (phone_number, password_hash))
            conn.commit()
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during registration: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

# صفحه ورود
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM users WHERE phone_number = %s
        ''', (phone_number,))
        user = cursor.fetchone()

        if user and user['password_hash'] == password:  # TODO: مقایسه هش رمز عبور
            session['user_id'] = user['id']
            return redirect(url_for('profile'))

        return "Invalid credentials"

    return render_template('login.html')

# صفحه پروفایل
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # دریافت اطلاعات پروفایل کاربر
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT * FROM addresses WHERE user_id = %s
    ''', (user_id,))
    address = cursor.fetchone()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        province = request.form['province']
        city = request.form['city']
        detailed_address = request.form['detailed_address']
        postal_code = request.form['postal_code']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # اگر آدرس قبلی وجود داشت، آن را به‌روزرسانی کنید
            if address:
                cursor.execute('''
                    UPDATE addresses
                    SET province = %s, city = %s, detailed_address = %s, postal_code = %s
                    WHERE user_id = %s
                ''', (province, city, detailed_address, postal_code, user_id))
            else:
                # در غیر اینصورت، آدرس جدید را ذخیره کنید
                cursor.execute('''
                    INSERT INTO addresses (user_id, province, city, detailed_address, postal_code)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (user_id, province, city, detailed_address, postal_code))
            conn.commit()
            return "آدرس با موفقیت ذخیره شد."
        except Exception as e:
            print(f"Error during address save: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    return render_template('profile.html', address=address)

# API برای دریافت شهرها
@app.route('/api/cities/<int:province_id>', methods=['GET'])
def get_cities(province_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name FROM cities WHERE province_id = %s', (province_id,))
    cities = cursor.fetchall()
    cursor.close()
    conn.close()
    return {'cities': cities}

if __name__ == '__main__':
    app.run(debug=True)





@app.route('/test-db-connection')
def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {str(e)}"