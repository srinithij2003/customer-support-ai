# CloudCart Troubleshooting FAQ and Support Policy

**Document ID:** CC-DOC-07 · **Version:** 5.0 · **Last updated:** 2026-10-15

> CloudCart is a fictional product created for the Sun Info Media AI/ML hackathon. All details are invented.

## 1. Contacting CloudCart Support

### 1.1 Channels and hours

| Channel | Plans | Hours |
|---------|-------|-------|
| Email (support@cloudcart.example) | All plans | Tickets accepted 24/7 |
| Live chat (in the admin) | Growth, Enterprise | Monday–Friday, 09:00–18:00 UTC |
| Phone | Enterprise | 24/7 for Critical issues. Monday–Friday, 09:00–18:00 UTC for other issues. |
| Dedicated success manager | Enterprise | Business hours in the customer's region |

Service status and incidents are posted at `https://status.cloudcart.example`. Merchants can subscribe to email or SMS updates there.

### 1.2 What to include in a ticket

- Store ID (shown in **Settings > Account**)
- Order number, product SKU, payout ID or API request ID, if relevant
- The exact **error code** (for example `CC-PAY-505`) and error message
- When the problem started, with time zone
- How many shoppers or orders are affected
- Steps to reproduce, screenshots, browser and device

Tickets that include an error code and store ID are resolved about twice as fast on average.

## 2. Ticket priority levels

Support assigns a priority to every ticket based on **business impact**, not on how the request is worded. Support may raise or lower the priority after reviewing the ticket.

| Priority | Definition | Examples |
|----------|------------|----------|
| **Critical (P1)** | The store cannot sell, or there is a security or data incident. No workaround. | Storefront down; checkout fails for all shoppers; payments fail for all shoppers (CC-PAY-505 everywhere); suspected account takeover or data breach |
| **High (P2)** | A core function is badly affected for many shoppers, or money is missing, but the store can still sell. | Payments failing for some card types; payout missing for more than 3 business days; orders not syncing to fulfilment; storefront stock wrong for more than 15 minutes; confirmed duplicate charges on many orders |
| **Medium (P3)** | One feature or one order is affected and a workaround exists. | A discount code not applying; a single failed refund; one webhook disabled; one shopper not receiving emails; CSV import errors |
| **Low (P4)** | Questions, how-to requests, feature requests and cosmetic issues. | How to set up shipping zones; how to change an email template; a feature suggestion |

### 2.1 First response targets

| Priority | Starter | Growth | Enterprise |
|----------|---------|--------|------------|
| Critical (P1) | 1 hour | 30 minutes | 15 minutes |
| High (P2) | 8 hours | 4 hours | 2 hours |
| Medium (P3) | 2 business days | 1 business day | 8 business hours |
| Low (P4) | 5 business days | 3 business days | 2 business days |

Critical and High targets apply 24/7. Medium and Low targets count business hours only.

### 2.2 Updates during an incident

For Critical tickets, Support posts an update at least every **60 minutes** until the issue is resolved or downgraded. For High tickets, at least every **4 hours** during business hours.

## 3. Escalation policy

### 3.1 Support tiers

- **Tier 1:** Front-line support. Handles how-to questions, account access, known issues and documented fixes.
- **Tier 2:** Senior specialists for payments, integrations and data issues. Can review logs and make account-level changes.
- **Tier 3:** CloudCart engineering. Handles confirmed product bugs and outages.

### 3.2 When a ticket is escalated

A ticket is escalated from Tier 1 to Tier 2 when **any** of these is true:

1. The ticket is **Critical (P1)**.
2. The first response target or the resolution target was **missed**.
3. The merchant reports a **financial loss over $1,000**, or the issue involves funds held, missing payouts or many duplicate charges.
4. The merchant has contacted Support about the **same issue 3 or more times within 7 days**.
5. The issue involves **security, account takeover, or personal data** (for example a data deletion request that could not be completed).
6. The issue involves a **chargeback dispute, legal threat or regulator complaint**.
7. A documented fix was tried and did not work, and the cause is not known.
8. An **Enterprise** merchant or their success manager asks for escalation.

Tier 2 escalates to **Tier 3 engineering** when a product bug is confirmed or reproduced, or when several merchants report the same problem at the same time.

### 3.3 Requesting escalation

Merchants can ask for escalation by replying to the ticket with the word **ESCALATE** and the reason. A Tier 2 specialist reviews the request within the ticket's first response target. Escalation requests are not accepted for Low (P4) tickets unless rule 2 or rule 4 in §3.2 applies.

### 3.4 Resolution targets

| Priority | Target to resolve or provide a workaround |
|----------|-------------------------------------------|
| Critical (P1) | 4 hours |
| High (P2) | 1 business day |
| Medium (P3) | 5 business days |
| Low (P4) | 10 business days, or answered with a feature request reference |

