from peewee import *
from datetime import datetime

# SQLite ma'lumotlar bazasi
database = SqliteDatabase('kiyim_dokoni.db')

# User modeli (Foydalanuvchi)
class User(Model):
    username = CharField(unique=True, max_length=50)
    email = CharField(unique=True, max_length=100)
    password = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        database = database
        table_name = 'users'

# Product modeli (Mahsulot)
class Product(Model):
    name = CharField(max_length=100)
    description = TextField()
    price = FloatField()
    category = CharField(max_length=50)
    image_url = CharField(max_length=500, null=True)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        database = database
        table_name = 'products'

# Ma'lumotlar bazasini yaratish
if __name__ == '__main__':
    database.connect()
    database.create_tables([User, Product], safe=True)
    print("Ma'lumotlar bazasi muvaffaqiyatli yaratildi!")
    database.close()