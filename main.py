from swytchcode_runtime import exec as swytchcode_exec
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from dotenv import load_dotenv
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()


class PaymentState(TypedDict):
    customer_email: str
    customer_name: str
    payment_link_url: Optional[str]
    payment_link_id: Optional[str]
    email_sent: Optional[bool]


# ── Node 1: Generate Stripe payment link ($99) ────────────────────────────────

def create_payment_link(state: PaymentState) -> dict:
    print(f"[1/2] Generating Stripe payment link ($99.00)...")

    # Step 1a: Create a Stripe Price (payment_links requires a pre-created Price ID)
    price_result = swytchcode_exec("prices.price.create", {
        "body": {
            "currency":           "usd",
            "unit_amount":        9900,
            "product_data[name]": "Swytchcode Service",
        },
        "Authorization": f"Bearer {os.environ['STRIPE_SECRET_KEY']}",
    })
    price_id = (price_result or {}).get("data", {}).get("id")

    # Step 1b: Create payment link using the Price ID
    result = swytchcode_exec("payment_links.payment_link.create", {
        "body": {
            "line_items[0][price]":    price_id,
            "line_items[0][quantity]": "1",
        },
        "Authorization": f"Bearer {os.environ['STRIPE_SECRET_KEY']}",
    })
    payment_link_url = (result or {}).get("data", {}).get("url")
    payment_link_id  = (result or {}).get("data", {}).get("id")
    print(f"    ✔ Payment link created: {payment_link_url}")
    return {
        "payment_link_url": payment_link_url,
        "payment_link_id":  payment_link_id,
    }


# ── Node 2: Email the payment link to the customer ────────────────────────────

def email_payment_link(state: PaymentState) -> dict:
    print(f"[2/2] Emailing payment link to {state['customer_email']}...")
    swytchcode_exec("emails.email.create", {
        "body": {
            "from":    "onboarding@resend.dev",
            "to":      [state["customer_email"]],
            "subject": "Your Payment Link — $99.00",
            "html": (
                f"<h2>Hi {state['customer_name']},</h2>"
                f"<p>Click below to complete your payment of <strong>$99.00</strong>:</p>"
                f"<p><a href='{state['payment_link_url']}'>Pay $99.00</a></p>"
            ),
        },
        "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
    })
    print(f"    ✔ Payment link emailed")
    return {"email_sent": True}


# ── Build graph ───────────────────────────────────────────────────────────────

workflow = StateGraph(PaymentState)
workflow.add_node("create_payment_link", create_payment_link)
workflow.add_node("email_payment_link",  email_payment_link)

workflow.set_entry_point("create_payment_link")
workflow.add_edge("create_payment_link", "email_payment_link")
workflow.add_edge("email_payment_link",  END)

app = workflow.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    result = app.invoke({
        "customer_email":   os.environ["CUSTOMER_EMAIL"],
        "customer_name":    "John Smith",
        "payment_link_url": None,
        "payment_link_id":  None,
        "email_sent":       None,
    })

    print("\n✅ Payment link created and sent!")
    print(f"   Payment Link: {result['payment_link_url']}")
    print(f"   Email sent:   {result['email_sent']}")

