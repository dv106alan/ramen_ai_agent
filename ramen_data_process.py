import csv
import re

from app.db_access import db_get_ramen_images, db_get_user_result

def get_image_file_by_id(csv_filename, date_id):
    image_file = None
    price = None
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['date_id'] == date_id:
                image_file = row['image_file']
                price = row['price']
                break
    img = []
    if image_file is not None:
        img = image_file.split(";")

    return img, price

def string_to_dict_shop(input_string):
    # Remove the leading \ufeff character if present
    input_string = input_string.lstrip('\ufeff')
    
    # Split the string by newline character and remove the leading and trailing whitespace
    lines = input_string.strip().split('\n')
    
    # Initialize an empty dictionary to store key-value pairs
    result_dict = {}
    
    # Iterate through each line in the input string
    for line in lines:
        # Split each line by ':' and strip any whitespace
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # Convert coordinate value to tuple if applicable
        if key == 'coordinate':
            value = tuple(map(float, value.split(',')))
        # Convert id value to integer
        elif key == 'id':
            value = int(value)
        
        # Add key-value pair to the dictionary
        result_dict[key] = value
    
    return result_dict

def get_ramen_data (id_list):
    csv_filename = './data/ramenlist.csv'
    ramen_list = []
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['date_id'] in id_list:
                ramen_list.append(row)
    return ramen_list

def get_shop_data (id_list):
    csv_filename = './data/shoplist.csv'
    shop_list = []
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['id'] in id_list:
                shop_list.append(row)
    return shop_list

def get_shop_data_by_name (name_list):
    csv_filename = './data/shoplist.csv'
    shop_list = {}
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['shop_name'] in name_list:
                shop_list[row['shop_name']] = row
    return shop_list

def search_shop_by_ramen(ramen_list):

    pass

def clear_bom_from_file(file_path):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    
    # Remove the BOM character (\ufeff)
    content_without_bom = content.replace('\ufeff', '')
    
    # Write the content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content_without_bom)


def preprocess_json_string(json_string):
    # Remove invalid control characters
    cleaned_string = ''.join(char for char in json_string if ord(char) > 31 or char in ['\n', '\r', '\t'])
    return cleaned_string

def dic_chain_result (data):
    # Split data into individual ramen entries and remove empty lines
    ramen_entries = [entry for entry in data.split('\n\n') if entry.strip()]

    # Parse each ramen entry and append it to the list
    parsed_ramen_list = []
    for entry in ramen_entries:
        entry_dict = {}
        lines = entry.split('\n')
        for line in lines:
            key, value = line.split(': ', 1)
            entry_dict[key] = value
        parsed_ramen_list.append(entry_dict)

    return parsed_ramen_list


def ramen_result_to_detail(data_list):
    """
    [{'ramen_name': '本店鹽味拉麵 (限定)', 'id': '2022-07-06_10-00-42_UTC', 'info': '加入虱目魚、黑羽雞熬製的湯頭，鮮甜爽口，搭配虱目魚肚、赤嘴等配料，豐富有層次。'}, 
    {'ramen_name': '鹽味豚骨拉麵', 'id': '2020-05-03_09-58-22_UTC', 'info': '以大火炒過湯頭和配料的鹽味豚骨拉麵，湯頭醇厚清爽，麵條偏硬有嚼勁，配料有叉燒、溏心蛋等。'}, 
    {'ramen_name': '煮干塩味雞湯溏心蛋拉麵 (隱藏版)', 'id': '2022-01-22_10-03-26_UTC', 'info': '以鹽味雞湯搭配煮干風味油的隱藏版拉麵，湯頭鮮香但風味較不明顯，麵條和湯頭有些分離。'}]
    """
    # add pic_ruls
    detail_list = []

    for data in data_list:
        id = data['id']
        img_list = db_get_ramen_images(id).split(";")
        url = "https://raw.githubusercontent.com/dv106alan/ramen_pic/main/pic/"
        url_list = [f"{url}{img}" for img in img_list if img is not None]
        data["img_url"] = url_list
        detail_list.append(data)
    
    return detail_list

def shop_result_to_detail(data_list):
    """
    [{'shop_name': '旨燕', 'location': '台北郵局附近', 'seats': '約20個', 'address': '台北市中正區開封街一段90號一樓', 'coordinate': (25.046048077512754, 121.51045696948748), 'time': '11:30–13:30\r17:00–20:40', 'id': 34, 'image_file': '027_ziyan.JPG'}, 
    {'shop_name': '鳳華拉麵 二號店', 'location': '科技大樓', 'seats': '約16個', 'address': '台北市大安區復興南路二段190號1樓', 'coordinate': (25.028682719808454, 121.54356663930132), 'time': '11:30–14:00\r17:00–21:00', 'id': 88, 'image_file': '068_fanghua.JPG'}, 
    {'shop_name': '你回來啦Okaeri', 'location': '延吉街', 'seats': '約14個', 'address': '台北市大安區延吉街60號', 'coordinate': (25.04390928087362, 121.5537357388058), 'time': '11:30–14:30\r17:30–21:00\r週一、二公休', 'id': 38, 'image_file': '031_okaeri.JPG'}, 
    {'shop_name': '吉天元 公館店', 'location': '台灣大學', 'seats': '18個', 'address': '台北市大安區新生南路三段104號', 'coordinate': (25.016992701244, 121.53291336948688), 'time': '12:00–14:30\r17:30–21:00', 'id': 32, 'image_file': '025_jitanyuan.JPG'}]
    """
    # add pic_ruls
    detail_list = []

    for data in data_list:
        img = data['image_file']
        img_url = f"https://raw.githubusercontent.com/dv106alan/ramen_pic/main/shop/{img}"
        data["img_url"] = img_url
        detail_list.append(data)

    return detail_list

def know_result_to_detail(data_list):
    pass


def get_flexmesssage (user_id, column):

    if not column in ["ramen", "shop", "know_msg", "map_list"]:
        return None

    data = db_get_user_result("U6d6cd695a00a626321ec386321b2e129", "result_linebot")

    # Given string
    given_string = data[0]

    # Define the pattern to search for FlexMessage(...)
    pattern = fr"'{column}': FlexMessage\(.*?\)]\)\)"

    # Use re.findall() to find all occurrences of the pattern in the string
    flex_messages = re.findall(pattern, given_string)
    flex_string = flex_messages[0].replace(f"'{column}':","").strip()
    
    return flex_string

