from peewee import *
from datetime import datetime
import os

# Vercelda /tmp papkasini ishlatish, aks holda joriy papka
if 'VERCEL' in os.environ:
    DB_NAME = '/tmp/kiyim_dokoni.db'
else:
    DB_NAME = 'kiyim_dokoni.db'

database = SqliteDatabase(DB_NAME)

class User(Model):
    username = CharField(unique=True, max_length=50)
    email = CharField(unique=True, max_length=100)
    password = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        database = database
        table_name = 'users'

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
