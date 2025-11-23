import os, uuid
from flask import Flask, request, jsonify, abort, redirect
from dotenv import load_dotenv
import stripe

load_dotenv()
app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ONE_TIME = os.getenv("PRICE_ONE_TIME")
PRICE_SUB_MONTHLY = os.getenv("PRICE_SUB_MONTHLY")
DOMAIN = os.getenv("DOMAIN", "http://localhost:5000")


# Webhook：confirm the event and update your own database
@app.post("/webhook")
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig, secret=WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        abort(400)

    et = event["type"]
    data = event["data"]["object"]
    print(f'event type: {et}, event object: {data}')
    
    def checkout_session_completed():
        pass
    def subscription_updated(subscription: stripe.Subscription):
        pass
    def subscription_deleted(subscription: stripe.Subscription):
        pass
    def invoice_payment_succeeded(invoice: stripe.Invoice):
        pass
    def invoice_payment_failed(invoice: stripe.Invoice):
        pass

    # checkout completed, whether one-time or subscription
    if et == "checkout.session.completed":
        checkout_session_completed()
    # subscription updated
    elif event.type == 'customer.subscription.updated':
        subscription_updated(event.data.object)
    # subscription deleted
    elif event.type == 'customer.subscription.deleted':
        subscription_deleted(event.data.object)
    # payment succeeded
    elif event.type == 'invoice.payment_succeeded':
        invoice_payment_succeeded(event.data.object)
    # payment failed
    elif event.type == 'invoice.payment_failed':
        invoice_payment_failed(event.data.object)
        
    return "", 200


# one-time purchase: create Checkout Session, mode=payment
@app.post("/api/checkout/one-time")
def create_one_time_checkout():
    # user_id = get_current_user_id()
    # customer_id = ensure_customer(user_id)

    # the client can also include quantity, coupon, etc.
    data = request.get_json(silent=True) or {}
    quantity = int(data.get("quantity", 1))
    price_id = data.get("price_id", PRICE_ONE_TIME)

    session = stripe.checkout.Session.create(
        customer_email="xyz@gmail.com",
        mode="payment",
        line_items=[{"price": price_id, "quantity": quantity}],
        success_url=f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}/cancel",
    )
    return jsonify({"url": session.url})
    

# subscription: create Checkout Session, mode=subscription
@app.post("/api/checkout/subscribe")
def create_sub_checkout():
    # user_id = get_current_user_id()
    # customer_id = ensure_customer(user_id)

    data = request.get_json(silent=True) or {}
    price_id = data.get("price_id", PRICE_SUB_MONTHLY)
    trial_days = int(data.get("trial_days", 0))

    session = stripe.checkout.Session.create(
        customer_email="xyz@gmail.com",
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}/cancel",
        subscription_data={"trial_period_days": trial_days} if trial_days > 0 else {},
    )
    return jsonify({"url": session.url})
    
    
# success and cancel pages
@app.get("/success")
def success():
    return "Payment or subscription succeeded."


@app.get("/cancel")
def cancel():
    return "Checkout canceled."
    
    
if __name__ == "__main__":
    app.run(port=5000)