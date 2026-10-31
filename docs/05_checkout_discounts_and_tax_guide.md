# CloudCart Checkout, Discounts and Tax Guide

**Document ID:** CC-DOC-05 · **Version:** 2.5 · **Last updated:** 2026-10-15

> CloudCart is a fictional product created for the Sun Info Media AI/ML hackathon. All details are invented.

## 1. Overview

This guide explains how the shopping cart and checkout work, how to set up discounts, and how CloudCart calculates shipping and tax. It also lists the checkout errors shoppers may see.

## 2. Cart

- A cart can hold up to **100 different line items**. Each line item can have a quantity of up to **999**. Going over either limit returns **CC-CHK-208**.
- The cart total cannot be more than **$50,000** (or the same amount in the store currency). Larger orders must be placed as draft orders by the merchant (CC-DOC-03 §2).
- Carts are saved for **30 days** for signed-in shoppers and **14 days** for guests (stored in a browser cookie). Clearing cookies empties a guest cart.
- Adding items to the cart does **not** reserve stock (CC-DOC-02 §5.2). The cart shows a warning if an item's stock drops below the quantity in the cart.
- Prices in the cart are updated if the merchant changes them before checkout is completed.

## 3. Checkout flow

### 3.1 Steps

1. **Information:** email address or sign-in.
2. **Shipping:** shipping address and shipping method. Tax is calculated at this step.
3. **Payment:** payment method and billing address.
4. **Review:** order summary and **Place order**.

### 3.2 Guest checkout

Guest checkout is **on by default**. Merchants can require shoppers to have an account in **Settings > Checkout > Customer accounts**. Shoppers who check out as guests can create an account afterwards from the order confirmation page, and the order is linked to the new account.

## 4. Checkout sessions and stock reservation

### 4.1 Checkout session

- A checkout session lasts **60 minutes** from the moment the shopper starts checkout.
- After 60 minutes, the session expires (**CC-CHK-209**). The cart is kept, but the shopper must start checkout again. Any discount code must be applied again.

### 4.2 Stock reservation at the payment step

- When the shopper reaches the **Payment** step, the items are reserved for **15 minutes**.
- If payment is not finished within 15 minutes, the reservation is released and the payment fails with **CC-PAY-504** (CC-DOC-04 §4.1).
- If another shopper bought or reserved the last units before this shopper reached the payment step, checkout shows **CC-CHK-203** and lets the shopper remove the item or lower the quantity.

## 5. Discounts

### 5.1 Discount types

| Type | Example | Notes |
|------|---------|-------|
| Percentage | 10% off the order | Can apply to the whole order, a collection or specific products. |
| Fixed amount | $15 off | Never makes the order total less than 0. |
| Free shipping | Free standard shipping | Can be limited to shipping rates under a set amount. |
| Buy X get Y | Buy 2, get 1 free | The cheapest qualifying item is the free item. |

### 5.2 Discount codes

- Codes are **3 to 32 characters** long and can contain letters, numbers and hyphens.
- Codes are **not case-sensitive**. `SUMMER10` and `summer10` are the same code.
- Each code can have:
  - a start date and an optional end date,
  - a **minimum purchase** amount or minimum quantity,
  - a **total usage limit** (for example the first 500 uses),
  - a **one use per customer** limit, checked by email address,
  - eligibility rules (all shoppers, specific customer tags, or first-time customers only).
- Discount codes are applied to the subtotal **before tax and shipping**.

### 5.3 Automatic discounts

- Automatic discounts apply without a code when the cart meets the conditions.
- A store can have up to **25 active automatic discounts**.
- If more than one automatic discount qualifies, the one that gives the shopper the **largest saving** is applied.

### 5.4 Combining discounts

- **Starter:** only **one discount** can apply per order, either an automatic discount or a code.
- **Growth and Enterprise:** an order can combine **one order discount** (percentage or fixed amount) with **one free shipping discount**, if both discounts have **Combinable** turned on.
- Two order discounts can never be combined. Trying to apply a second one returns **CC-CHK-206**.

### 5.5 Discount code errors

