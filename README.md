# FunWater

![image](https://drive.google.com/uc?export=view&id=11ugfHT5l8z6ToCZm4bMDNAoDKmeJveIY)

## Proposal
藉由 FunWater 小幫手，簡單找到飲水機資訊（暫時以台北市為例）。

## Concept
- 每週透過 [Data Taipei](https://data.taipei/#/) 取得台北市相關資訊(data.json)
- 資料整理後(infos.json)，將資料上傳至 [Algolia](https://www.algolia.com/)
- dialogflow 取得使用者意圖（CanGetWater）
- 使用 Line 內建方式取得使用者的位置
- 依照使用者所提供的位置至 Algolia 的 `geoserach` 功能，處理 nearby (經緯度、距離<1km、回傳3筆)
- 使用 Google Map Distance matrix API 計算使用者與上述回傳的點做距離計算（取得步行時間、兩者距離）

## 準備項目
- Line@ developer trial
- 建立一個 GCP 專案
- 在 GCP 上授權 Dialogflow 專案

### Dialogflow.com

定義 intents, entities, fulfillment

### cloud function

- 設定原始碼來源(Google Source Repository)
- 環境變數

```
ACCESS_TOKEN (from LINE)
SECRET (from LINE)
GOOGLE_API_KEY (from Google, 記得要同時啟用 Google Map Distance Matrix API)
DIALOGFLOW_CLIENT_ACCESS_TOKEN (from dialogflow)
ALGOLIA_APP_ID (from Algolia)
ALGOLIA_APP_KEY (from Algolia)
ALGOLIA_APP_INDEX (from Algolia)
```

## 推廣時間

![image](https://drive.google.com/uc?export=view&id=1kVuA_TMXlv3hJb8wQpJ412vDlxLHvTZY)


### references:
- [LINE BOT 時隔兩年之個人無創新 – Google 餐廳+ML on Heroku](https://site-optimize-note.tk/line-bot-%E6%99%82%E9%9A%94%E5%85%A9%E5%B9%B4%E4%B9%8B%E5%80%8B%E4%BA%BA%E7%84%A1%E5%89%B5%E6%96%B0-google-%E9%A4%90%E5%BB%B3ml-on-heroku/)
- [用Dialogflow建立LINE Chatbot](https://medium.com/@wolkesau/%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8dialogflow%E5%BB%BA%E7%AB%8Bchatbot-1-%E4%BB%8B%E7%B4%B9-62736bcdad95)
- [DIALOGFLOW](https://cloud.google.com/dialogflow/?hl=zh-TW)
