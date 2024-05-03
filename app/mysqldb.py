import pymysql
import pandas as pd

class SQLDB:
    def __init__ (self, host, port, user, password, db_name):
        self.host = host
        self.user = user
        self.db_name = db_name
        self.port = port
        self.db = pymysql.connect(host=self.host,
                                user=self.user,
                                password=password,  #"ntC1234#31#",
                                database=self.db_name, 
                                port=self.port)
    
    def sql_commit (self):
        self.db.commit()
    
    def sql_read_table (self, table_name, select):
        try:
            query = f"SELECT * FROM {table_name} {select} LIMIT 100"
            df = pd.read_sql(query, self.db)

            return df

        
        except Exception as e:
            print(e)

    def sql_read_table_column (self, table_name, columns, select):
        try:
            query = f"SELECT {columns} FROM {table_name} {select} LIMIT 100"
            df = pd.read_sql(query, self.db)
            return df

        except Exception as e:
            print(e)

    def sql_update_table (self, table_name, colums, row_data):
        try:
            db = self.db

            cursor = db.cursor()
            
            # 插入資料 (column)
            sql = f"INSERT INTO {table_name}({colums}) VALUES {row_data}"
            cursor.execute(sql)

            db.commit()

            print(cursor.rowcount, "OK !")

            for x in cursor:
                print(x)
        except Exception as e:
            print(e)

    