| Code | Message shown to the shopper | Common cause |
|------|------------------------------|--------------|
| CC-CHK-201 | This discount code is not valid | Code typed wrong, or deleted by the merchant. |
| CC-CHK-202 | This discount code has expired or is not active yet | Outside the code's start and end dates. Dates use the store's time zone. |
| CC-CHK-204 | Minimum purchase not met | Subtotal or quantity is below the code's minimum. The message shows the amount still needed. |
| CC-CHK-205 | This discount code has reached its usage limit | Total limit reached, or the shopper already used a one-per-customer code. |
| CC-CHK-206 | This discount cannot be combined with other discounts | Another discount is already applied (§5.4). |

Common merchant checks when a shopper says a code does not work:

1. Check that the code is **Active** in **Discounts** and that the dates are right for the store's time zone.
2. Check the minimum purchase and eligibility rules.
3. Check the usage count against the usage limit.
4. Check whether the items in the cart are eligible. Products on sale (with a compare-at price) are excluded if **Exclude sale items** is on.

## 6. Shipping zones and addresses

- Merchants must set up at least one **shipping zone** (a group of countries or regions with shipping rates) in **Settings > Shipping**.
- If the shopper's address is not in any shipping zone, checkout shows **CC-CHK-207**: "We don't ship to this address." The merchant must add the region to a shipping zone.
- CloudCart checks that the postal code matches the country, state or province. A mismatch returns **CC-CHK-210**. The shopper should correct the address.
- Products marked as **digital** do not need a shipping address.

## 7. Tax

### 7.1 How tax is calculated

- Tax is calculated automatically from the **shipping address**, or the billing address for digital products.
- Tax is calculated at the **Shipping** step and shown on the payment and review steps.
- Merchants choose whether product prices **include tax** (common in the EU, UK, India and Australia) or have tax **added at checkout** (common in the US). Set this in **Settings > Taxes**.
- CloudCart updates its built-in tax rates on the **1st of each month**. Merchants are responsible for checking that rates are correct for their business and registering with tax authorities where needed.

### 7.2 Tax overrides and exemptions

- Merchants can set a different tax rate for specific products or collections, for example reduced-rate food items.
- Customers tagged `tax-exempt` are not charged tax. The tag must be added before checkout. Tax cannot be removed from an order after it is placed. Issue a partial refund for the tax amount instead (CC-DOC-04 §6).

### 7.3 Tax and discounts

When prices include tax, discounts lower the tax-inclusive price and the tax is recalculated on the discounted amount. When tax is added at checkout, tax is calculated on the subtotal after discounts.

## 8. Abandoned checkouts

- A checkout counts as abandoned when the shopper entered an email address but did not place the order within **1 hour**.
- **Growth and Enterprise** stores can send an automatic recovery email after **1, 6, 10 or 24 hours** (default: 10 hours). The email contains a link that restores the cart.
- Recovery emails are sent only once per checkout and only to shoppers who agreed to receive marketing emails, if the store's region requires consent.
- Abandoned checkouts are listed for **90 days** under **Orders > Abandoned checkouts**.

## 9. Checkout error codes

| Code | Meaning | What to do |
|------|---------|------------|
| CC-CHK-201 | Discount code not found | Check the spelling, or the code was deleted (§5.5). |
| CC-CHK-202 | Discount code expired or not yet active | Check the dates in the store time zone (§5.5). |
| CC-CHK-203 | Item no longer available in the requested quantity | Remove the item or lower the quantity (§4.2). |
| CC-CHK-204 | Minimum purchase not met | Add items to reach the minimum (§5.5). |
| CC-CHK-205 | Discount usage limit reached | Code cannot be used again (§5.5). |
| CC-CHK-206 | Discount cannot be combined | Remove the other discount (§5.4). |
| CC-CHK-207 | No shipping available to this address | Merchant adds the region to a shipping zone (§6). |
| CC-CHK-208 | Cart limit exceeded | Up to 100 line items and 999 units per line (§2). |
| CC-CHK-209 | Checkout session expired (60 minutes) | Start checkout again (§4.1). |
| CC-CHK-210 | Postal code does not match the region | Correct the address (§6). |
