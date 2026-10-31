# CloudCart Notifications and Integrations Guide

**Document ID:** CC-DOC-06 · **Version:** 2.3 · **Last updated:** 2026-10-15

> CloudCart is a fictional product created for the Sun Info Media AI/ML hackathon. All details are invented.

## 1. Overview

This guide covers the emails and SMS messages CloudCart sends to shoppers and staff. It also covers webhooks, the REST API, API keys and third-party apps.

## 2. Email notifications

### 2.1 Shopper emails

| Email | Sent when | Can be turned off |
|-------|-----------|-------------------|
| Order confirmation | Order is placed | No |
| Payment received | A Pending payment order is marked paid | Yes |
| Shipping confirmation | Items are fulfilled. Includes the tracking link. | Yes |
| Delivery confirmation | Carrier confirms delivery | Yes |
| Order cancelled | Merchant or shopper cancels the order | Yes |
| Refund issued | A refund is processed | No |
| Abandoned checkout recovery | See CC-DOC-05 §8 (Growth and Enterprise) | Yes |
| Account invitation and password reset | See CC-DOC-01 §8 | No |

- Edit templates in **Settings > Notifications**. Templates use Liquid-style placeholders such as `{{ order.number }}` and `{{ customer.first_name }}`.
- Use **Send test email** to preview a template with sample data.
- Emails are queued and usually delivered within **2 minutes**.

### 2.2 Staff emails

- New order alerts (optional, per staff member)
- Daily low-stock digest at 08:00 store time (CC-DOC-02 §7)
- Payout sent and payout failed (CC-DOC-04 §7)
- Chargeback opened (CC-DOC-04 §8)
- Security alerts: account locked, new-location sign-in, API key created (always sent)

### 2.3 Custom sender domain

By default, emails are sent from `no-reply@cloudcart.example` with the store name as the sender name. To send from your own domain (for example `orders@yourstore.com`):

1. Go to **Settings > Notifications > Sender email** and enter the address.
2. Add the **SPF**, **DKIM** and **DMARC** DNS records that CloudCart shows to your domain's DNS settings.
3. Click **Verify**.

- DNS changes can take up to **72 hours** to take effect.
- Until the domain is verified, emails are still sent from `no-reply@cloudcart.example`, and the settings page shows **CC-INT-606**.
- If verification fails after 72 hours, check that the records were added exactly as shown, with no extra quotation marks or spaces, and that there is only **one SPF record** on the domain.

### 2.4 Shoppers not receiving emails

1. Check **Customers > [customer] > Timeline**. Each email shows a status: Delivered, Bounced or Marked as spam.
2. **Bounced:** the email address is wrong or the inbox is full. Correct the address on the customer record.
3. **Marked as spam:** the shopper's provider stops further marketing emails. Order emails are still attempted.
4. If emails show **Delivered**, ask the shopper to check spam and promotions folders.

## 3. SMS notifications

- Available on **Growth** (1,000 SMS per month included) and **Enterprise** (5,000 SMS per month included).
- Extra SMS cost **$0.02** each in the US and India and **$0.06** each in other countries. Extra SMS must be turned on in **Settings > Notifications > SMS**.
- If the monthly quota runs out and extra SMS is off, SMS stop until the next billing cycle, and the notification settings page shows **CC-INT-607**. Email notifications continue as normal.
- Shoppers must opt in to SMS at checkout. Shoppers can reply **STOP** to opt out.

## 4. Webhooks

### 4.1 Setting up a webhook

1. Go to **Settings > Developers > Webhooks > Add webhook**.
2. Choose an event and enter an endpoint URL. **The URL must use HTTPS.**
3. Choose the API version and click **Save**. A store can have up to **50 webhooks**.

### 4.2 Events

| Event | Fires when |
|-------|------------|
| `order.created` | An order is placed |
| `order.paid` | Payment is captured |
| `order.fulfilled` | All items on an order are fulfilled |
| `order.cancelled` | An order is cancelled |
| `refund.created` | A refund is issued |
| `product.updated` | A product or variant is changed |
| `inventory.low_stock` | A variant reaches its low-stock threshold |
| `customer.created` | A shopper account is created |

### 4.3 Delivery and retries

