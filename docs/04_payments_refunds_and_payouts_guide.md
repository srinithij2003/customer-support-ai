# CloudCart Payments, Refunds and Payouts Guide

**Document ID:** CC-DOC-04 · **Version:** 4.1 · **Last updated:** 2026-10-15

> CloudCart is a fictional product created for the Sun Info Media AI/ML hackathon. All details are invented.

## 1. Overview

CloudCart stores can take payments through **CloudCart Payments** (the built-in payment processor) or through a supported **external payment gateway**. This guide covers payment methods, failed and duplicate payments, refunds, payouts and chargebacks.

## 2. Payment methods and fees

### 2.1 Supported methods

- **Cards:** Visa, Mastercard, American Express, RuPay
- **Digital wallets:** Apple Pay, Google Pay
- **UPI** (stores with Indian rupee (INR) as the store currency only)
- **Manual methods:** bank transfer, cash on delivery (COD). Orders paid by manual methods start as **Pending payment** (CC-DOC-03 §2).

### 2.2 Transaction fees

| Plan | CloudCart Payments fee | Extra platform fee when using an external gateway |
|------|------------------------|---------------------------------------------------|
| Starter | 2.9% + $0.30 per transaction | 1.0% |
| Growth | 2.6% + $0.30 per transaction | 0.5% |
| Enterprise | 2.4% + $0.30 per transaction | 0% |

- International cards have an extra **1.5%** fee.
- Currency conversion has an extra **1.0%** fee.
- Manual payment methods have no CloudCart transaction fee.

## 3. Authorisation and capture

### 3.1 Automatic capture (default)

The payment is authorised and captured as soon as the order is placed.

### 3.2 Manual capture

Turn this on in **Settings > Payments > Capture method**. The card is authorised at checkout. The merchant captures the payment later, for example when the order ships.

- Authorisations **expire after 7 days**. Capturing an expired authorisation returns **CC-PAY-509**. Send the customer a new payment link from the order page.
- You can capture less than the authorised amount. The rest is released to the customer.
- You cannot capture more than the authorised amount.

## 4. Failed payments

### 4.1 Failure reasons

| Code | Reason shown to the shopper | Typical cause | What the shopper should do |
|------|------------------------------|---------------|----------------------------|
| CC-PAY-501 | Card declined | The card issuer refused the payment (for example blocked card, suspected fraud, or online payments turned off) | Contact the card issuer or use another card. |
| CC-PAY-502 | Insufficient funds | Not enough balance or credit limit | Use another payment method. |
| CC-PAY-503 | Authentication failed | The 3D Secure or OTP step failed, was cancelled or timed out | Try again and finish the bank's verification step. |
| CC-PAY-504 | Payment session timed out | The shopper did not finish payment within **15 minutes** | Go back to checkout and try again. |
| CC-PAY-505 | Payment service temporarily unavailable | The payment processor or gateway is having an outage | Wait a few minutes and try again. Check the status page. |

- CloudCart never shows the shopper detailed decline reasons from the issuer, for security. Merchants can see the issuer's decline code under **Orders > Abandoned checkouts > [checkout] > Payment attempts**.
- A shopper can try up to **5 payment attempts per checkout**. After that, the checkout is blocked for **1 hour** to prevent card testing.

### 4.2 When many payments fail at once

If several shoppers report failed payments at the same time, or **CC-PAY-505** appears repeatedly:

1. Check `https://status.cloudcart.example` for an active incident.
2. If you use an external gateway, check that the gateway's API credentials in **Settings > Payments** have not expired or been rotated.
3. Contact Support. When payments are failing for **all** shoppers, the issue is **Critical** priority (CC-DOC-07 §2).

## 5. Duplicate payments

### 5.1 Why a shopper may see two charges

- **Pending authorisation plus a successful charge:** when a first attempt fails or times out and the shopper pays again, the bank may show the failed attempt as a pending charge. Pending authorisations that were never captured **drop off automatically within 5–7 business days**. No refund is needed.
- **Two completed orders:** the shopper submitted checkout twice and two orders were created. Both are captured.

### 5.2 Duplicate protection

CloudCart blocks a second payment with the **same card, same amount and same store within 10 minutes** and shows **CC-PAY-510**. The shopper can confirm they want to pay again, for example when buying the same item twice on purpose.

### 5.3 Resolving a confirmed duplicate charge

1. Search **Orders** for the shopper's email address and find both orders.
2. Confirm that both payments show the status **Captured**.
3. Cancel the duplicate order with **Refund payment** selected (CC-DOC-03 §4.2).
4. Tell the shopper the refund will appear within **5–10 business days**.

