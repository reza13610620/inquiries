import sqlite3

# اتصال به پایگاه داده
conn = sqlite3.connect('inquiries.db')
cursor = conn.cursor()

# ایجاد جدول درخواست‌ها
cursor.execute('''
CREATE TABLE IF NOT EXISTS inquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    city TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("جدول 'inquiries' با موفقیت ایجاد شد.")