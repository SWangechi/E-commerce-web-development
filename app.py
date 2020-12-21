from flask import Flask, render_template, request, redirect, session
import pymysql
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os

# import os
# import stripe
#
# stripe_keys = {
#   'secret_key': os.environ['SECRET_KEY'],
#   'publishable_key': os.environ['PUBLISHABLE_KEY']
# }
#
# stripe.api_key = stripe_keys['secret_key']


app = Flask(__name__)
app.secret_key = "dhgfhdk"  # Just a random string of characters
UPLOAD_FOLDER = "static/img"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
    # key=stripe_keys['publishable_key']


@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html')


@app.route('/products', methods=['POST', 'GET'])
def products():
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM products ORDER BY product_id ASC"
    cur.execute(sql)
    if cur.rowcount >= 1:
        return render_template('products.html', result=cur.fetchall())
    else:
        return render_template('products.html', result="No products found")


@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    id = request.args.get('id')
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM products WHERE product_id = %s"
    cur.execute(sql, id)
    if cur.rowcount >= 1:
        return render_template('checkout.html', result=cur.fetchall())
    else:
        return redirect('/checkout')


@app.route('/buy', methods=['POST', 'GET'])
def buy():
    if request.method == "POST":
        phone = str(request.form['phone'])
        amount = str(request.form['amount'])
        # GENERATING THE ACCESS TOKEN
        consumer_key = "yfDSkguKMesvIZPqsJJGzjUKtQs8nAqo"
        consumer_secret = "2HhXV3Za9HydeVFs"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        # GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }

        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)

        return response.json()
    else:
        return redirect('/checkout')


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    return render_template('contact.html')


@app.route('/home', methods=['POST', 'GET'])
def home():
    if 'username' in session:
        return render_template('home.html')
    else:
        return render_template('login.html', msg="please Login first")


@app.route('/add-products', methods=['POST', 'GET'])
def addProducts():
    if request.method == 'POST':
        title = str(request.form['title'])
        price = str(request.form['price'])
        description = str(request.form['description'])
        if title == "" or price == "" or description == "":
            return render_template("home.hml", msg="Ensure no field is empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "INSERT INTO products(title, price, description) VALUES(%s, %s, %s)"
            cur.execute(sql, (title, price, description))
            conn.commit()
            return render_template("home.html", msg="Products Added successfully")
    else:
        return redirect('/home')


@app.route('/register', methods=['POST', 'GET'])
def register():
    return render_template('register.html')


@app.route('/add-users-to-db', methods=['POST', 'GET'])
def addUsers():
    if request.method == "POST":
        # we proceed with the registration
        fname = str(request.form['fname'])
        lname = str(request.form['lname'])
        email = str(request.form['email'])
        password = str(request.form['password'])
        phone = str(request.form['phone'])
        # we check if the fields are empty
        if fname == "" or lname == "" or email == "" or password == "" or phone == "":
            return render_template("register.html", msg="Ensure none of the fields are empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            check_sql = "SELECT email FROM users WHERE email = %s"
            cur.execute(check_sql, email)
            if cur.rowcount >= 1:
                return render_template("register.html", msg="The email " + email + " is already registered")
            elif cur.rowcount == 0:
                sql = "INSERT INTO users(fname, lname, email, password, phone)values(%s,%s,%s,%s,%s)"
                cur.execute(sql, (fname, lname, email, password, phone))
                conn.commit()
                return render_template("info.html", msg="User has been added successfully")

    else:
        # we redirect user to login page
        return redirect('/register')


@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')


@app.route('/login-user', methods=['POST', 'GET'])
def loginuser():
    if request.method == 'POST':
        # We check if the form has been posted with empty fields
        email = str(request.form['email'])
        password = str(request.form['password'])
        if email == "" or password == "":
            return render_template("login.html", msg="Ensure that no field is empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "SELECT * FROM users WHERE email = %s AND password=%s"
            cur.execute(sql, (email, password))
            if cur.rowcount >= 1:
                session['username'] = email
                return redirect('/home')
            else:
                return render_template("login.html", msg="The Email/password combination is incorrect")
    else:
        return render_template("login.html", msg="Wrong Request Method")


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    return redirect('/')


def makeConnection():
    host = "127.0.0.1"
    user = "root"
    password = ""
    database = "users"  # This is the name of your database
    return pymysql.connect(host, user, password, database)


# return pymysql.connect("127.0.0.1", root, "", users)

# @app.route('/charge', methods=['POST'])
# def charge():
#     # Amount in cents
#     amount = 500
#
#     customer = stripe.Customer.create(
#         email='customer@example.com',
#         source=request.form['stripeToken']
#     )
#
#     charge = stripe.Charge.create(
#         customer=customer.id,
#         amount=amount,
#         currency='usd',
#         description='Flask Charge'
#     )
#
#     return render_template('charge.html', amount=amount)


if __name__ == "__main__":
    app.run(debug=True)