## 4. Error code index

| Code | Meaning | Guide |
|------|---------|-------|
| CC-AUTH-101 | Invalid email or password | CC-DOC-01 §11 |
| CC-AUTH-102 | Email address not verified | CC-DOC-01 §3.2 |
| CC-AUTH-103 | Account temporarily locked (30 minutes) | CC-DOC-01 §6.1 |
| CC-AUTH-104 | Extended lockout: password reset required | CC-DOC-01 §6.2 |
| CC-AUTH-105 | Invalid or expired 2FA code | CC-DOC-01 §7.1 |
| CC-AUTH-106 | Password reset link expired or already used | CC-DOC-01 §5.2 |
| CC-AUTH-107 | Password does not meet requirements | CC-DOC-01 §5.1 |
| CC-AUTH-108 | SSO sign-in required | CC-DOC-01 §4.1 |
| CC-AUTH-109 | Email address already registered | CC-DOC-01 §3.1 |
| CC-AUTH-110 | New-location sign-in needs confirmation | CC-DOC-01 §4.3 |
| CC-AUTH-111 | Session expired | CC-DOC-01 §4.2 |
| CC-CHK-201 | Discount code not found | CC-DOC-05 §5.5 |
| CC-CHK-202 | Discount code expired or not yet active | CC-DOC-05 §5.5 |
| CC-CHK-203 | Item no longer available in requested quantity | CC-DOC-05 §4.2 |
| CC-CHK-204 | Minimum purchase not met | CC-DOC-05 §5.5 |
| CC-CHK-205 | Discount usage limit reached | CC-DOC-05 §5.5 |
| CC-CHK-206 | Discount cannot be combined | CC-DOC-05 §5.4 |
| CC-CHK-207 | No shipping available to address | CC-DOC-05 §6 |
| CC-CHK-208 | Cart limit exceeded | CC-DOC-05 §2 |
| CC-CHK-209 | Checkout session expired (60 minutes) | CC-DOC-05 §4.1 |
| CC-CHK-210 | Postal code does not match region | CC-DOC-05 §6 |
| CC-INV-301 | Duplicate SKU | CC-DOC-02 §2.2 |
| CC-INV-302 | CSV import file cannot be read | CC-DOC-02 §4.3 |
| CC-INV-303 | Variant or option limit exceeded | CC-DOC-02 §3 |
| CC-INV-304 | Image upload failed | CC-DOC-02 §2.3 |
| CC-INV-305 | Stock cannot go below zero | CC-DOC-02 §5.3 |
| CC-INV-306 | Product limit for plan reached | CC-DOC-02 §2.4 |
| CC-INV-307 | Location limit for plan reached | CC-DOC-02 §6 |
| CC-INV-308 | Transfer exceeds available stock | CC-DOC-02 §6 |
| CC-ORD-401 | Fulfilled order cannot be cancelled | CC-DOC-03 §4.2 |
| CC-ORD-402 | Order cannot be edited after fulfilment | CC-DOC-03 §5 |
| CC-ORD-403 | Fulfilment quantity exceeds unfulfilled quantity | CC-DOC-03 §6.1 |
| CC-ORD-404 | Tracking number does not match carrier | CC-DOC-03 §6.1 |
| CC-ORD-405 | Return window expired | CC-DOC-03 §7.1 |
| CC-ORD-406 | Item is final sale | CC-DOC-03 §7.1 |
| CC-ORD-407 | Shopper cancellation window passed | CC-DOC-03 §4.1 |
| CC-PAY-501 | Card declined by issuer | CC-DOC-04 §4.1 |
| CC-PAY-502 | Insufficient funds | CC-DOC-04 §4.1 |
| CC-PAY-503 | 3D Secure or OTP authentication failed | CC-DOC-04 §4.1 |
| CC-PAY-504 | Payment session timed out (15 minutes) | CC-DOC-04 §4.1 |
| CC-PAY-505 | Payment processor unavailable | CC-DOC-04 §4.2 |
| CC-PAY-506 | Refund exceeds refundable amount | CC-DOC-04 §6.2 |
| CC-PAY-507 | Refund window (180 days) passed | CC-DOC-04 §6.2 |
| CC-PAY-508 | Payout failed: invalid bank details | CC-DOC-04 §7.2 |
| CC-PAY-509 | Authorisation expired | CC-DOC-04 §3.2 |
| CC-PAY-510 | Possible duplicate payment blocked | CC-DOC-04 §5.2 |
| CC-INT-601 | API rate limit exceeded | CC-DOC-06 §5.3 |
| CC-INT-602 | Invalid or revoked API key | CC-DOC-06 §5.2 |
| CC-INT-603 | API key missing required scope | CC-DOC-06 §5.2 |
| CC-INT-604 | Webhook delivery failed | CC-DOC-06 §4.3 |
| CC-INT-605 | Webhook disabled after repeated failures | CC-DOC-06 §4.3 |
| CC-INT-606 | Sender domain not verified | CC-DOC-06 §2.3 |
| CC-INT-607 | SMS quota used up | CC-DOC-06 §3 |
| CC-INT-608 | App connection expired | CC-DOC-06 §6.2 |

