from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import User, Product, database
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# Vercel uchun maxfiy kalitni o'zgartirish tavsiya etiladi, lekin hozircha shunday qolishi mumkin
app.secret_key = 'sizning_maxfiy_kalitingiz_12345'

# Ma'lumotlar bazasini ulash
@app.before_request
def before_request():
    database.connect(reuse_if_open=True)

@app.after_request
def after_request(response):
    if not database.is_closed():
        database.close()
    return response

# --- BAZANI YARATISH VA TO'LDIRISH FUNKSIYASI ---
def initialize_db():
    database.connect(reuse_if_open=True)
    database.create_tables([User, Product], safe=True)
    
    # Agar mahsulotlar bo'lmasa, ularni qo'shamiz
    if Product.select().count() == 0:
        demo_products = [
             {
                "name": "Klassik Oq Ko'ylak",
                "description": "Ofis va rasmiy uchrashuvlar uchun juda mos keladigan 100% paxtadan tikilgan oq ko'ylak.",
                "price": 180000,
                "category": "Erkaklar kiyimi",
                "image_url": "https://placehold.co/300x400/eceff1/2c3e50?text=Oq+Koylak"
            },
            {
                "name": "Jinsi Shim (Slim Fit)",
                "description": "Zamonaviy uslubdagi ko'k rangli jinsi shim. Kundalik kiyish uchun qulay.",
                "price": 220000,
                "category": "Erkaklar kiyimi",
                "image_url": "https://placehold.co/300x400/3498db/ffffff?text=Jinsi+Shim"
            },
            {
                "name": "Charm Kurtka",
                "description": "Haqiqiy charmdan ishlangan qora rangli bahorgi kurtka.",
                "price": 650000,
                "category": "Erkaklar kiyimi",
                "image_url": "https://placehold.co/300x400/2c3e50/ffffff?text=Charm+Kurtka"
            },
            {
                "name": "Ayollar Oqshom Libosi",
                "description": "Bayramlar va to'ylar uchun mo'ljallangan nafis qizil ko'ylak.",
                "price": 450000,
                "category": "Ayollar kiyimi",
                "image_url": "https://placehold.co/300x400/e74c3c/ffffff?text=Oqshom+Libosi"
            },
            {
                "name": "Yozgi Bluzka",
                "description": "Yengil matodan tikilgan, gulli naqshli yozgi bluzka.",
                "price": 120000,
                "category": "Ayollar kiyimi",
                "image_url": "https://placehold.co/300x400/f1c40f/ffffff?text=Yozgi+Bluzka"
            },
            {
                "name": "Klassik Yubka",
                "description": "Ishga kiyish uchun qulay, tizzagacha tushadigan qora yubka.",
                "price": 140000,
                "category": "Ayollar kiyimi",
                "image_url": "https://placehold.co/300x400/34495e/ffffff?text=Qora+Yubka"
            },
            {
                "name": "Bolalar Kombinezoni",
                "description": "1-3 yoshli bolalar uchun issiq va yumshoq kombinezon.",
                "price": 190000,
                "category": "Bolalar kiyimi",
                "image_url": "https://placehold.co/300x400/e67e22/ffffff?text=Kombinezon"
            },
            {
                "name": "Bolalar Futbolkasi",
                "description": "Multfilm qahramonlari tushirilgan paxtali futbolka.",
                "price": 60000,
                "category": "Bolalar kiyimi",
                "image_url": "https://placehold.co/300x400/2ecc71/ffffff?text=Futbolka"
            },
            {
                "name": "Nike Running Krossovka",
                "description": "Yugurish va sport uchun mo'ljallangan qulay poyabzal.",
                "price": 550000,
                "category": "Poyabzal",
                "image_url": "https://placehold.co/300x400/95a5a6/ffffff?text=Sport+Krossovka"
            },
            {
                "name": "Klassik Tufli",
                "description": "Erkaklar uchun rasmiy charm tufli.",
                "price": 380000,
                "category": "Poyabzal",
                "image_url": "https://placehold.co/300x400/5d4037/ffffff?text=Tufli"
            },
            {
                "name": "Ayollar Etigi",
                "description": "Qishki mavsum uchun issiq, poshnli etik.",
                "price": 420000,
                "category": "Poyabzal",
                "image_url": "https://placehold.co/300x400/8e44ad/ffffff?text=Etik"
            },
            {
                "name": "Charm Sumka",
                "description": "Ayollar uchun zamonaviy va sig'imli qo'l sumkasi.",
                "price": 280000,
                "category": "Aksessuarlar",
                "image_url": "https://placehold.co/300x400/d35400/ffffff?text=Sumka"
            },
            {
                "name": "Qishki Sharf",
                "description": "Yungdan to'qilgan issiq sharf (uniseks).",
                "price": 75000,
                "category": "Aksessuarlar",
                "image_url": "https://placehold.co/300x400/1abc9c/ffffff?text=Sharf"
            },
            {
                "name": "Qo'l Soati",
                "description": "Metall tasmali klassik uslubdagi qo'l soati.",
                "price": 300000,
                "category": "Aksessuarlar",
                "image_url": "https://placehold.co/300x400/7f8c8d/ffffff?text=Soat"
            },
            {
                "name": "Quyosh ko'zoynagi",
                "description": "Yozgi mavsum uchun zamonaviy qora ko'zoynak.",
                "price": 90000,
                "category": "Aksessuarlar",
                "image_url": "https://placehold.co/300x400/2c3e50/ffffff?text=Kozoynak"
            }
        ]
        for product in demo_products:
            Product.create(
                name=product["name"],
                description=product["description"],
                price=product["price"],
                category=product["category"],
                image_url=product["image_url"]
            )
    database.close()

# Dastur ishga tushganda bir marta bazani tekshirib olamiz
# Vercel har safar serverni yangidan ko'targani uchun buni funksiya ichida chaqiramiz
try:
    initialize_db()
except Exception as e:
    print(f"Bazani yaratishda xatolik: {e}")


# --- ROUTELAR ---

@app.route('/')
def index():
    try:
        products = Product.select()
        return render_template('index.html', products=products)
    except:
        # Xatolik bo'lsa qayta urinib ko'rish
        initialize_db()
        products = Product.select()
        return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Parollar bir xil emas!', 'danger')
            return redirect(url_for('register'))
        
        if User.select().where(User.username == username).exists():
            flash('Bu foydalanuvchi nomi band!', 'danger')
            return redirect(url_for('register'))
        
        if User.select().where(User.email == email).exists():
            flash('Bu email allaqachon ro\'yxatdan o\'tgan!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        User.create(username=username, email=email, password=hashed_password)
        flash('Ro\'yxatdan o\'tdingiz! Endi tizimga kirishingiz mumkin.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Iltimos, avval tizimga kiring!', 'warning')
        return redirect(url_for('login'))
    
    products = Product.select()
    return render_template('dashboard.html', products=products)

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

@app.route('/logout')
def logout():
    session.clear()
    flash('Tizimdan chiqdingiz!', 'info')
    return redirect(url_for('index'))

# Vercel uchun bu qism shart emas, lekin local ishlashi uchun qoldiramiz
if __name__ == '__main__':
    app.run(debug=True)