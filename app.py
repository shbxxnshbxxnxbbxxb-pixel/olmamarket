from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import User, Product, database
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'sizning_maxfiy_kalitingiz_12345'

# --- BAZA BILAN ISHLASH ---
# Vercel uchun maxsus himoya funksiyasi
def get_db():
    try:
        database.connect(reuse_if_open=True)
    except Exception as e:
        print(f"Baza ulanish xatosi: {e}")

@app.before_request
def before_request():
    get_db()

@app.after_request
def after_request(response):
    try:
        if not database.is_closed():
            database.close()
    except:
        pass
    return response

# --- INIT DB FUNCTION ---
# Bazani yaratishni xavfsiz usulda bajaramiz
def initialize_app():
    try:
        database.connect(reuse_if_open=True)
        database.create_tables([User, Product], safe=True)
        
        # Agar mahsulotlar yo'q bo'lsa, qo'shamiz
        if Product.select().count() == 0:
            demo_products = [
                {"name": "Oq Ko'ylak", "description": "Klassik oq ko'ylak", "price": 180000, "category": "Erkaklar", "image_url": "https://placehold.co/300x400/eceff1/2c3e50?text=Koylak"},
                {"name": "Jinsi Shim", "description": "Ko'k jinsi shim", "price": 220000, "category": "Erkaklar", "image_url": "https://placehold.co/300x400/3498db/ffffff?text=Jinsi"},
                {"name": "Ayollar Libosi", "description": "Qizil oqshom libosi", "price": 450000, "category": "Ayollar", "image_url": "https://placehold.co/300x400/e74c3c/ffffff?text=Libos"}
            ]
            for p in demo_products:
                Product.create(name=p['name'], description=p['description'], price=p['price'], category=p['category'], image_url=p['image_url'])
            print("Demo mahsulotlar qo'shildi")
            
        database.close()
    except Exception as e:
        # Agar xatolik bo'lsa, konsolga chiqaramiz, lekin saytni to'xtatmaymiz
        print(f"INIT ERROR: {e}")

# Dastur ishga tushganda bir marta chaqiramiz
initialize_app()

# --- ROUTELAR ---

@app.route('/')
def index():
    try:
        products = Product.select()
        return render_template('index.html', products=products)
    except Exception as e:
        return f"Xatolik yuz berdi: {e} <br> Iltimos sahifani yangilang."

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                flash('Parollar mos emas', 'danger')
                return redirect(url_for('register'))
            
            hashed = generate_password_hash(password)
            User.create(username=username, email=email, password=hashed)
            flash('Muvaffaqiyatli!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')
    except Exception as e:
        return f"Ro'yxatdan o'tishda xato: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            try:
                user = User.get(User.username == username)
                if check_password_hash(user.password, password):
                    session['user_id'] = user.id
                    session['username'] = user.username
                    return redirect(url_for('dashboard'))
                else:
                    flash('Parol xato', 'danger')
            except User.DoesNotExist:
                flash('Foydalanuvchi topilmadi', 'danger')
        return render_template('login.html')
    except Exception as e:
        return f"Kirishda xato: {e}"

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        products = Product.select()
        return render_template('dashboard.html', products=products)
    except:
        return "Dashboard xatosi"

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            Product.create(
                name=request.form['name'],
                description=request.form['description'],
                price=float(request.form['price']),
                category=request.form['category'],
                image_url=request.form['image_url']
            )
            return redirect(url_for('dashboard'))
        except Exception as e:
            return f"Mahsulot qo'shishda xato: {e}"
    return render_template('add_product.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)