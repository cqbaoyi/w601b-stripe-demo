# Stripe API Proof of Concept

A minimal Flask application for testing Stripe payment integration with one-time payments and subscriptions.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PRICE_ONE_TIME=price_...
PRICE_SUB_MONTHLY=price_...
DOMAIN=http://localhost:5000
```

## Running

```bash
python src/app.py
```

The server will start on `http://localhost:5000`.

## API Endpoints

### Create One-Time Payment Checkout
- **POST** `/api/checkout/one-time`
- Body (optional): `{"quantity": 1, "price_id": "price_..."}`
- Returns: `{"url": "https://checkout.stripe.com/..."}`

### Create Subscription Checkout
- **POST** `/api/checkout/subscribe`
- Body (optional): `{"price_id": "price_...", "trial_days": 0}`
- Returns: `{"url": "https://checkout.stripe.com/..."}`

### Webhook Handler
- **POST** `/webhook`
- Handles Stripe webhook events (checkout.session.completed, subscription updates, invoice payments, etc.)

### Pages
- **GET** `/success` - Payment success page
- **GET** `/cancel` - Checkout cancellation page

## Testing

This is configured for local webhook testing. Use Stripe CLI to forward webhooks:
```bash
stripe listen --forward-to localhost:5000/webhook
```
