import os
from datetime import timedelta

class Config(object):
    DEBUG = False
    TESTING = False

    REDIS_URL = os.environ['REDIS_URL']

    MONGODB_SETTINGS = {    
        'host': os.environ['MONGOLAB_URI']}

    SECRET_KEY = 'super-secret'
    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = 'abcde'

    MAIL_SUPPRESS_SEND = True


    CELERY_TIMEZONE = 'UTC'
    CELERY_IMPORTS = ['api.util']
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
    BROKER_POOL_LIMIT = 0
    
class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    TESTING = True


    CELERYBEAT_SCHEDULE = {
        'requeue-every-5-seconds': {
            'task': 'requeue',
            'schedule': timedelta(seconds=5),
            'args': ()
        },
    }

class Production(Config):
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False

    REQUEUE_INTERVAL = int(os.environ['REQUEUE_INTERVAL'])

    CELERYBEAT_SCHEDULE = {
        'requeue-every-minute': {
            'task': 'requeue',
            'schedule': timedelta(seconds=REQUEUE_INTERVAL),
            'args': ()
        },
    }
