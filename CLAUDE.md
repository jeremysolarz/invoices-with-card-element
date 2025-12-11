# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Stripe card payment integration demo using the **Card Element** with **Invoice tracking**. It's a Flask (Python) backend serving a static HTML/JS client that accepts card payments using Stripe's Card Element and automatically creates and marks invoices as paid.

The project consists of a Python Flask server that creates card PaymentIntents with associated Stripe Invoices, and a single-page client application with the Stripe Card Element. When a payment succeeds, the webhook automatically marks the invoice as paid following Stripe's "Accept partial payments for invoices" pattern.

## Architecture

### Server (Flask/Python)
- **Location**: `server/server.py`
- **Port**: 4242 (internal), 4343 (external via Docker)
- **Key endpoints**:
  - `GET /` - Serves index.html with card payment form
  - `GET /config` - Returns Stripe publishable key to client
  - `POST /create-payment-intent` - Creates PaymentIntent for card payments with associated invoice (amount: $59.99)
    - Creates/retrieves a Stripe Product
    - Creates a Price for the product
    - Creates a Customer
    - Creates an Invoice with the price
    - Finalizes the invoice
    - Creates a PaymentIntent linked to the invoice via metadata
    - Returns: clientSecret, invoiceId, invoiceNumber, customerId
  - `POST /webhook` - Handles Stripe webhook events
    - On `payment_intent.succeeded`: Marks the associated invoice as paid using `stripe.Invoice.pay()`
    - On `payment_intent.payment_failed`: Logs failure
  - `GET /success` - Success page after payment completion
- **Static file serving**: Serves client files from `client/` directory (configured via `STATIC_DIR` env var)

### Client (HTML/JS)
- **Location**: `client/` directory
- **Files**:
  - `index.html` - Main page with card payment form (entry point)
  - `card.html` - Alternative card payment page (same as index)
  - `card.js` - Handles Stripe Card Element and payment submission
  - `utils.js` - Helper functions for displaying messages
  - `success.html` / `success.js` - Payment success page
  - `css/base.css` - Styling
  - Note: All other payment method files have been removed
- **Payment flow**:
  1. Fetch Stripe publishable key from `/config` (card.js:4)
  2. Initialize Stripe.js and create Card Element (card.js:12-18)
  3. Mount Card Element to `#card-element` div
  4. On form submit, call `/create-payment-intent` with currency='usd' (card.js:33-45)
  5. Confirm card payment with `stripe.confirmCardPayment()` using returned client_secret (card.js:63-73)
  6. Display payment status

### Docker Setup
- **Dockerfile**: Multi-stage build copying server and client code
- **docker-compose.yml**: Single service setup exposing port 4242
- Environment variables loaded from `.env` file

## Development Commands

### Local Development (without Docker)

1. **Set up Python environment**:
```bash
cd server
python3 -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate.bat
pip install -r requirements.txt
```

2. **Configure environment**: Copy `.env.example` to `.env` and add your Stripe keys:
```bash
cp .env.example .env
# Edit .env with your STRIPE_PUBLISHABLE_KEY and STRIPE_SECRET_KEY
```

3. **Run the Flask server**:
```bash
cd server
export FLASK_APP=server.py  # On Windows: $env:FLASK_APP="server.py"
python3 -m flask run --port=4242
```

4. **Access the application**: Navigate to `http://localhost:4242`

### Docker Development

```bash
# Build and start
docker-compose up

# Rebuild after code changes
docker-compose up --build

# Stop
docker-compose down
```

### Testing Webhooks Locally

Use Stripe CLI to forward webhooks to your local server:
```bash
stripe listen --forward-to localhost:4242/webhook
# Copy the webhook signing secret (whsec_...) to STRIPE_WEBHOOK_SECRET in .env
```

## Testing

This repository uses two testing frameworks:
- **RSpec/Capybara** for Ruby-based E2E and server API tests
- **Playwright** for browser automation and snapshot testing

See `TESTING.md` for comprehensive testing documentation including:
- Docker Compose setup with test runner services
- Running Playwright snapshot tests
- Running Capybara E2E tests
- Running server API tests with RSpec
- Updating visual regression snapshots

## Environment Variables

Required variables in `.env`:
- `STRIPE_PUBLISHABLE_KEY` - Stripe test mode publishable key (pk_test_...)
- `STRIPE_SECRET_KEY` - Stripe test mode secret key (sk_test_...)
- `STRIPE_WEBHOOK_SECRET` - Webhook signing secret (whsec_...) from Stripe CLI
- `STATIC_DIR` - Path to client files (default: `../../client/html` or `../client` for Docker)
- `DOMAIN` - Application domain for redirects (default: `http://localhost:4242`)

