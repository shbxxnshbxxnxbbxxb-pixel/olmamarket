from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import User, Product, database
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'sizning_maxfiy_kalitingiz_12345'

# Ma'lumotlar bazasini ulash
@app.before_request
def before_request():
    database.connect(reuse_if_open=True)

@app.after_request
def after_request(response):
    database.close()
    return response

# Asosiy sahifa
@app.route('/')
def index():
    products = Product.select()
    return render_template('index.html', products=products)

# Registratsiya sahifasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Parollarni tekshirish
        if password != confirm_password:
            flash('Parollar bir xil emas!', 'danger')
            return redirect(url_for('register'))
        
        # Foydalanuvchi mavjudligini tekshirish
        if User.select().where(User.username == username).exists():
            flash('Bu foydalanuvchi nomi band!', 'danger')
            return redirect(url_for('register'))
        
        if User.select().where(User.email == email).exists():
            flash('Bu email allaqachon ro\'yxatdan o\'tgan!', 'danger')
            return redirect(url_for('register'))
        
        # Yangi foydalanuvchi yaratish
        hashed_password = generate_password_hash(password)
        User.create(username=username, email=email, password=hashed_password)
        flash('Ro\'yxatdan o\'tdingiz! Endi tizimga kirishingiz mumkin.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login sahifasi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            user = User.get(User.username == username)
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                flash(f'Xush kelibsiz, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Noto\'g\'ri parol!', 'danger')
        except User.DoesNotExist:
            flash('Foydalanuvchi topilmadi!', 'danger')
    
    return render_template('login.html')

# Dashboard (Foydalanuvchi sahifasi)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Iltimos, avval tizimga kiring!', 'warning')
        return redirect(url_for('login'))
    
    products = Product.select()
    return render_template('dashboard.html', products=products)

# Mahsulot qo'shish (admin uchun)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        flash('Iltimos, avval tizimga kiring!', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        image_url = request.form['image_url']
        
        Product.create(
            name=name,
            description=description,
            price=price,
            category=category,
            image_url=image_url
        )
        flash('Mahsulot muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_product.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Tizimdan chiqdingiz!', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ma'lumotlar bazasini yaratish
    database.create_tables([User, Product], safe=True)
    
    # Demo mahsulotlarni qo'shish (agar bo'sh bo'lsa)
    if Product.select().count() == 0:
        Product.create(
            name="Ko'ylak",
            description="Zamonaviy va qulay ko'ylak",
            price=150000,
            category="Erkaklar kiyimi",
            image_url="https://via.placeholder.com/300x400?text=Koylak"
        )
        Product.create(
            name="Jinsi",
            description="Klassik jinsi shim",
            price=200000,
            category="Erkaklar kiyimi",
            image_url="https://via.placeholder.com/300x400?text=Jinsi"
        )
        Product.create(
            name="Ko'ylak (Ayollar)",
            description="Elegant va zamonaviy ko'ylak",
            price=180000,
            category="Ayollar kiyimi",
            image_url="https://via.placeholder.com/300x400?text=Koylak+Ayol"
        )
    
    app.run(debug=True)