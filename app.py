import sys
import requests

from flask import Flask, request, abort
from linebot.v3 import (
     WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    AudioMessageContent,
    LocationMessageContent
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
    TemplateMessage,
    ButtonsTemplate,
    URIAction
)

from mibao_flex_templates import create_shop_information, create_ramen_information
from ramen_data_process import get_image_file_by_id
from audio_func import prepare_voice_file, speech_2_text
from line_app import ramen_agent_invoke_new

import os
from dotenv import load_dotenv
load_dotenv()

def linebot_location_check (user_id, msg, event, api_client):
    keywords = ["附近", "最近"]
    # 檢查消息中是否包含任一關鍵字
    if any(keyword in msg for keyword in keywords):
        buttons_template_message = TemplateMessage(
            alt_text='位置請求',
            template=ButtonsTemplate(
                title='位置分享',
                text='咪寶咪~ 請輸入您的位置咪！!',
                actions=[
                    URIAction(
                        label='傳送位置',
                        uri='line://nv/location'
                    )
                ]
            )
        )

        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message( #reply_message_with_http_info
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[buttons_template_message]
            )
        )
        return True
    else:
        return False

app = Flask(__name__)

csv_filename = 'ramenlist.csv'  # Replace with your CSV filename
user_question_temp = {}
user_coordinate = {}

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)

print(channel_secret)
print(channel_access_token)

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    with ApiClient(configuration) as api_client:
        msg = event.message.text
        user_id = event.source.user_id

        if linebot_location_check (user_id, msg, event, api_client):
            user_question_temp[f"{user_id}"] = msg
            return

        user_question_temp[f"{user_id}"] = None
        ramen_agent_invoke_new(user_id, msg, event, api_client, user_coordinate)


@handler.add(MessageEvent, message=AudioMessageContent)
def message_audio(event):
    with ApiClient(configuration) as api_client:
        # 獲取傳送聲音
        audio_id = event.message.id
        print(audio_id)
        user_id = event.source.user_id

        print(user_id)
        
        speech_text = '音訊無字文字'

        headers = {
            'Authorization': f"Bearer {channel_access_token}",
        }
        record = requests.get(f"https://api-data.line.me/v2/bot/message/{audio_id}/content", headers=headers)

        record_file = f"./voice/{user_id}.m4a"
        speech_file = f"./voice/{user_id}.wav"
        if (record.encoding == None):
            f = open(record_file,"wb")
            f.write(record.content)
            f.close()
            prepare_voice_file(record_file)
            speech_text = speech_2_text(speech_file)
        
        print(speech_text)

        if linebot_location_check (user_id, speech_text, event, api_client):
            user_question_temp[f"{user_id}"] = speech_text
            return

        ramen_agent_invoke_new(user_id, speech_text, event, api_client, user_coordinate)


@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location(event):
    with ApiClient(configuration) as api_client:
        user_id = event.source.user_id
        user_lat = event.message.latitude
        user_lng = event.message.longitude

        if user_question_temp[f"{user_id}"] is not None:
            msg = user_question_temp[f"{user_id}"]
            user_coordinate[f"{user_id}"] = f"({user_lat},{user_lng})"
            print(user_id, user_coordinate[f"{user_id}"])
            ramen_agent_invoke_new(user_id, msg, event, api_client, user_coordinate)
            user_question_temp[f"{user_id}"] = None
        else:
            user_coordinate[f"{user_id}"] = f"({user_lat},{user_lng})"
            print(user_id, user_coordinate[f"{user_id}"])

        user_location = {'lat': user_lat, 'lng': user_lng}  # 使用者位置
        # {"user_id":user_id, "location":(user_lat,user_lng)}


if __name__ == "__main__":
    app.run(port=5000)



