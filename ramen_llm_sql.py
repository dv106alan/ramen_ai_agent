from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI

import json

import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ['GOOGLE_API_KEY']

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.1, convert_system_message_to_human=False)

db_user = "root"
db_password = "123456"
db_host = "localhost"
db_name = "ramibodb"

llm_db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=5)

def llm_sql_renew ():
    llm_db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=5)

def llm_sql_ask (question, user_id, user_coordinate):

    db_chain = SQLDatabaseChain.from_llm(llm, llm_db, verbose=True)

    keywords = ["附近", "最近"]
    if any(keyword in question for keyword in keywords) and user_id in user_coordinate:
        # 查詢座標
        user_coor = user_coordinate[f"{user_id}"]
        qns = db_chain(f"""{question} (座標{user_coor})(random)(max 4 record)(**add ramen_id or shop_id column**)(search from name or content)(output json string array)(******without '''sql******)

        use the following method
        Question:
            我想找附近500m的拉麵
        SQL Command Answer:
            SELECT 
                ramen_name,
                ramen_id,
                shop_data.shop_name, 
                `shop_id`
            FROM 
                `shop_data` 
                JOIN `ramen_data` ON `shop_data`.`shop_name` = `ramen_data`.`shop_name`
            WHERE 
                6371 * 2 * ASIN(
                    SQRT(
                        POW(SIN(RADIANS(25.082164552257417 - ST_X(`coordinate`)) / 2), 2) +
                        COS(RADIANS(25.082164552257417)) * COS(RADIANS(ST_X(`coordinate`))) * 
                        POW(SIN(RADIANS(121.57068137079477 - ST_Y(`coordinate`)) / 2), 2)
                    )
                ) <= 0.5
        """)
    else:
        # 一般查詢
        qns = db_chain(f"{question} (random)(max 4 record)(add ramen_id or shop_id column)(search from name or content)(output json string array)(******without '''sql******)")

    print(qns)

    if "SQLQuery" in qns['result']:
        return None
    
    data = json.loads(qns['result'])

    return data

# function test
if __name__ == "__main__":
    llm_sql_ask("我想找附近500m的豚骨拉麵", "123456")