
def create_shop_information(shop_name, shop_url, shop_uri, shop_address, shop_time):
    shop_information = {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": shop_url,
                    "size": "full",
                    "aspectRatio": "15:13",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "uri": shop_uri
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": shop_name,
                            "weight": "bold",
                            "size": "xl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "lg",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "地址",
                                            "color": "#aaaaaa",
                                            "size": "md",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": shop_address,
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "md",
                                            "flex": 5
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "時間",
                                            "color": "#aaaaaa",
                                            "size": "md",
                                            "flex": 1
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "flex": 5,
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": shop_time,
                                                    "wrap": True,
                                                    "color": "#666666",
                                                    "size": "md"
                                                }
                                                # {
                                                #     "type": "text",
                                                #     "text": shop_time,
                                                #     "wrap": True,
                                                #     "color": "#666666",
                                                #     "size": "md"
                                                # }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    return shop_information['contents'][0]

def create_ramen_information(ramen_name, ramen_url, ramen_uri, ramen_price, ramen_feature, shop_name):
    ramen_information = {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": ramen_url,
                    "size": "full",
                    "aspectRatio": "15:13",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "uri": ramen_uri
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": ramen_name,
                            "wrap": True,
                            "weight": "bold",
                            "size": "xl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "lg",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "價格",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "flex": 5,
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": ramen_price,
                                                    "wrap": True,
                                                    "color": "#666666",
                                                    "size": "sm"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "特色",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "flex": 5,
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": ramen_feature,
                                                    "wrap": True,
                                                    "color": "#666666",
                                                    "size": "sm"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "店家",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "flex": 5,
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": shop_name,
                                                    "wrap": True,
                                                    "color": "#666666",
                                                    "size": "sm"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    return ramen_information['contents'][0]

