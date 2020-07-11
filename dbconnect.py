import pymysql

def connection():

    con  = pymysql.connect(user="root", host="localhost", password="Chinmay$7552", db="pythontest")

    cursor = con.cursor()

    return cursor, con

    con.close()

def check_login(username, password):

    cursor, con = connection()
    cmd = f"select username,password from users where username='{str(username)}' and password='{str(password)}'"
    cursor.execute(cmd)
    profile = None
    for rows in cursor:
        profile = rows
    con.close()

    if profile != None:
        return 1
    else:
        return 0
