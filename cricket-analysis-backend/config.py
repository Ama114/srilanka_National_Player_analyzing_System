import os
from dotenv import load_dotenv

# 1. load.env file
load_dotenv()

class Config:
    # 2. os.getenv from .env file  'DATABASE_URL' අගය ගන්නවා
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # .env එකේ Link එක නැත්නම්, Default එකක් දාන්න (Safety එකට)
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:admin123@localhost/cricket_analysis'

    SQLALCHEMY_TRACK_MODIFICATIONS = False