## 5. Frequently asked questions

### 5.1 I'm locked out of my account. What do I do?
After 5 failed sign-in attempts in 15 minutes, the account is locked for 30 minutes (CC-AUTH-103). Wait, or ask an Owner or Admin to unlock it. If you were locked out 3 times in 24 hours (CC-AUTH-104), you must reset your password. See CC-DOC-01 §6.

### 5.2 My password reset link doesn't work.
Reset links are valid for 30 minutes and work only once. Requesting a new link cancels older ones. Use the most recent email. See CC-DOC-01 §5.2.

### 5.3 A customer was charged twice. What should I do?
First check whether both payments were captured. If one was a failed or timed-out attempt, it is a pending authorisation that disappears within 5–7 business days. No refund is needed. If two orders were captured, cancel the duplicate with a refund. See CC-DOC-04 §5.

### 5.4 How long do refunds take?
Card and wallet refunds take 5–10 business days. UPI refunds take 2–4 business days. If a refund has not arrived after 10 business days, give the customer the ARN from the refund receipt. See CC-DOC-04 §6.3.

### 5.5 Can I refund to a different card?
No. Refunds go to the original payment method only. See CC-DOC-04 §6.2.

### 5.6 Why can't I cancel this order?
Orders with fulfilled items cannot be cancelled (CC-ORD-401). Create a return instead. See CC-DOC-03 §4 and CC-DOC-03 §7.

### 5.7 A customer wants to cancel, but the cancel button is gone.
Shoppers can cancel only within 2 hours of ordering and only before fulfilment (CC-ORD-407). The merchant can still cancel it if nothing is fulfilled. See CC-DOC-03 §4.

### 5.8 My discount code isn't working.
Check the error code. The usual causes are wrong dates for the store time zone (CC-CHK-202), a minimum purchase (CC-CHK-204), the usage limit (CC-CHK-205), or another discount already applied (CC-CHK-206). See CC-DOC-05 §5.5.

### 5.9 The product shows in stock, but checkout says it is unavailable.
Carts do not reserve stock. Another shopper probably reserved or bought the last units at the payment step (CC-CHK-203). See CC-DOC-05 §4.2 and CC-DOC-02 §5.2.

### 5.10 I updated stock, but the storefront still shows the old number.
Changes normally appear within 60 seconds. If it has been more than 15 minutes, follow CC-DOC-02 §5.4 and contact Support. This is High priority.

### 5.11 My payout hasn't arrived.
Check **Finances > Payouts** for the expected date and any CC-PAY-508 failure. New stores have a 7-day hold on the first payout. If a payout is more than 3 business days late, contact Support with the payout ID. See CC-DOC-04 §7.

### 5.12 Customers say checkout is failing for everyone.
Check the status page. If payments are failing for all shoppers, contact Support right away. This is Critical (P1). Enterprise merchants can call 24/7. See CC-DOC-04 §4.2 and §2 of this document.

### 5.13 My API requests are being rejected with 429.
You have gone over your plan's rate limit (CC-INT-601). Wait for the `Retry-After` time and use bulk endpoints. See CC-DOC-06 §5.3.

### 5.14 My webhook stopped working.
After 24 hours of failed deliveries, webhooks are disabled (CC-INT-605). Fix the endpoint so it returns 2xx within 10 seconds, then re-enable it. Missed events are not resent. See CC-DOC-06 §4.3.

### 5.15 Emails to my customers are coming from no-reply@cloudcart.example instead of my domain.
Your sender domain is not verified yet (CC-INT-606). Add the SPF, DKIM and DMARC records and allow up to 72 hours. See CC-DOC-06 §2.3.

### 5.16 How do I close my store, and can I get my data back?
Only the Owner can close the store. Data is kept for 90 days, and you can reactivate within that time. After 90 days, data is permanently deleted. See CC-DOC-01 §10.

### 5.17 How do I get my ticket escalated?
Reply to the ticket with **ESCALATE** and the reason. Tickets are also escalated automatically in the cases listed in §3.2.

## 6. Questions outside this documentation

The CloudCart documentation does not cover every topic. If a question is not answered in CC-DOC-01 to CC-DOC-07, support agents and automated assistants must **not guess**. They should say the information is not in the documentation, ask for the details listed in §1.2, and create a ticket for a human agent.
