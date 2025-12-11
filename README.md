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

## Running samples with Dev Containers or Codespaces

We provide [Dev Container](https://containers.dev/) configurations for most of the sample apps for web. For the Visual Studio Code example, by hitting `Reopen in Containers` in the Command Pallete and choosing a sample from the options prompted, dedicated Docker containers for the sample will be automatically created.

You can also try these samples even without installing Docker on your machine by using [GitHub Codespaces](https://github.com/features/codespaces). A sample app codespace can be created by clicking "New with options..." below and choosing a sample app from the Dev container configuration select box. **Note that in this case, you would be charged for usage of GitHub Codespaces.**

![](https://github.com/stripe-samples/accept-a-payment/assets/43346/9db4688c-a71d-4624-80f1-4b79c5cae44d)

### Running server app samples

After launching the environment, a couple of setup steps would be needed to launch the web app. For the NodeJS (`custom-payment-flow-server-node`) example:

1. Export the required environment variables
    1. `export STRIPE_PUBLISHABLE_KEY=XXXX`
    2. `export STRIPE_SECRET_KEY=XXXX`
    3. `export PRICE=XXXX`
2. Install the dependencies and run the web server. For NodeJS example, `npm install && npm run start`

You can also run some tests for the server app by the following steps. This example is a little hacky as we need to use SSH to run a test command in another container (`runner`).

1. Run `ssh-keygen` and `chmod 600 ~/.ssh/*`
2. Login to the test runner service with `ssh runner`
3. Move to the working dir with `cd /work`
4. Export the required environment variables
    1. `export $(cat .devcontainer/.env | xargs)`
    2. `export STRIPE_PUBLISHABLE_KEY=XXXX`
    3. `export STRIPE_SECRET_KEY=XXXX`
    4. `export PRICE=XXXX`
5. Run tests like `bundle exec rspec spec/custom_payment_flow_server_spec.rb `

### Running client app samples

After launching the environment, a couple of setup steps would be needed to launch the app. For the Create React App (`custom-payment-flow-client-react-cra`) example:

1. Export the required environment variables
    1. `export STRIPE_PUBLISHABLE_KEY=XXXX`
    2. `export STRIPE_SECRET_KEY=XXXX`
    3. `export PRICE=XXXX`
2. Install the dependencies and run the node web server by running `cd ../../server/node && npm install && npm run start`
3. In another terminal, install the dependencies and run the client app by running `npm install && npm start`
  * :memo: You might want to set `server.hmr.port` to `443` in `vite.config.js` ([related issue](https://github.com/vitejs/vite/issues/4259))

## Authors

- [@cjav_dev](https://twitter.com/cjav_dev)
- [@thorwebdev](https://twitter.com/thorwebdev)
- [@aliriaz](https://github.com/aliriaz-stripe)
- [@charlesw](https://twitter.com/charlesw_dev)

## Contributors

<a href="https://github.com/stripe-samples/accept-a-payment/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=stripe-samples/accept-a-payment" />
</a>

Made with [contrib.rocks](https://contrib.rocks).
