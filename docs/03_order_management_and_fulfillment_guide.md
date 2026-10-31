# CloudCart Order Management and Fulfillment Guide

**Document ID:** CC-DOC-03 · **Version:** 3.0 · **Last updated:** 2026-10-15

> CloudCart is a fictional product created for the Sun Info Media AI/ML hackathon. All details are invented.

## 1. Overview

This guide covers the order lifecycle in CloudCart: how orders are created, cancelled, edited, shipped and returned. Payment and refund rules are in CC-DOC-04. Checkout rules are in CC-DOC-05.

## 2. Order numbers and placement

- Order numbers start at **#1001** and go up by one for each order. Owners can add a prefix or suffix in **Settings > Orders** (for example `SM-1001`).
- An order is created when the shopper completes checkout. For card and wallet payments, the order is created only after the payment is authorised.
- For **manual payment methods** (bank transfer, cash on delivery), the order is created right away with the status **Pending payment**.
- Merchants can create orders for customers from **Orders > Create order** (draft orders). A draft order can be sent to the customer as an invoice with a payment link. The payment link is valid for **30 days**.

## 3. Order statuses

| Status | Meaning |
|--------|---------|
| Pending payment | Order placed with a manual payment method. Payment not yet received. |
| Paid | Payment captured. Nothing shipped yet. |
| Processing | Merchant has started preparing the order (optional status set manually). |
| Partially fulfilled | Some items shipped. |
| Fulfilled | All items shipped. |
| Delivered | Carrier confirmed delivery of all shipments. |
| Cancelled | Order cancelled before fulfilment. |
| Refunded | Full amount refunded. |
| Partially refunded | Part of the amount refunded. |

**Pending payment orders are cancelled automatically after 7 days** if the merchant does not mark them as paid. Reserved stock is then released.

## 4. Cancelling orders

### 4.1 Cancellation by the shopper

- Shoppers can cancel from their account (**My orders > Cancel order**) within **2 hours** of placing the order, as long as nothing has been fulfilled.
- After 2 hours, the cancel button is hidden and an attempt through the API returns **CC-ORD-407**. The shopper must contact the merchant.
- Guest shoppers cannot cancel themselves. They must contact the merchant.

### 4.2 Cancellation by the merchant

1. Open the order and click **More actions > Cancel order**.
2. Choose a reason: Customer request, Fraud, Inventory unavailable, Payment declined, or Other.
3. Choose whether to **refund the payment** and **restock items**. Both are selected by default.
4. Choose whether to notify the customer.

- Only orders with **no fulfilled items** can be cancelled. Cancelling a fulfilled or partially fulfilled order returns **CC-ORD-401**. Process a return instead (Section 7).
- Cancelling refunds the full amount to the original payment method. Transaction fees are not returned to the merchant (CC-DOC-04 §6.4).

## 5. Editing orders

- You can add items, remove items, change quantities and apply a discount on orders that have **no fulfilled items**. After any item is fulfilled, editing returns **CC-ORD-402**.
- If the edit increases the total, CloudCart sends the customer a payment link for the difference. The link is valid for **72 hours**. Fulfilment of the added items stays on hold until the difference is paid.
- If the edit lowers the total, the difference is refunded automatically to the original payment method.
- You can change the shipping address until the order, or the shipment the address applies to, is fulfilled.
- Every edit is recorded in the order timeline with the staff member's name and the time.

## 6. Fulfillment and shipping

### 6.1 Fulfilling an order

1. Open the order and click **Fulfil items**.
2. Choose the items and quantities to ship. You can ship part of an order and send the rest later.
3. Choose the carrier and enter the tracking number, or buy a shipping label through CloudCart Shipping.
4. Click **Fulfil**. The customer receives a shipping confirmation email with the tracking link (CC-DOC-06 §2).

- You cannot fulfil more units than remain unfulfilled on the order (**CC-ORD-403**).
- CloudCart checks the tracking number format for supported carriers. A number that does not match the carrier's format returns **CC-ORD-404**. Pick the correct carrier or choose **Other carrier** to skip the check.

### 6.2 Tracking updates

- Tracking status is refreshed from supported carriers every **4 hours**.
- When every shipment on an order shows delivered, the order status changes to **Delivered** and the delivery email is sent.
- Tracking for **Other carrier** shipments is not refreshed. The order stays **Fulfilled** until the merchant marks it delivered.

### 6.3 Delayed or lost shipments

- A shipment is flagged **Possibly delayed** if tracking shows no update for **5 days** (domestic) or **10 days** (international).
- After **7 days** (domestic) or **14 days** (international) with no tracking update, the merchant can open a carrier claim for labels bought through CloudCart Shipping. Claims must be filed within **30 days** of the label purchase date.
- For labels bought outside CloudCart, the merchant must contact the carrier directly.
- Common next steps for a shopper who has not received an order: check the tracking link, confirm the shipping address on the order, then contact the merchant. The merchant can reship or refund (CC-DOC-04 §6).

### 6.4 Order holds

CloudCart places an order on **Fraud review hold** when its fraud analysis rates the order as **High risk**. Held orders cannot be fulfilled until a staff member clicks **Approve** or **Cancel**. Holds do not expire, but authorised payments expire after 7 days (CC-DOC-04 §3.2), so review held orders quickly.

## 7. Returns and exchanges

### 7.1 Return window

- The default return window is **30 days after delivery**. You can set it from 0 to 90 days in **Settings > Returns**. A request outside the window returns **CC-ORD-405**.
- Items marked **Final sale** on the product page cannot be returned (**CC-ORD-406**).
- Gift cards and digital products cannot be returned.

### 7.2 Return process

| Return status | Meaning |
|---------------|---------|
| Requested | Customer asked to return items from their account. |
| Approved | Merchant approved the return. A return label or instructions are sent. |
| Rejected | Merchant declined the return. A reason is required and sent to the customer. |
| Received | Merchant confirmed the items arrived back. |
| Refunded | Refund issued for the returned items. |

- Merchants must approve or reject a requested return within **3 business days**. After that, the request is approved automatically if **Auto-approve overdue returns** is on (default: on).
- When marking a return **Received**, choose **Restock item** to add the units back to inventory (CC-DOC-02 §5.2).
- The refund is not issued automatically when items are received. The merchant must click **Refund** (CC-DOC-04 §6).
- Return shipping costs are paid by the customer by default. Merchants can choose to provide free return labels.

### 7.3 Exchanges

An exchange is a return plus a new order. Approve the return, then create a draft order for the replacement item and apply a 100% discount, or charge the price difference.

## 8. Order error codes

| Code | Meaning | What to do |
|------|---------|------------|
| CC-ORD-401 | Order cannot be cancelled because items are fulfilled | Process a return (§4.2, §7). |
| CC-ORD-402 | Order cannot be edited after fulfilment | Create a new order or a return (§5). |
| CC-ORD-403 | Fulfilment quantity exceeds unfulfilled quantity | Check remaining quantities (§6.1). |
| CC-ORD-404 | Tracking number does not match carrier format | Pick the correct carrier or Other carrier (§6.1). |
| CC-ORD-405 | Return window has expired | The merchant may make an exception manually (§7.1). |
| CC-ORD-406 | Item is final sale and cannot be returned | See §7.1. |
| CC-ORD-407 | Shopper cancellation window (2 hours) has passed | Contact the merchant (§4.1). |
