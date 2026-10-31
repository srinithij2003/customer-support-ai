# CloudCart Product Documentation Pack

Knowledge base for the **RAG-based customer support** part of the Sun Info Media AI/ML hackathon.

> CloudCart is a **fictional** e-commerce management platform created only for this hackathon. Every rule, limit, price, URL and error code in this pack is invented. Any resemblance to a real product is coincidental. Use this pack as the only source of product knowledge. You do not need any external documentation.

## Documents

| File | Document ID | Covers |
|------|-------------|--------|
| `01_user_account_and_access_guide.md` | CC-DOC-01 | Plans, registration, login, passwords, lockout, 2FA, staff roles, store closure |
| `02_product_catalog_and_inventory_guide.md` | CC-DOC-02 | Products, variants, CSV import, stock tracking, locations, low-stock alerts |
| `03_order_management_and_fulfillment_guide.md` | CC-DOC-03 | Order statuses, cancellation, editing, shipping, tracking, returns |
| `04_payments_refunds_and_payouts_guide.md` | CC-DOC-04 | Payment methods, failed and duplicate payments, refunds, payouts, chargebacks |
| `05_checkout_discounts_and_tax_guide.md` | CC-DOC-05 | Cart, checkout errors, discount codes, shipping zones, tax |
| `06_notifications_and_integrations_guide.md` | CC-DOC-06 | Emails, SMS, webhooks, REST API, rate limits, apps |
| `07_troubleshooting_faq_and_support_policy.md` | CC-DOC-07 | Support priorities, escalation policy, error code index, FAQ |

## Conventions

- **Section numbers** (for example `CC-DOC-04 §5.2`) are stable. Use them when you cite sources in generated answers.
- **Error codes** look like `CC-<AREA>-<NUMBER>`. Areas: `AUTH` (1xx), `CHK` (2xx), `INV` (3xx), `ORD` (4xx), `PAY` (5xx), `INT` (6xx). The full index is in CC-DOC-07 §4.
- **Times** are in the store's configured time zone unless a section says otherwise. "Business days" means Monday to Friday, excluding public holidays.
- If the documentation does not answer a question, the assistant should say so instead of guessing.
