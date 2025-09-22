from os import getenv

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv('.env.celery')
except:
    pass