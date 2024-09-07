from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'products.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM products')
    products = cur.fetchall()
    db.close()
    return render_template('dashboard.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    
    db = get_db()
    db.execute('INSERT INTO products (name, description, price) VALUES (?, ?, ?)', (name, description, price))
    db.commit()
    db.close()
    
    return redirect(url_for('dashboard'))

@app.route('/api/products', methods=['GET'])
def api_get_products():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM products')
    products = cur.fetchall()
    db.close()
    return jsonify([dict(row) for row in products])

if __name__ == '__main__':
    app.run(debug=True)
