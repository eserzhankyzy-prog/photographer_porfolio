from flask import Flask
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from models import User, db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


with app.app_context():
    db.create_all()
    sqlite_columns = {
        'order': {
            'customer_email': 'VARCHAR(120)',
            'notes': 'TEXT',
            'user_id': 'INTEGER',
        },
        'review': {
            'user_id': 'INTEGER',
            'created_at': 'DATETIME',
            'approved': 'BOOLEAN DEFAULT 0',
        },
        'photo': {
            'category': "VARCHAR(50) DEFAULT 'Wedding'",
            'description': 'TEXT',
            'price': 'FLOAT',
            'shoot_date': 'DATE',
            'created_at': 'DATETIME',
        },
    }

    for table_name, required_columns in sqlite_columns.items():
        existing_columns = {
            row[1]
            for row in db.session.execute(text(f"PRAGMA table_info('{table_name}')"))
        }
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                db.session.execute(
                    text(f'ALTER TABLE "{table_name}" ADD COLUMN {column_name} {column_type}')
                )

    db.session.execute(
        text("UPDATE photo SET category = 'Wedding' WHERE category IS NULL OR category = ''")
    )

    admin = User.query.filter_by(email='Ailaer@studio.com').first()

    if not admin:
        admin = User(
            username='admin',
            email='Ailaer@studio.com',
            role='admin'
        )
        db.session.add(admin)

    admin.username = 'admin'
    admin.email = 'Ailaer@studio.com'
    admin.password = generate_password_hash('admins19')
    admin.role = 'admin'
    db.session.commit()

    print('Database initialized successfully!')
