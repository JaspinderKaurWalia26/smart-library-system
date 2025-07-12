import oracledb

def get_connection():
    return oracledb.connect(user="SYSTEM", password="jasoracle55$W", dsn="localhost:1521/XEPDB1")


