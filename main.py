import os
import re
import requests
from algoliasearch.search_client import SearchClient

ALGOLIA_APP_ID = os.environ.get('ALGOLIA_APP_ID')
ALGOLIA_APP_KEY = os.environ.get('ALGOLIA_APP_KEY')
ALGOLIA_APP_INDEX = os.environ.get('ALGOLIA_APP_INDEX')

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_APP_KEY)
index = client.init_index(ALGOLIA_APP_INDEX)

def main(request):
    results = requests.get("https://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=59629791-5f4f-4c91-903b-e9ab9aa0653b").json()

    infos=[]
    for point in results['result']['results']:
        info={}
        # 略過資料為空項目
        if not point['緯度'].strip():
            continue
        if int(float(point['緯度'])) > 100:
            # 修正資料經緯度相反項目
            print("fixed: " + str(point['_id']))
            lat = point['緯度']
            lng = point['經度']
            point['緯度'] = lng
            point['經度'] = lat
        # 重新整理資料
        info['objectID'] = int(point['_id'])
        info['city'] = point['市別']
        info['administrative_area'] = point['行政區']
        info['place'] = point['設置地點']
        info['updated_time'] = point['最近採樣日期時間']
        info['management_unit'] = point['管理單位']
        info['link'] = 'http://gismobile.water.gov.taipei/W/S.aspx?SD=' + point['直飲臺編號']
        info['uid'] = point['直飲臺編號']
        info['status_updated_time'] = point['狀態異動日期時間']
        info['place_category'] = point['場所次分類']
        info['escherichia_coli'] = point['大腸桿菌數']
        info['place_type'] = point['場所別']
        info['opening_hours'] = point['場所開放時間']
        info['place_divide'] = point['轄區分處']
        info['address'] = point['地址']
        info['contact'] = transform_tel_style(point['連絡電話'])
        info['place_name'] = point['場所名稱']
        info['status'] = point['狀態']
        info['_geoloc'] = {
            'lat': float(point['緯度']),
            'lng': float(point['經度'])
        }
        infos.append(info)
    index.save_objects(infos)

# 重置電話格式
def transform_tel_style(line):
    rule = re.compile(u"^02")
    line = rule.sub('',line)
    rule = re.compile(u"\(02\)")
    line = rule.sub('',line)
    rule = re.compile(u"ext")
    line = rule.sub('#',line)
    rule = re.compile(u"p")
    line = rule.sub('#',line)
    rule = re.compile(u"轉")
    line = rule.sub('#',line)
    rule = re.compile(u"\*")
    line = rule.sub('#',line)
    rule = re.compile(r"\-")
    line = rule.sub('',line)
    rule = re.compile(r"\s")
    line = rule.sub('',line)
    rule = re.compile(r'[\u4e00-\u9fa5]')
    line = rule.sub('',line)
    line = '+8862' + line
    rule = re.compile(r'^\+886203')
    line = rule.sub('+8863',line)
    rule = re.compile(r'^\+886209')
    line = rule.sub('+8869',line)
    rule = re.compile(r'#[0-9]*')
    line = rule.sub('',line)
    return line