- CloudCart sends a `POST` request with a JSON body.
- Your endpoint must return a **2xx status code within 10 seconds**. Any other response, or no response, counts as a failure (**CC-INT-604**).
- Failed deliveries are retried **8 times over 24 hours** with exponential backoff.
- If every delivery to a webhook fails for **24 hours in a row**, the webhook is **disabled automatically** (**CC-INT-605**) and the Owner and Admins receive an email. Fix the endpoint, then click **Re-enable**. Events from the disabled period are **not** resent. Use the REST API to fetch missed data.
- Webhooks can arrive out of order and can occasionally be delivered more than once. Use the `X-CloudCart-Event-Id` header to ignore duplicates.

### 4.4 Verifying webhooks

Every request includes an `X-CloudCart-Signature` header. It is a Base64-encoded **HMAC-SHA256** hash of the raw request body, made with the webhook's signing secret. Compute the same hash on your server and compare. Reject requests that do not match. The signing secret is shown in the webhook's settings and can be rotated at any time.

## 5. REST API

### 5.1 Basics

- Base URL: `https://api.cloudcart.example/v2`
- Requests and responses use JSON.
- Authenticate with an API key in the header `Authorization: Bearer <api_key>`.
- API version `v1` is deprecated and will stop working on **2027-03-31**.

### 5.2 API keys

- Owners and Admins create API keys in **Settings > Developers > API keys**.
- Each key has **scopes**, for example `orders:read`, `orders:write`, `products:read`, `products:write`, `customers:read`.
- **The full key is shown only once**, when it is created. If it is lost, create a new key and revoke the old one.
- A store can have up to **10 active API keys**.
- A missing, wrong or revoked key returns HTTP **401** with **CC-INT-602**.
- A valid key without the scope an endpoint needs returns HTTP **403** with **CC-INT-603**.
- API keys are **not** revoked when the staff member who created them is removed. Review keys when staff leave.

### 5.3 Rate limits

- Limits depend on the plan: **60**, **300** or **1,200 requests per minute** for Starter, Growth and Enterprise (CC-DOC-01 §2). The limit applies to the whole store, shared across all keys.
- Going over the limit returns HTTP **429** with **CC-INT-601**. The `Retry-After` header gives the number of seconds to wait.
- Every response includes `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers.
- Bulk endpoints (for example `POST /v2/products/bulk`) accept up to **250 items** per request and count as **one** request.

### 5.4 Pagination

List endpoints return up to **100 items** per page (default 50). Use the `next_cursor` value from the response to fetch the next page.

## 6. Apps and integrations

### 6.1 Installing apps

- Apps from the **CloudCart App Marketplace** add features such as accounting sync, marketing, reviews and shipping.
- When you install an app, you approve the scopes it needs. Only Owners and Admins can install apps.
- Removing an app revokes its access right away. Data the app already copied to its own systems is covered by the app developer's privacy policy, not CloudCart's.

### 6.2 App connection expired

Some apps need you to sign in to the other service again from time to time, for example every **90 days** for some accounting tools. When a connection expires, sync stops and the app shows **CC-INT-608**. Open the app and click **Reconnect**.

### 6.3 Sync delays

Most apps sync through webhooks and reflect changes within a few minutes. If an app has not synced for more than **1 hour**:

1. Check whether the app shows **CC-INT-608** and reconnect it.
2. Check **Settings > Developers > Webhooks** for disabled webhooks that belong to the app (**CC-INT-605**).
3. Contact the app developer. CloudCart Support can confirm that CloudCart sent the events, but cannot fix problems inside third-party apps.

## 7. Integration error codes

| Code | Meaning | What to do |
|------|---------|------------|
| CC-INT-601 | API rate limit exceeded (HTTP 429) | Wait for `Retry-After` and use bulk endpoints (§5.3). |
| CC-INT-602 | Invalid or revoked API key (HTTP 401) | Check the key or create a new one (§5.2). |
| CC-INT-603 | API key missing the required scope (HTTP 403) | Add the scope to the key (§5.2). |
| CC-INT-604 | Webhook delivery failed | Endpoint must return 2xx within 10 seconds (§4.3). |
| CC-INT-605 | Webhook disabled after 24 hours of failures | Fix the endpoint and re-enable it (§4.3). |
| CC-INT-606 | Sender domain not verified | Add the DNS records and wait up to 72 hours (§2.3). |
| CC-INT-607 | SMS quota used up | Turn on extra SMS or wait for the next cycle (§3). |
| CC-INT-608 | App connection expired | Reconnect the app (§6.2). |
