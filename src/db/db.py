import os
import pymongo


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DB(metaclass=Singleton):
    def __init__(self):
        DB_UNAME = os.getenv('DB_UNAME')
        DB_PWD = os.getenv('DB_PWD')
        DB_URL = os.getenv('DB_URL')
        connection_string = f"mongodb+srv://{DB_UNAME}:{DB_PWD}@{DB_URL}/test?retryWrites=true&w=majority" 
        self.client = pymongo.MongoClient(connection_string, tls=True, tlsAllowInvalidCertificates=True)
        print(self.client.server_info())

    def get_client(self):
        return self.client
