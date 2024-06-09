class Config:
    SECRET_KEY = 'B!1weNAt1T^%kvhUI*S^'

#Nombre y contraseña de la base de datos
class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'maestranzas'
    MYSQL_CURSORCLASS = 'DictCursor'

config = {
    'development': DevelopmentConfig
}