Duplicate charges where both payments were captured should be resolved within **2 business days** of the shopper reporting them.

## 6. Refunds

### 6.1 Issuing a refund

1. Open the order and click **Refund**.
2. Choose the items and quantities, or enter a custom amount.
3. Choose whether to refund shipping.
4. Enter a reason (internal only) and click **Refund**.

### 6.2 Refund rules

- Refunds go back to the **original payment method only**. CloudCart cannot send a refund to a different card or bank account.
- The total refunded cannot be more than the captured amount (**CC-PAY-506**).
- Refunds through CloudCart Payments can be issued up to **180 days** after the original payment. After that, the refund button is disabled (**CC-PAY-507**) and the merchant must refund the shopper outside CloudCart, for example by issuing store credit or a bank transfer.
- Orders paid by manual methods (bank transfer, COD) are refunded outside CloudCart. Mark them refunded manually so reports stay correct.
- A merchant needs the **Issue refunds** permission (CC-DOC-01 §9).

### 6.3 Refund timing

| Payment method | Time until the shopper sees the refund |
|----------------|----------------------------------------|
| Cards | 5–10 business days |
| Apple Pay, Google Pay | 5–10 business days |
| UPI | 2–4 business days |

If a shopper has not received a refund after **10 business days**, the merchant can download a refund receipt with the **Acquirer Reference Number (ARN)** from the order page. The shopper can give the ARN to their bank to trace the refund.

### 6.4 Fees on refunds

CloudCart transaction fees are **not returned** when you refund a payment, fully or in part.

## 7. Payouts

### 7.1 Payout schedule

- CloudCart Payments sends your balance to your bank account on a **daily**, **weekly** (every Monday) or **monthly** (1st of the month) schedule. The default is daily.
- Funds from a payment become available for payout **2 business days** after capture.
- **First payout:** the first payout for a new store is held for **7 days** after the store's first successful sale, for risk review.
- Payouts in the store currency arrive within **1–2 business days** after they are sent.

### 7.2 Payout failures

- If the bank rejects a payout, for example because the account number is wrong or the account is closed, the payout fails with **CC-PAY-508**. The funds stay in your CloudCart balance.
- The Owner must update the bank account in **Settings > Payments > Payout account**. Only the Owner can change it (CC-DOC-01 §9). For security, changing the payout account holds payouts for **3 business days**.
- After the account is updated, the failed payout is retried automatically with the next scheduled payout.

### 7.3 Missing payouts

A payout is considered **missing** if it has not arrived **3 business days** after the date shown in **Finances > Payouts**. Contact Support with the payout ID. A missing payout is **High** priority (CC-DOC-07 §2).

### 7.4 Risk holds

CloudCart may hold payouts for up to **72 hours** for risk review, for example after a sudden large increase in sales or a high chargeback rate. The Owner receives an email explaining the hold and any documents needed.

## 8. Chargebacks

- A chargeback happens when a shopper disputes a charge with their bank.
- CloudCart emails the Owner and adds a **Dispute** banner to the order.
- The disputed amount plus a **$15 chargeback fee** is taken from your balance right away.
- You must submit evidence (proof of delivery, customer messages, tracking) within **7 days** from **Orders > [order] > Respond to dispute**. Unanswered disputes are lost automatically.
- Banks usually decide within **60–75 days**. If you win, the amount and the $15 fee are returned.
- Stores with a chargeback rate above **1%** of orders in a calendar month may have payouts held (Section 7.4).

## 9. Payment error codes

| Code | Meaning | What to do |
|------|---------|------------|
| CC-PAY-501 | Card declined by issuer | Shopper contacts their bank or uses another card (§4.1). |
| CC-PAY-502 | Insufficient funds | Use another payment method (§4.1). |
| CC-PAY-503 | 3D Secure or OTP authentication failed | Retry and finish verification (§4.1). |
| CC-PAY-504 | Payment session timed out (15 minutes) | Restart checkout (§4.1). |
| CC-PAY-505 | Payment processor unavailable | Retry later and check the status page (§4.2). |
| CC-PAY-506 | Refund exceeds refundable amount | Lower the amount (§6.2). |
| CC-PAY-507 | Refund window (180 days) has passed | Refund outside CloudCart (§6.2). |
| CC-PAY-508 | Payout failed because of invalid bank details | Owner updates the payout account (§7.2). |
| CC-PAY-509 | Authorisation expired (manual capture after 7 days) | Send a new payment link (§3.2). |
| CC-PAY-510 | Possible duplicate payment blocked | Shopper confirms the second payment if it is intended (§5.2). |
