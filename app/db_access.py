from app.mysqldb import SQLDB

sqldb = SQLDB(host="localhost", port=3306, 
              user="root", password="123456", 
              db_name="ramibodb")

def db_get_ramen_list(id_list):
    try:
        list_str = ', '.join('"' + item + '"' for item in id_list)

        ramen_data = sqldb.sql_read_table_column("ramen_data", "ramen_name,price,content,shop_name,ramen_id",f"""WHERE ramen_id in ({list_str})""")

        # ramen_data = sqldb.sql_read_table("ramen_data", f"""WHERE ramen_id in ({list_str})""")

        if ramen_data is not None:
            dict_by_records = ramen_data.to_dict(orient='records')
            print(dict_by_records)

            return dict_by_records
        else:
            return None

    except Exception as e:
        print(e)
        return ""

def db_get_shop_list(id_list):
    try:
        list_str = ', '.join('"' + item + '"' for item in id_list)

        pd_data = sqldb.sql_read_table("shop_data", f"""WHERE shop_id in ({list_str})""")

        if pd_data is not None:
            dict_by_records = pd_data.to_dict(orient='records')
            print(dict_by_records)

            return dict_by_records
        else:
            return None

    except Exception as e:
        print(e)
        return ""

def db_get_ramen_images(id):
    try:
        ramen_data = sqldb.sql_read_table("ramen_data", f"""WHERE date_id = '{id}'""")

        content = ramen_data['image_file']

        data_as_string = str(content.iloc[0])

        return data_as_string
    except Exception as e:
        print(e)
        return ""

def db_get_user_result(user_id, column):

    if column not in ["result_detail", "result_linebot", "position", "ramen_linebot"]:
        return None

    conn = sqldb.db
    
    try:
        # Check if the id exists in the table
        query = f"SELECT {column} FROM user_query WHERE id = %s"
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id))
            result = cursor.fetchone()
        
        if result:
            return result
        else:
            return None

    except Exception as e:
        print("Error:", e)

    pass

def db_update_user_result(id_value, column ,result_detail_data):
    # Connect to MariaDB

    if column not in ["result_detail", "result_linebot", "position", "ramen_linebot"]:
        return None

    conn = sqldb.db

    try:
        # Check if the id exists in the table
        query = "SELECT id FROM user_query WHERE id = %s"
        with conn.cursor() as cursor:
            cursor.execute(query, (id_value))
            result = cursor.fetchone()

        # If id exists, update result_detail; otherwise, insert new row
        if result:
            # Update result_detail for the specific id
            query = f"""UPDATE user_query SET {column} = %s WHERE id = %s"""
            with conn.cursor() as cursor:
                cursor.execute(query, (result_detail_data, id_value))
            conn.commit()
            print("Data updated successfully!")
        else:
            # Insert a new row
            query = f"""INSERT INTO user_query (id, {column}) VALUES (%s, %s)"""
            with conn.cursor() as cursor:
                cursor.execute(query, (id_value, result_detail_data))
            conn.commit()
            print("New row inserted successfully!")

    except Exception as e:
        print("Error:", e)

def db_clear_user_result(id_value, column ,result_detail_data):
    # Connect to MariaDB

    if column not in ["result_detail", "result_linebot", "position", "ramen_linebot"]:
        return None

    conn = sqldb.db

    try:
        # Check if the id exists in the table
        query = "SELECT id FROM user_query WHERE id = %s"
        with conn.cursor() as cursor:
            cursor.execute(query, (id_value))
            result = cursor.fetchone()

        # If id exists, update result_detail; otherwise, insert new row
        if result:
            # Update result_detail for the specific id
            query = f"UPDATE user_query SET {column} = %s WHERE id = %s"
            with conn.cursor() as cursor:
                cursor.execute(query, (result_detail_data, id_value))
            conn.commit()
            print("Data updated successfully!")
        else:
            # Insert a new row
            query = f"INSERT INTO user_query (id, {column}) VALUES (%s, %s)"
            with conn.cursor() as cursor:
                cursor.execute(query, (id_value, result_detail_data))
            conn.commit()
            print("New row inserted successfully!")

    except Exception as e:
        print("Error:", e)