Optional variables:
- `PAYMENT_METHOD_TYPES` - Comma-separated list of payment methods (default: "card")
- `PRICE` - Stripe Price ID for prebuilt checkout (if using that flow)

## Code Patterns

### Invoice and Payment Intent Creation Flow

The payment flow creates both an invoice and payment intent (server.py:32-103):

1. **Product Setup** (lines 39-47): Retrieves existing product or creates new one named "Card Payment Service"
2. **Price Creation** (lines 49-71): Searches for existing price with matching currency and amount, reuses if found, otherwise creates new one (€59.99)
3. **Customer Creation** (lines 56-60): Creates a new Stripe Customer for each payment
4. **Invoice Creation** (lines 62-70): Creates an invoice with `auto_advance=False` and `collection_method='charge_automatically'`
5. **Invoice Item** (lines 72-77): Adds the price to the invoice as a line item
6. **Invoice Finalization** (line 80): Finalizes the invoice, making it ready for payment
7. **Payment Intent** (lines 82-91): Creates PaymentIntent with invoice_id in metadata

This follows Stripe's "Accept partial payments for invoices" pattern by creating the invoice first, then using a PaymentIntent to collect payment.

### Card Payment Confirmation

Card payments are confirmed in card.js:63-76 using `stripe.confirmCardPayment()`:
- Takes the `clientSecret` from PaymentIntent
- Includes card element and billing details (cardholder name)
- Returns payment status or error
- Displays invoice number and customer ID on success

### Webhook Handling - Attaching Payments to Invoices

Webhooks are verified using `STRIPE_WEBHOOK_SECRET` and signature validation (server.py:109-178). The webhook handler:
- Verifies webhook signatures if secret is configured
- On `payment_intent.succeeded` (lines 149-171):
  - Retrieves invoice_id from payment intent metadata
  - Attaches the PaymentIntent to the invoice using `stripe.Invoice.attach_payment()`
  - This creates an InvoicePayment record that properly links the payment to the invoice
  - Logs invoice number, payment intent ID, invoice status, and amount paid
- On `payment_intent.payment_failed`: Logs failure

## Stripe API Version

The server uses Stripe API version `2023-10-16` (set in server.py:18). Be aware of API version differences when consulting Stripe documentation.

## Common Tasks

### Testing Card Payments
Visit `http://localhost:4343` and use test cards:
- `4242424242424242` - Visa (succeeds)
- `5555555555554444` - Mastercard (succeeds)
- `4000002500003155` - Requires 3D Secure authentication

Use any future expiration date, any 3-digit CVC, and any postal code.

**Note**: The application is configured to use EUR currency by default (card.js:41).

### Debugging Payment Issues
1. Check Flask console for server errors
2. Check browser console for client-side errors (card.js)
3. Use Stripe Dashboard logs to see API calls
4. Verify webhook events are being received (if using Stripe CLI)
5. Check the `#messages` div for payment status messages

### Changing the Payment Amount
Edit `orderAmount = 5999` in server.py:36 (amount in cents). For example, change to `2000` for €20.00.

### Changing the Currency
Edit the currency in card.js:41. For example, change from `'eur'` to `'usd'`. The server will automatically find or create a matching price for the new currency.

### Customizing the Card Element
The Card Element is created in card.js:17. You can pass options to customize appearance:
```javascript
const card = elements.create('card', {
  style: {
    base: { fontSize: '16px', color: '#32325d' }
  }
});
```

### Viewing Invoices in Stripe Dashboard
After a successful payment:
1. Go to Stripe Dashboard → Billing → Invoices
2. Find the invoice by the invoice number shown in the payment confirmation
3. Verify the invoice status shows as "Paid"
4. Check the payment is linked to the PaymentIntent

### Testing the Invoice Flow
1. Visit `http://localhost:4343`
2. Enter test card: `4242424242424242`
3. Complete the payment
4. Watch the browser messages show:
   - Invoice number (e.g., "Invoice created: ABC-1234")
   - Payment success with PaymentIntent ID
   - Note that invoice will be marked as paid via webhook
5. Check server logs (or Stripe CLI webhook logs) for:
   - "💰 Payment received!"
   - "✅ Invoice [NUMBER] payment attached!"
   - Invoice status and amount paid
6. Verify in Stripe Dashboard:
   - Invoice shows as Paid
   - Payment is properly linked to the invoice (expand the "payments" field)
