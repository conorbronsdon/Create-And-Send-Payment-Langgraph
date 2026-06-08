# Create and Send Payment — LangGraph + Swytchcode

Automates payment link creation and customer notification:
1. Generates a Stripe payment link for $99
2. Emails the link to the customer via Resend

Built with [LangGraph](https://github.com/langchain-ai/langgraph) and [Swytchcode](https://swytchcode.com).

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and fill in your API keys
cp .env.example .env

# 3. Fetch all integrations
swytchcode bootstrap
```

## Run

```bash
python main.py
```

## Canonical IDs Used

| Service | Canonical ID                        |
|---------|-------------------------------------|
| Stripe  | `prices.price.create`               |
| Stripe  | `payment_links.payment_link.create` |
| Resend  | `emails.email.create`               |
