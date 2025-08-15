import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'filesystem')
    SESSION_PERMANENT = os.environ.get('SESSION_PERMANENT', 'false').lower() == 'true'
    SESSION_FILE_DIR = os.environ.get('SESSION_FILE_DIR', None)
    SESSION_USE_SIGNER = True
