from pymongo import MongoClient

def get_db_connection(uri, db_name):
    client = MongoClient(uri
                         , tlsAllowInvalidCertificates=True) #Issue with cetificate validation on Ashu
    return client[db_name]