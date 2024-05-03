from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from ramen_data_process import get_shop_data, get_shop_data_by_name, ramen_result_to_detail, shop_result_to_detail
from mibao_maps import create_flex_message_contents
from app.db_access import db_update_user_result, db_get_ramen_list, db_get_shop_list
from ramen_llm_sql import llm_sql_ask

import json

from linebot.v3.messaging import (
    FlexMessage,
    FlexContainer,
)

import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ['GOOGLE_API_KEY']
print(api_key)

### Load vector database ###
HugEmbeddings = HuggingFaceInstructEmbeddings(model_name="aspire/acge_text_embedding")
knowvect_file_path = "./chroma_know3_db"
vectorstore_know = Chroma(persist_directory=knowvect_file_path, embedding_function=HugEmbeddings)

retriever_know = vectorstore_know.as_retriever(score_threshold = 0.8)

# ramen data conclusion
def ai_ramen_invoke (json_string, features):
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.5)

    prompt_template = """
    Given the following context and a question, generate an answer based on this context only. List all racords.
    Provide the following format as dict string (do not make things up):
    ramen_name:
    ramen_id:
    info(50字以內):
    shop:

    give me all the list of data

    請用中文回答
    CONTEXT: {context}

    QUESTION: {question}

    ***reply array json string***
    """
    # Please answer in the following format(dictionary type):
    #     answer context:,action:,adjustment number:

    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain = (
        prompt
        | llm
        | StrOutputParser() 
    )

    result = chain.invoke({"context":json_string, "question":features})
    print(result)
    json_data = result.strip().strip('```').strip().strip('json').strip()
    print(result)

    try:
        dict_data = json.loads(json_data)
    except Exception as e:
        return []
    
    return dict_data

