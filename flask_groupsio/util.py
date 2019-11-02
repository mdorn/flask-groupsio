import requests
from flask import request

def groupsio_api_query(url):
    req = requests.get(url, cookies=request.cookies)
    data = req.json()
    print(data)
    return data

