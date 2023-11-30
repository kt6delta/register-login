class Config(object):
    SECRET_KEY = 'tzkburpreriwpbzn12345'
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "datapreciado08@gmail.com"
    MAIL_PASSWORD = "tzkburpreriwpbzn"

class DevConfig(Config):
     DEBUG = True