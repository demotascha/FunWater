import os
import apiai
import json
import requests
import random
import googlemaps

from algoliasearch.search_client import SearchClient

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageSendMessage,
    LocationMessage,
    CarouselTemplate, CarouselColumn, URIAction,
    TemplateSendMessage, ButtonsTemplate, URITemplateAction,
)

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
SECRET = os.environ.get('SECRET')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
DIALOGFLOW_CLIENT_ACCESS_TOKEN = os.environ.get('DIALOGFLOW_CLIENT_ACCESS_TOKEN')

ALGOLIA_APP_ID = os.environ.get('ALGOLIA_APP_ID')
ALGOLIA_APP_KEY = os.environ.get('ALGOLIA_APP_KEY')
ALGOLIA_APP_INDEX = os.environ.get('ALGOLIA_APP_INDEX')

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_APP_KEY)
index = client.init_index(ALGOLIA_APP_INDEX)

ai = apiai.ApiAI(DIALOGFLOW_CLIENT_ACCESS_TOKEN)
line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

gmaps = googlemaps.Client(GOOGLE_API_KEY)

def callback(request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + str(body))

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ================= 客製區 Start =================
def is_alphabet(uchar):
    if ('\u0041' <= uchar<='\u005a') or ('\u0061' <= uchar<='\u007a'):
        print('English')
        return "en"
    elif '\u4e00' <= uchar<='\u9fff':
        #print('Chinese')
        print('Chinese')
        return "zh-tw"
    else:
        return "en"
# ================= 客製區 End =================

# ================= 機器人區塊 Start =================
@handler.add(MessageEvent, message=TextMessage)  # default
def handle_text_message(event):                  # default
    msg = event.message.text # message from user
    uid = event.source.user_id # user id
    # 1. 傳送使用者輸入到 dialogflow 上
    ai_request = ai.text_request()
    #ai_request.lang = "en"
    ai_request.lang = is_alphabet(msg)
    ai_request.session_id = uid
    ai_request.query = msg

    # 2. 獲得使用者的意圖
    ai_response = json.loads(ai_request.getresponse().read())
    user_intent = ai_response['result']['metadata']['intentName']

    # 3. 根據使用者的意圖做相對應的回答
    if user_intent == "CanGetWater":
        # 建立一個 button 的 template
        buttons_template_message = TemplateSendMessage(
            alt_text="告訴我你現在的位置",
            template=ButtonsTemplate(
                text="告訴我你現在的位置",
                actions=[
                    URITemplateAction(
                        label="Send my location",
                        uri="line://nv/location"
                    )
                ]
            )
        )
        line_bot_api.reply_message(
            event.reply_token,
            buttons_template_message)

    else: # 聽不懂時的回答
        msg = "Sorry，I don't understand"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # 1. 獲取使用者的經緯度
    lat = event.message.latitude
    lng = event.message.longitude
    print(str(event))

    # 2. 使用 Algolia 取得離目前最近的 3 個飲水機 =========
    origins = (lat, lng)
    hits = index.search('', {
        'aroundLatLng': origins,
        'aroundRadius': 1000, # 1km
        'hitsPerPage': 3
    })
    if (int(len(hits['hits']) < 1)):
        msg = "抱歉，目前沒有支援此範圍"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
        exit()

    columnObjs=[]
    for location in hits['hits']:
        # 使用 Google distance_matrix 取得距離
        destination = (location['_geoloc']["lat"], location['_geoloc']["lng"])
        location['distance_matrix'] = gmaps.distance_matrix(origins, destination, mode='walking')
        location_distance = location['distance_matrix']["rows"][0]["elements"][0]["distance"]["text"]
        location_duration = location['distance_matrix']["rows"][0]["elements"][0]["duration"]["text"]

        distance = "沒有資料" if location_distance is None else location_distance
        duration = "沒有資料" if location_duration is None else location_duration
        checkLink = "無" if location.get("link") is None else location["link"]
        openHours = "無" if location.get("opening_hours") is None else location["opening_hours"]
        # address = "沒有資料" if location.get("address") is None else location["address"]
        contact = "沒有資料" if location.get("contact") is None else location["contact"]
        details = "營業時間：{}\n距離：{}\n步行時間：{}".format(openHours, distance, duration)

        # 6. 取得 Google map 網址
        map_url = "https://www.google.com/maps/search/?api=1&query={lat},{lng}".format(
            lat=location['_geoloc']["lat"],
            lng=location['_geoloc']["lng"],
        )
        # 建立 CarouselColumn obj
        column = CarouselColumn(
            thumbnail_image_url='https://drive.google.com/uc?export=view&id=1cPNUZiIZ0J-zsIfvYQpS2ELUSzVHQM0U',
            title=location['place_name'] + ' ' + location["place"],
            text=details,
            actions=[
                URIAction(
                    label='查看 Google 地圖',
                    uri=map_url
                ),
                URIAction(
                    label='水質資料', 
                    uri=checkLink
                ),
                URIAction(
                    label='CALL電話', 
                    uri=str('tel:' + contact)
                )
            ]
        )
        # 加入 list
        columnObjs.append(column)

    # 回覆使用 Carousel Template
    carousel_template_message = TemplateSendMessage(
        alt_text='選出最近的三個飲水機資訊給你',
        template=CarouselTemplate(
            columns=columnObjs
        )
    )

    try:
        line_bot_api.reply_message(
            event.reply_token,
            carousel_template_message)
    except:
        print(str(columnObjs))