from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pymysql

# Import Models (මේ නම් models.py එකේ තියෙන්න ඕනේ)
from models import db, ODIPerformance, T20Performance, TestPerformance, BestXIPlayer
import data_loader

# Import Blueprints
from routes.home import home_bp
from routes.batting import batting_bp
from routes.bowling import bowling_bp
from routes.dataset import dataset_bp
from routes.best_xi import best_xi_bp

pymysql.install_as_MySQLdb()
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(batting_bp)
app.register_blueprint(bowling_bp)
app.register_blueprint(dataset_bp)
app.register_blueprint(best_xi_bp)

# Tables Create කිරීම
with app.app_context():
    try:
        db.create_all()
        print("✓ Database tables created/verified successfully")
    except Exception as e:
        print(f"✗ Database Error: {e}")

if __name__ == '__main__':
    print("🏏 Cricket Analysis System Running...")
    app.run(debug=True, port=5000)