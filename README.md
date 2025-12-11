# Accept a payment

_Learn how to securely accept payments online._

## ⚠️ DISCLAIMER

**This is an unofficial, community-created tool and is NOT affiliated with, endorsed by, or supported by Stripe, Inc. Use at your own risk. For official Stripe documentation and samples, visit [stripe.com/docs](https://stripe.com/docs) and [github.com/stripe-samples](https://github.com/stripe-samples).**

---

This repository demonstrates card payment acceptance using Stripe's Card Element with automatic invoice creation and tracking.

## Features

- **Card Element Integration**: Accept card payments using Stripe's Card Element
- **Automatic Invoice Creation**: Creates a Stripe Invoice for each payment
- **Invoice Tracking**: Automatically marks invoices as paid when payment succeeds via webhooks
- **EUR Currency Support**: Configured for Euro payments by default
- **Price Reuse**: Efficiently reuses existing Stripe Price objects
- **Docker Support**: Easy deployment with Docker Compose

## Payment Method Support

This implementation supports **card payments only** using Stripe's Card Element:
- ✅ Visa
- ✅ Mastercard
- ✅ American Express
- ✅ Discover
- ✅ And all other card types supported by Stripe


## Installation

### Prerequisites

- Docker and Docker Compose
- Stripe account with API keys ([Get your keys](https://dashboard.stripe.com/apikeys))

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd invoices-with-card-element
   ```

2. **Configure environment variables**

   Copy the example env file and add your Stripe keys:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your keys:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...  # Optional for local testing
   ```

3. **Start the application**
   ```bash
   docker-compose up
   ```

4. **Access the application**

   Open your browser to `http://localhost:4343`

### Local Development (without Docker)

See the [server README](./server/README.md) for instructions on running the Flask server locally.

### Testing Webhooks Locally

To test webhook events locally, use the Stripe CLI:
```bash
stripe listen --forward-to localhost:4343/webhook
# Copy the webhook signing secret (whsec_...) to STRIPE_WEBHOOK_SECRET in .env
```

For more details, see [CLAUDE.md](./CLAUDE.md)

---

## How It Works

1. **Payment Initiation**: User enters card details on the payment form
2. **Invoice Creation**: Server creates:
   - Stripe Product (or reuses existing)
   - Stripe Price with EUR currency (or reuses existing)
   - Stripe Customer
   - Stripe Invoice with line items
   - Payment Intent linked to the invoice
3. **Payment Confirmation**: Client confirms payment using Stripe.js
4. **Webhook Processing**: When payment succeeds, webhook marks the invoice as paid
5. **Confirmation**: User sees payment success with invoice number

## Architecture

- **Backend**: Python Flask server (port 4242 internal, 4343 external)
- **Frontend**: Vanilla HTML/JavaScript with Stripe.js
- **Payment Flow**: Card Element → Invoice → Payment Intent → Webhook
- **Currency**: EUR (configurable in `client/card.js`)

## Documentation

- [CLAUDE.md](./CLAUDE.md) - Comprehensive development guide
- [server/README.md](./server/README.md) - Server setup instructions
- [TESTING.md](./TESTING.md) - Testing documentation

## Support

For official Stripe support and documentation:
- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Discord](https://stripe.com/go/developer-chat)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/stripe-payments)


## Testing

See [TESTING.md](./TESTING.md).

## License

See [LICENSE](./LICENSE).
