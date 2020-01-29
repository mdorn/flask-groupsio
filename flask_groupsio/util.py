import requests

from bs4 import BeautifulSoup
from flask import request


def groupsio_api_query(url):
    req = requests.get(url, cookies=request.cookies)
    data = req.json()
    return data


def get_external_html(url, elems):
    req = requests.get(url, timeout=2)
    soup = BeautifulSoup(req.text, 'html.parser')
    html = ''
    for elem in elems:
        html = html + str(soup(elem).pop())
    return html


