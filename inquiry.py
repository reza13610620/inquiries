@app.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    if 'user_id' not in session:
        flash("برای ثبت استعلام ابتدا وارد شوید")
        return redirect('/login')

    conn = sqlite3.connect('inquiries.db')
    cursor = conn.cursor()

    # گرفتن محصولات برای لیست کشویی
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()

    # گرفتن شهر پیش‌فرض کاربر
    default_city = get_user_default_city(session['user_id'])

    if request.method == 'POST':
        product_id = request.form['product_id']
        unit = request.form['unit']
        quantity = request.form['quantity']
        city_id = request.form.get('city_id') or default_city
        created_at = datetime.now()

        cursor.execute("""
            INSERT INTO inquiries (product_id, unit, quantity, city_id, user_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, unit, quantity, city_id, session['user_id'], created_at))

        conn.commit()
        conn.close()
        flash("استعلام با موفقیت ثبت شد")
        return redirect('/')

    conn.close()
    return render_template('form_inquiry.html', products=products, default_city=default_city)
