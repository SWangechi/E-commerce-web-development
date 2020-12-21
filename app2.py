# from flask import Flask, render_template
# import requests
# import datetime
# import base64
# from requests.auth import HTTPBasicAuth
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def home():
#     return "<h1>This is home</h1><a href='/mpesa_payment'>STK PUSH</a>"
#
#
# @app.route('/mpesa_payment')
# def mpesa_payment():
#     # GENERATING THE ACCESS TOKEN
#     consumer_key = "TLEbdlzeI1YMFikSnU9YyAxpqzqG4BJG"
#     consumer_secret = "wFYDiA6LSRyOa6Zv"
#
#     api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
#     r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
#
#     data = r.json()
#     access_token = "Bearer" + ' ' + data['access_token']
#
#     # GETTING THE PASSWORD
#     timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
#     passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
#     business_short_code = "174379"
#     data = business_short_code + passkey + timestamp
#     encoded = base64.b64encode(data.encode())
#     password = encoded.decode('utf-8')
#
#     # BODY OR PAYLOAD
#     payload = {
#         "BusinessShortCode": "174379",
#         "Password": "{}".format(password),
#         "Timestamp": "{}".format(timestamp),
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": "1",
#         "PartyA": "254708118890",
#         "PartyB": "174379",
#         "PhoneNumber": "254708118890",
#         "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
#         "AccountReference": "account",
#         "TransactionDesc": "account"
#     }
#
#     # POPULAING THE HTTP HEADER
#     headers = {
#         "Authorization": access_token,
#         "Content-Type": "application/json"
#     }
#
#     url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL
#
#     response = requests.post(url, json=payload, headers=headers)
#
#     return render_template("access_token.html")
#
#
# if __name__ == '__main__':
#     app.run()
