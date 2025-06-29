import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'


class DevelopmentConfig(Config):
    """Configuración de desarrollo."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    

class ProductionConfig(Config):
    """Configuración de producción."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # RATELIMIT_STORAGE_URI = "redis://localhost:6379"

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}