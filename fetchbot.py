import json
import requests

results = requests.get("https://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=59629791-5f4f-4c91-903b-e9ab9aa0653b").json()
with open('data.json', 'w') as outfile:
    json.dump(results, outfile, ensure_ascii=False)