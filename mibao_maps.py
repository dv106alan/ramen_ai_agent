from urllib.parse import urlencode

import os
from dotenv import load_dotenv
load_dotenv()

google_maps_api_key = os.environ['GOOGLE_MAP_API_KEY']

#創造靜態地圖網址(標籤)
def generate_map_image_url(markers, google_maps_api_key):
    base_url = "https://maps.googleapis.com/maps/api/staticmap?"
    params = {
        "size": "600x400",
        "maptype": "roadmap",
        "key": google_maps_api_key
    }

    #製作標籤
    markers_params = '&'.join(
        f"markers=color:red%7Clabel:{index + 1}%7C{marker['lat']},{marker['lng']}"
        for index, marker in enumerate(markers)
    )
    
    # 創造網址格式
    encoded_params = urlencode(params)
    url = f"{base_url}{encoded_params}&{markers_params}"
    return url

#創造訊息 含搜尋(需要店名)
def create_flex_message_contents(shops_info):
    hero_image_url = generate_map_image_url(
        markers=[{'lat': shop['lat'], 'lng': shop['lng']} for shop in shops_info],
        google_maps_api_key=google_maps_api_key
    )
    
    body_contents = []
    for index, shop in enumerate(shops_info):
        shop_name = shop['name']
        url_name = shop['url_name']
        search_query = urlencode({'query': url_name})
        google_maps_search_url = f"https://www.google.com/maps/search/?api=1&{search_query}"

        body_contents.append({
            "type": "text",
            "text": f"{index + 1}. {shop_name}",
            "wrap": True,
            "color": "#0000FF",
            "action": {
                "type": "uri",
                "uri": google_maps_search_url
            },
            "margin": "md"
        })

    flex_content = {
        "type": "bubble",
        "size": "mega",
        "hero": {
            "type": "image",
            "url": hero_image_url,
            "size": "full",
            "aspectRatio": "16:9",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "label": "View on Google Maps",
                "uri": hero_image_url
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": body_contents
        },
    }
    
    return flex_content

