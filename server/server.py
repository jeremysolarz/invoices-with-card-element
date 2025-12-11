#! /usr/bin/env python3.8
import stripe
import json
import os

from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# For sample support and debugging, not required for production:
stripe.set_app_info(
    'stripe-samples/accept-a-payment/card-element',
    version='0.0.3',
    url='https://github.com/stripe-samples')

stripe.api_version = '2023-10-16'
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

static_dir = str(os.path.abspath(os.path.join(__file__ , "..", os.getenv("STATIC_DIR"))))
app = Flask(__name__, static_folder=static_dir, static_url_path="", template_folder=static_dir)

@app.route('/', methods=['GET'])
def get_root():
    return render_template('index.html')


@app.route('/config', methods=['GET'])
def get_config():
    return jsonify({'publishableKey': os.getenv('STRIPE_PUBLISHABLE_KEY')})

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    data = json.loads(request.data)
    currency = data.get('currency', 'usd')
    customer_name = data.get('name', 'Hans Müller')  # Use provided name or default
    orderAmount = 5999  # Amount in cents ($59.99)

    try:
        # Step 1: Create or get a product
        products = stripe.Product.list(limit=1)
        if len(products.data) > 0:
            product = products.data[0]
        else:
            product = stripe.Product.create(
                name='Card Payment Service',
                description='Payment for card element demo'
            )

        # Step 2: Get or create a price for the product with specific currency and amount
        # Search for existing price with matching criteria
        existing_prices = stripe.Price.list(
            product=product.id,
            active=True,
            currency=currency,
            limit=100
        )

        # Find a price that matches our amount
        price = None
        for p in existing_prices.data:
            if p.unit_amount == orderAmount and p.currency == currency:
                price = p
                break

        # If no matching price found, create a new one
        if not price:
            price = stripe.Price.create(
                product=product.id,
                unit_amount=orderAmount,
                currency=currency,
            )

        # Step 3: Create a customer with Swiss address
        customer = stripe.Customer.create(
            name=customer_name,
            description='Card payment customer',
            address={
                'line1': 'Bahnhofstrasse 42',
                'city': 'Zürich',
                'postal_code': '8001',
                'country': 'CH'
            },
            metadata={'source': 'card_element_demo'}
        )

        # Step 4: Create an invoice
        invoice = stripe.Invoice.create(
            customer=customer.id,
            auto_advance=False,  # Don't auto-finalize
            collection_method='charge_automatically',
            metadata={
                'payment_flow': 'card_element'
            }
        )

        # Step 5: Add invoice item
        stripe.InvoiceItem.create(
            customer=customer.id,
            price=price.id,
            invoice=invoice.id,
        )

        # Step 6: Finalize the invoice
        invoice = stripe.Invoice.finalize_invoice(invoice.id)

        # Step 7: Create a PaymentIntent with invoice metadata
        intent = stripe.PaymentIntent.create(
            payment_method_types=['card'],
            amount=orderAmount,
            currency=currency,
            customer=customer.id,
            metadata={
                'invoice_id': invoice.id
            }
        )

        # Send PaymentIntent details to the front end
        return jsonify({
            'clientSecret': intent.client_secret,
            'invoiceId': invoice.id,
            'invoiceNumber': invoice.number,
            'customerId': customer.id
        })
    except stripe.error.StripeError as e:
        return jsonify({'error': {'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 400

@app.route('/success', methods=['GET'])
def get_success():    
    return render_template('success.html')

@app.route('/webhook', methods=['POST'])
def webhook_received():
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'payment_intent.succeeded':
        print('💰 Payment received!')
        payment_intent_id = data_object['id']

        # Get invoice_id from metadata
        invoice_id = data_object.get('metadata', {}).get('invoice_id')

        if invoice_id:
            try:
                # Attach the PaymentIntent to the invoice
                # This creates an InvoicePayment and properly links the payment
                invoice = stripe.Invoice.attach_payment(
                    invoice_id,
                    payment_intent=payment_intent_id
                )

                print(f'✅ Invoice {invoice.number} (ID: {invoice_id}) payment attached!')
                print(f'   Payment Intent: {payment_intent_id}')
                print(f'   Invoice Status: {invoice.status}')
                print(f'   Amount Paid: €{invoice.amount_paid / 100:.2f}')

            except stripe.error.StripeError as e:
                print(f'❌ Error attaching payment to invoice: {str(e)}')

        # Fulfill any orders, e-mail receipts, etc
        # To cancel the payment you will need to issue a Refund (https://stripe.com/docs/api/refunds)
    elif event_type == 'payment_intent.payment_failed':
        print('❌ Payment failed.')
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4242, debug=True)
