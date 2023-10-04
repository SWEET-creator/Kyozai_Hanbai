#! /usr/bin/env python3.6
"""
Python 3.6 or newer required.
"""
import json
import os
import stripe
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Product

# This is your test secret API key.
stripe.api_key = 'sk_test_51Nt9YtCURV3QRRGH4j7scSoMZm4JGmkGiu9yebRYFT7nUxkNeG0t6T7G0N4uFTRVel9Sw3uaOAQHvWmZl7zLXT1T00qK1Qx9fW'

from flask import Flask, render_template, jsonify, request, send_from_directory

DATABASE_URL = "sqlite:///products.db"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

app = Flask(__name__, static_folder='static',
            static_url_path='', template_folder='templates')

def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return 1400

@app.route('/')
def index():
    session = Session()
    products = session.query(Product).all()
    session.close()
    return render_template('product_list.html', products=products)

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = json.loads(request.data)
        item_id = data['items'][0]['id']

        # DBから商品情報を取得
        session = Session()
        product = session.query(Product).filter_by(id=item_id).first()
        session.close()

        if not product:
            raise Exception("Product not found")

        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(product.price * 100),  # Stripeはセンチ単位で価格を扱います
            currency='jpy',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    session = Session()
    product = session.query(Product).filter_by(id=product_id).first()
    session.close()
    if product:
        return render_template('product.html', product=product)
    else:
        return "Product not found", 404
    

@app.route('/checkout/<int:product_id>')
def checkout(product_id):
    session = Session()
    product = session.query(Product).filter_by(id=product_id).first()
    session.close()
    if product:
        return render_template('checkout.html', product=product)
    else:
        return "Product not found", 404

@app.route('/thank-you/<int:product_id>')
def thank_you(product_id):
    session = Session()
    product = session.query(Product).filter_by(id=product_id).first()
    session.close()
    if product:
        return render_template('thank-you.html', product=product)
    else:
        return "Product not found", 404

@app.route('/product/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.debug = True
    app.run(port=4242)
