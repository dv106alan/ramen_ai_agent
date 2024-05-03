from urllib.parse import urlencode

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
    FlexCarousel,
    AudioMessage
)

from mibao_flex_templates import create_shop_information, create_ramen_information
from ai_agents import ai_agent_invoke2, ai_linebot_data_update, ai_first_filter, ai_conclude_all, ai_persional_output
from ramen_data_process import get_image_file_by_id
from app.db_access import db_get_ramen_images, db_update_user_result, db_get_user_result

import json


csv_filename = './data/ramenlist.csv'

def list_dict_to_string (data_list):
    dict_strings = [str(d) for d in data_list]
    result = '\n'.join(dict_strings)
    return result

def linebot_ramen_process (data_list):
    carousel_contents = []

    print(data_list)

    if data_list is None: return ""

    for ramen in data_list:
        name = ramen["ramen_name"]
        id = ramen["ramen_id"]
        info = ramen["info"]
        shop = ramen["shop"]

        jpg_list, price = get_image_file_by_id(csv_filename, id)

        ramen_url = f"https://raw.githubusercontent.com/dv106alan/ramen_pic/main/pic/{id}_2.jpg"

        search_query = urlencode({'query': shop})
        google_maps_search_uri = f"https://www.google.com/maps/search/?api=1&{search_query}"

        bobble = create_ramen_information(name, ramen_url, google_maps_search_uri, f"{price}", info, shop)

        carousel_contents.append(bobble)

    bubble_dict = {
                "type": "carousel",
                "contents": carousel_contents
                }
    
    flexdata = FlexContainer.from_dict(bubble_dict)
    flex_message = FlexMessage(
            altText="搜尋拉麵",
            contents=flexdata
        )
    
    return flex_message

def ai_shop_process (data_list):
    carousel_contents = []

    for shop in data_list[:]:
        name = shop["shop_name"]
        image_file = shop["image_file"]
        shop_address = shop["address"]
        shop_time = str(shop["time"])
        print(shop_time)

        shop_url = f"https://raw.githubusercontent.com/dv106alan/ramen_pic/main/shop/{image_file}"

        search_query = urlencode({'query': name})
        google_maps_search_uri = f"https://www.google.com/maps/search/?api=1&{search_query}"

        bobble = create_shop_information(name, shop_url, google_maps_search_uri, shop_address, shop_time)

        carousel_contents.append(bobble)

    bubble_dict = {
                "type": "carousel",
                "contents": carousel_contents
                }
    
    flexdata = FlexContainer.from_dict(bubble_dict)
    flex_message = FlexMessage(
            altText="搜尋店家",
            contents=flexdata
        )

    return flex_message

def ramen_agent_invoke_new (user_id, msg, event, api_client, user_coordinate):
    result_string = ""
    response = None
    message_list = []

    print(user_id)

    flex_msg = []
    ### flex message: 若要求詳細資訊，則回傳搜尋結果
    if msg in ["#詳細資訊"]:
        json_string = db_get_user_result(user_id, "result_linebot")
        if json_string:
            data_dict = json.loads(json_string[0])
            data = data_dict['ramen']
            if data is not None:
                ramen_flex = FlexMessage.from_dict(data_dict['ramen'][0])
                flex_msg.append(ramen_flex)
            data = data_dict['shop']
            if data is not None:
                shop_flex = FlexMessage.from_dict(data_dict['shop'][0])
                flex_msg.append(shop_flex)
            data = data_dict['map_list']
            print(data)
            if data is not None:
                map_flex = FlexMessage.from_dict(data_dict['map_list'][0])
                flex_msg.append(map_flex)
            
            if flex_msg is None: return

            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=flex_msg
                )
            )
            return
    elif msg in ["#網頁資訊"]:
        web_url_message = TextMessage(text="http://127.0.0.1")
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[web_url_message]
            )
        )

    # command type, no process
    if "#" in msg[:1]: return

    # 1. Filter message
    is_ramen = ai_first_filter(msg)
     
    repeat_time = 3

    if ("yes" not in is_ramen['相關']):
        result_string = "輸入資料中，無拉麵相關資料。"
    else:
        for _ in range(repeat_time):
            # 2. llm process
            response = ai_agent_invoke2(msg, is_ramen, user_id, user_coordinate)
            print(response)
            if response is not None:
                break
        result_string = "無拉麵相關資料。"

    # 3. process llm response data
    if response:
        is_res_valid = response['query']
        ramen_list = response['ramen']
        shop_list = response['shop']
        know_list = response['know']
        map_list = response['map_list']
        is_map = response['isSendMap']

        line_data = {"ramen":None, "shop":None, "know_msg":None, "map_list":None}
        web_data = {"ramen":ramen_list, "shop":shop_list, "know_msg":know_list, "map_list":map_list}
        
        know_str = ""
        ramen_str = ""
        shop_str = ""
        map_str = ""
        
        if know_list:
            know_text = know_list[0]['簡單']
            print(know_list)
            know_msg = TextMessage(text=know_text)
            message_list.append(know_msg)
            to_dict = know_msg.to_dict()
            line_data["know_msg"] = [to_dict]
            _str = list_dict_to_string(know_list)
            know_str = f"拉麵知識：{_str}\n"

        if ramen_list:
            flex_message = linebot_ramen_process(ramen_list)
            message_list.append(flex_message)
            to_dict = flex_message.to_dict()
            line_data["ramen"] = [to_dict]

            _str = list_dict_to_string(ramen_list)
            ramen_str = f"拉麵資訊：{_str}\n"
        
        if shop_list:
            flex_message = ai_shop_process(shop_list)
            message_list.append(flex_message)
            to_dict = flex_message.to_dict()
            line_data["shop"] = [to_dict]
            # print(line_data["shop"])
            # line_data["shop"] = f""" "{flex_message.to_json()}" """
            _str = list_dict_to_string(shop_list)
            shop_str = f"店家資訊：{_str}\n"
        
        if is_map:
            map_msg = response['map_message']
            print("map_message:")
            map_dict = dict(map_msg)
            print(map_dict)
            message_list.append(map_msg)
            flex_message = FlexMessage.from_dict(map_msg)
            to_dict = flex_message.to_dict()
            line_data["map_list"] = [to_dict]


        # ai_web_data_update(user_id, web_data)
        _dumps = json.dumps(line_data)
        ai_linebot_data_update(user_id, _dumps)

        all_message = None
        print(response)
        if is_res_valid:
            all_message = know_str + ramen_str + shop_str + map_str
        else:
            all_message = "無拉麵相關資料。"
        print("all message:")
        print(all_message)
        result_string = ai_conclude_all(all_message)

    print("result_string:")
    print(result_string)
    reply_message = ai_persional_output(result_string)
    print("reply_message:")
    print(reply_message)

    text_msg = TextMessage(text=reply_message)

    line_bot_api = MessagingApi(api_client)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[text_msg]
        )
    )


# Function test
if __name__ == "__main__":
    # result = ramen_agent_invoke_new("123456","替玉是什麼意思？", None, None)
    result = ramen_agent_invoke_new("123456","我想找附近的拉麵店", None, None)
    print(result)