# Get knowledge by using RAG, and make conclusion using LLM
def ai_know_invoke (qust):
    template = """Answer the question based only on the following context:

    {context}

    Question: {question}

    return the following format:
    簡單:
    詳細:

    conditions:
    簡單(200字以內)
    詳細(700字以內)

    reply json string
    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.5)

    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    chain = (
        {"context": retriever_know | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("ai_know_invoke:")
    qust_str = ""
    if type(qust) == list:
        qust_str = ' '.join(qust)
    elif type(qust) == str:
        qust_str = qust
    json_data = chain.invoke(qust_str)
    print(json_data)
    json_data = json_data.strip().strip('```').strip().strip('json').strip()
    data_dict = json.loads(json_data)

    return data_dict

def ai_sentence_classify (sentent):
    system = """You are a query extract expert, by enter the sentences, then return the queries.
    Please follow the following type, and categorising it (拉麵特色:,拉麵配料:, ...):
    拉麵特色:
    拉麵配料:
    用餐心得:
    店家:
    是否查詢位置:
    地區:
    範圍:
    是否找拉麵店:
    拉麵知識:

    reply json type, and the value type is string

    sentences：{sentences}

    """

    prompt = ChatPromptTemplate.from_template(system)

    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.0, convert_system_message_to_human=True)

    # query_analyzer = prompt | llm | StrOutputParser()

    chain = (
        prompt
        | llm
        | StrOutputParser() 
    )

    json_data = chain.invoke(sentent)
    # print(f"{json_data}")
    json_data = json_data.strip().strip('```').strip().strip('json').strip()
    data_dict = json.loads(json_data)

    return json_data, data_dict

def ai_get_ramenMapInfo (id_list): # {ramen_name:shop_name}
    # load shop data
    ramen_data = db_get_ramen_list(id_list)

    shop_list = {}

    for data in ramen_data:
        shop_list[f"{data['ramen_name']}"] = f"{data['shop_name']}"

    shop_data = get_shop_data_by_name(shop_list.values())

    shops_info = []

    for ramen_name, shop_name in shop_list.items():
        name = ramen_name
        url_name = shop_name
        _data = shop_data[f"{shop_name}"]
        lat, lng = _data["coordinate"].split(', ')
        data = {"name": f"{name}", "lat": float(lat), "lng": lng, "url_name": url_name}
        shops_info.append(data)
        
    return shops_info

def ai_get_shopMapInfo (shop_list):
    # load shop data
    shop_data = get_shop_data(shop_list)

    shops_info = []

    for shop in shop_data:
        name = shop["shop_name"]
        url_name = name
        lat, lng = shop["coordinate"].split(', ')
        data = {"name": f"{name}", "lat": float(lat), "lng": lng, "url_name": url_name}
        shops_info.append(data)
        
    return shops_info

def ai_agent_invoke2 (msg, conditions, user_id, user_coordinate):
    search_string = ai_seperate_search(msg)
    is_sql = False
    is_know = False
    is_map = False

    ramen_result_list = None
    shop_result_list = None
    know_result_list = None

    ''' data format.
    {
        "相關": "yes",
        "拉麵": "yes",
        "店家": "yes",
        "地點": "yes",
        "知識": "no"
    }
    '''

    if ("yes" in conditions["拉麵"] or "yes" in conditions["店家"]):
        if search_string['拉麵及店家查詢']:
            is_sql = True

    if ("yes" in conditions["知識"]):
        if search_string['拉麵知識查詢']:
            is_know = True

    if ("yes" in conditions["地點"]):
        is_map = True

    print(search_string)
    
    ''' data format.
    {"拉麵及店家查詢": "我想找大安區鹽味拉麵還有他的拉麵店",\n  "拉麵知識查詢": "我想找拉麵風格有哪些"}
    '''
    ramen_ask = ""
    sql_result = []
    if is_sql:
        ramen_ask = search_string['拉麵及店家查詢']
        sql_result = llm_sql_ask(ramen_ask, user_id, user_coordinate)
        print(sql_result)
        
    if is_know:
        ask_msg = search_string['拉麵知識查詢']
        know_result = ai_know_invoke(ask_msg)

    print(sql_result)
    if (sql_result is None or ("SQLQuery:" in sql_result)):
        return None

    ramen_id_list = []
    if "yes" in conditions["拉麵"] and len(sql_result) > 0 and is_sql:
        if type(sql_result) == dict:
            print("sql_result is dict")
            if sql_result["ramen"][0].get('ramen_id') is not None:
                ramen_id_list = [data["ramen_id"] for data in sql_result["ramen"]]
                data_list = db_get_ramen_list(ramen_id_list)
                json_data = json.dumps(data_list, ensure_ascii=False)
                print("ai_ramen_invoke:")

                keywords = ["附近", "最近"]
                if any(keyword in ramen_ask for keyword in keywords):
                    ramen_result_list = ai_ramen_invoke(json_data, "特色")
                else:
                    ramen_result_list = ai_ramen_invoke(json_data, f"特色搜尋：{ramen_ask}")
                print("end:")
        elif type(sql_result) == list:
            print("sql_result is list")
            if sql_result[0].get('ramen_id') is not None:
                ramen_id_list = [data["ramen_id"] for data in sql_result if data["ramen_id"] is not None]
                data_list = db_get_ramen_list(ramen_id_list)
                json_data = json.dumps(data_list, ensure_ascii=False)
                print("ai_ramen_invoke:")
                keywords = ["附近", "最近"]
                if any(keyword in ramen_ask for keyword in keywords):
                    ramen_result_list = ai_ramen_invoke(json_data, "特色")
                else:
                    ramen_result_list = ai_ramen_invoke(json_data, f"特色搜尋：{ramen_ask}")
                print("end:")
    shop_id_list = []
    if "yes" in conditions["店家"] and len(sql_result) > 0 and is_sql:
        if type(sql_result) == dict:
            if sql_result['shop'][0].get('shop_id') is not None:
                shop_id_list = [str(data["shop_id"]) for data in sql_result['shop']]
                data_list = db_get_shop_list(shop_id_list)
                for data in data_list:
                    coor_str = data["coordinate"]
                    coor_val = tuple(map(float, coor_str.split(',')))
                    data["coordinate"] = coor_val
                shop_result_list = data_list
        elif type(sql_result) == list:
            if sql_result[0].get('shop_id') is not None:
                shop_id_list = [str(data["shop_id"]) for data in sql_result]
                data_list = db_get_shop_list(shop_id_list)
                for data in data_list:
                    coor_str = data["coordinate"]
                    coor_val = tuple(map(float, coor_str.split(',')))
                    data["coordinate"] = coor_val
                shop_result_list = data_list

    if "yes" in conditions["知識"]:
        know_result_list = [know_result]

    map_message = None
    map_info_list = None
    if "yes" in conditions["地點"]:
        if "yes" in conditions["拉麵"] and "no" in conditions["店家"]:
            map_list = ramen_id_list
            map_message, map_info_list = ai_map_process("ramen", map_list)
        elif "yes" in conditions["店家"]:
            map_list = shop_id_list
            map_message, map_info_list = ai_map_process("shop", map_list)
    
    result_data = {"query":True,"ramen":ramen_result_list, "shop":shop_result_list, "know":know_result_list, "isSendMap":is_map, "map_message":map_message, "map_list": map_info_list}

    if ramen_result_list or shop_result_list or know_result_list:
        return result_data
    else:
        return None

def ai_map_process (type, id_list):
    if type == "ramen":
        ramen_info = ai_get_ramenMapInfo(id_list)
        flex_content = create_flex_message_contents(ramen_info)

        flexdata = FlexContainer.from_dict(flex_content)

        flex_message = FlexMessage(
            altText="店家地圖",
            contents=flexdata
        )

        return flex_message.to_dict(), ramen_info
    
    elif type == "shop":
        shop_info = ai_get_shopMapInfo(id_list)
        flex_content = create_flex_message_contents(shop_info)

        flexdata = FlexContainer.from_dict(flex_content)

        flex_message = FlexMessage(
            altText="店家地圖",
            contents=flexdata
        )

        return flex_message, shop_info

# 第一層語意篩選
def ai_first_filter (msg):
    system = """You are a condition check ai, check if data related to the following conditions.
    conditions:
    查詢拉麵
    以心情查詢拉麵
    查詢店家
    查詢拉麵地點
    查詢拉麵知識

    please reply yes,no
    reply message: 相關:(yes,no),拉麵:(yes,no),店家:(yes,no),地點:(yes,no),知識:(yes,no)
    output json type

    data：{data}

    """

    prompt = ChatPromptTemplate.from_template(system)

    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.0, convert_system_message_to_human=True)

    chain = (
        prompt
        | llm
        | StrOutputParser() 
    )

    reply = chain.invoke(msg)
    reply = reply.replace("```json", "").strip().replace("```","").strip()
    print(reply)
    dict_data = json.loads(reply)
    
    return dict_data

# 區分語意
def ai_seperate_search (msg):
    system = """seperate the centances of data, base on the following condition.
    拉麵及店家查詢(描述搜尋拉麵或店家資訊): answser,拉麵知識查詢(描述搜尋拉麵知識及規則): answser

    output json type

    data：{data}

    """

    prompt = ChatPromptTemplate.from_template(system)

    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.0, convert_system_message_to_human=True)

    chain = (
        prompt
        | llm
        | StrOutputParser() 
    )

    reply = chain.invoke(msg)
    reply = reply.replace("```json", "").strip().replace("```","").strip()
    print(reply)
    dict_data = json.loads(reply)

    return dict_data

# LLM整理所有處理資訊
def ai_conclude_all (content):
    system = """According to input data, fill up the following topic. Only list the topic that contains data. Don't show id.
    Topics:
    拉麵資訊(列舉所有拉麵資訊):
    店家資訊(列舉所有店家資訊):
    拉麵知識(列舉所有拉麵知識):
    位置資訊(簡單介紹地理資訊):

    data：{data}

    """

    prompt = ChatPromptTemplate.from_template(system)

    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.0, convert_system_message_to_human=True)

    chain = (
        prompt
        | llm
        | StrOutputParser() 
    )

    reply = chain.invoke({"data":content})

    return reply

# 個性化輸出
def ai_persional_output (msg):
    system = """
    妳的名字是咪寶，是一位拉麵專家。妳的個性活潑開朗，聰明伶俐，說話輕快活潑平易近人，就像一位親近的好朋友。妳的口頭禪是"咪!"，習慣在說話開始或結尾等加上口頭禪。對於拉麵有極大的熱情，樂於回答問題及幫助人解決問題。
    妳的回答平易近人
    妳的工作是收到一段文字。用自己的話重新整理後回答。
    使用繁體中文。
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "用咪寶的話，重新說明以下文字，以回覆使用者:{user_input}"),
        ]
    )

    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.7, convert_system_message_to_human=True)

    chain = (
        prompt
        | llm
        | StrOutputParser() 
    )

    reply = chain.invoke({"user_input":msg})

    return reply



### data process ###

def ai_web_data_update (user_id, data_dict):
    ramen_list = data_dict['ramen']
    shop_list = data_dict['shop']
    know_list = data_dict['know_msg']
    map_list = data_dict['map_list']

    web_dict = {"id":user_id, "ramen":None, "shop":None, "know_msg":None, "map_list":None}

    if ramen_list:
        detail = ramen_result_to_detail(ramen_list)
        web_dict["ramen"] = detail

    if shop_list:
        detail = shop_result_to_detail(shop_list)
        web_dict["shop"] = detail

    if know_list:
        web_dict["know_msg"] = know_list

    if map_list:
        web_dict["map_list"] = map_list
    
    _dict = json.dumps(web_dict)
    db_update_user_result(user_id, "result_detail", _dict)
    pass

def ai_linebot_data_update (user_id, data_dict):
    db_update_user_result(user_id, "result_linebot", data_dict)


