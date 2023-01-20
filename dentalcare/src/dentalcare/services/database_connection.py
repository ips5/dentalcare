import mysql.connector

db_password = 'Password1!'

sql_query_template = {}

sql_query_template['get_dcr_role'] = f"SELECT Role FROM DCRUsers WHERE Email = %(email)s"


def db_connect():
    cnx = mysql.connector.connect(user="dentalcare",
                                  password=db_password,
                                  host="dentalcare.mysql.database.azure.com",
                                  port=3306,
                                  database="dentalcaredatabase",
                                  ssl_ca="DigiCertGlobalRootCA.crt (1).pem")

    print(f'[i] cnx is connected: {cnx.is_connected()}')
    return cnx


def execute_query(sql_query_name, data_dict):
    try:
        res = None
        cnx = db_connect()
        cursor = cnx.cursor(buffered=True)
        cursor.execute(sql_query_template[sql_query_name], data_dict)
        if sql_query_template[sql_query_name].startswith("SELECT"):
            res = cursor
        if sql_query_template[sql_query_name].startswith("INSERT"):
            cnx.commit()
        cursor.close()
        cnx.close()
        return res
    except Exception as ex:
        print(f'[x] error! {ex}')
        return None


def execute_instance(query):
    try:
        print(query)
        db = db_connect()
        cursor = db.cursor(buffered=True)
        query_insert = f"INSERT INTO DCRInstances(graphid, simid) VALUES ('{query[0]}', '{query[1]}');"
        cursor.execute(query_insert)
        db.commit()
    except Exception as ex:
        print(f'[x] error! {ex}')
        return None


def delete_instance(simid):
    try:
        db = db_connect()
        cursor = db.cursor(buffered=True)
        query_delete = f"DELETE FROM DCRInstances WHERE simid='{simid}';"
        cursor.execute(query_delete)
        db.commit()
        cursor.close()
        load_instances()
    except Exception as ex:
        print(f'[x] error! {ex}')
        return None


def load_instances():
    try:
        db = db_connect()
        cursor = db.cursor(buffered=True)
        query_load = f"SELECT * FROM DCRInstances"
        cursor.execute(query_load)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as ex:
        print(f'[x] error! {ex}')
        return None