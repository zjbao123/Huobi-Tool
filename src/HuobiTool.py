#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Win32 UI Tool for querying Huobi accountID written in python
# @Date    : 2018-05-09
# @Author  : zjbao123
# @github  : https://github.com/zjbao123


import base64
import datetime
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import requests
import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QLineEdit, QMessageBox, QWidget, QLabel, QDialog


# timeout in 5 seconds:
TIMEOUT = 5

API_HOST = "api.huobi.pro"

SCHEME = 'https'

# language setting: 'zh-CN', 'en':
LANG = 'zh-CN'

DEFAULT_GET_HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': LANG,
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
}

DEFAULT_POST_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': LANG,
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
}

# 首次运行可通过get_accounts()获取acct_id,然后直接赋值,减少重复获取。
ACCOUNT_ID = None


# API 请求地址
MARKET_URL = TRADE_URL = "https://api.huobi.pro"

#各种请求,获取数据方式
def http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)

    try:
        response = requests.get(url, postdata, headers=headers, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            return
    except BaseException as e:
        error = Exception("httpGet failed, detail is:connect timeout!  Please open VPN!")
        raise error


def api_key_get(params, request_path, ACCESS_KEY, SECRET_KEY):
    method = 'GET'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params.update({'AccessKeyId': ACCESS_KEY,
                   'SignatureMethod': 'HmacSHA256',
                   'SignatureVersion': '2',
                   'Timestamp': timestamp})

    host_url = TRADE_URL
    host_name = urllib.parse.urlparse(host_url).hostname
    host_name = host_name.lower()


    params['Signature'] = createSign(params, method, host_name, request_path, SECRET_KEY)
    url = host_url + request_path
    return http_get_request(url, params)



def createSign(pParams, method, host_url, request_path, secret_key):
    sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
    encode_params = urllib.parse.urlencode(sorted_params)
    payload = [method, host_url, request_path, encode_params]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')
    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature

def get_accounts(ACCESS_KEY, SECRET_KEY):
    """
    :return:
    """
    path = "/v1/account/accounts"
    params = {}
    return api_key_get(params, path, ACCESS_KEY, SECRET_KEY)

class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.InitUI()

    def InitUI(self):
        self.resize(450, 200)
        self.btn = QPushButton("查询AccountID", self)
        self.btn.move(130, 80)
        self.btn.clicked.connect(self.ShowDialog)
        self.label = QLabel("ACCESS_KEY" , self)
        self.label.move(50, 20)
        self.le = QLineEdit(self)
        self.le.resize(250, 20)
        self.le.move(130, 20)
        self.label2 = QLabel("SECRET_KEY", self)
        self.label2.move(50, 50)
        self.le1 = QLineEdit(self)
        self.le1.move(130, 50)
        self.le1.resize(250, 20)
        self.label2 = QLabel("AccountID", self)
        self.label2.move(50, 110)
        self.le2 = QLineEdit(self)
        self.le2.move(130, 110)
        self.setWindowTitle("AccountID查询器")
        self.show()

    def ShowDialog(self):
        try:
            accounts = get_accounts(self.le.text(), self.le1.text())
            self.le2.setText(str(accounts['data'][0]['id']))
        except BaseException as e:
            error = '获取AccountID错误:%s' % e
            QMessageBox.warning(self, "Warning", error)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
