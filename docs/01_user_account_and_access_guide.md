# CloudCart User Account and Access Guide

**Document ID:** CC-DOC-01 · **Version:** 3.2 · **Last updated:** 2026-10-15

> CloudCart is a fictional product created for the Sun Info Media AI/ML hackathon. All details are invented.

## 1. Overview

CloudCart is a cloud-based e-commerce management platform. Merchants use it to run an online store: manage products and inventory, take payments, and fulfil orders. This guide covers **merchant accounts** (the store owner and staff who sign in to the CloudCart admin). Shopper accounts are covered in Section 8.

## 2. Plans and account limits

| Limit | Starter | Growth | Enterprise |
|-------|---------|--------|------------|
| Monthly price | $29 | $79 | $299 |
| Products | 500 | 10,000 | Unlimited |
| Staff accounts (including Owner) | 2 | 10 | Unlimited |
| Inventory locations | 1 | 5 | 25 |
| API rate limit | 60 requests/min | 300 requests/min | 1,200 requests/min |
| SMS notifications included | None | 1,000/month | 5,000/month |
| Abandoned checkout recovery | No | Yes | Yes |
| Combinable discounts | No | Yes | Yes |
| SAML single sign-on (SSO) | No | No | Yes |
| Support channels | Email | Email, live chat | Email, live chat, phone, dedicated success manager |
| Uptime SLA | None | None | 99.9% monthly |

- Plans are billed monthly in advance. Annual billing gives a 15% discount.
- **Upgrades** take effect immediately. You are charged a prorated amount for the rest of the billing cycle.
- **Downgrades** take effect at the start of the next billing cycle. A downgrade is blocked if the store is over the lower plan's limits (for example, 600 active products when moving to Starter). Archive products or remove staff first.
- Every new store gets a **14-day free trial** of the Growth plan. No card is needed to start the trial, but you must add a payment method before the trial ends or the store is paused.

## 3. Registration and email verification

### 3.1 Creating a store account

1. Go to `https://cloudcart.example/signup`.
2. Enter your email address, a password that meets the requirements in Section 5.1, and a store name.
3. Choose your store country and currency. **The store currency cannot be changed after the first order is placed.**
4. Click **Create store**. A verification email is sent to the address you entered.

Each email address can own only one store. To run several stores from one email address, use an Enterprise plan with multi-store management. Registering an email address that is already in use returns **CC-AUTH-109**.

### 3.2 Email verification

- The verification link is valid for **24 hours**.
- You can request a new link up to **5 times per hour** from the banner in the admin.
- Unverified accounts can sign in and set up products, but **cannot publish the storefront or accept payments** (CC-AUTH-102).
- Accounts that are not verified within **30 days** are deleted automatically.

### 3.3 Verification email not received

1. Wait up to 10 minutes. Delivery is sometimes delayed.
2. Check spam, junk and promotions folders.
3. Add `no-reply@cloudcart.example` to your allowlist. Corporate email filters often quarantine automated messages.
4. Check the email address shown in **Settings > Account** for typos. You can correct it before verification.
5. Request a new link. Only the most recent link works.

## 4. Signing in

### 4.1 Sign-in methods

- Email and password
- Google sign-in
- SAML SSO (Enterprise only). When an Enterprise store enforces SSO, email and password sign-in is disabled for all staff except the Owner. Staff who try it receive **CC-AUTH-108**.

### 4.2 Sessions

- An admin session ends after **8 hours of inactivity**.
- If you select **Remember me**, you stay signed in for **30 days** on that browser.
- Each user can have up to **5 active sessions**. Signing in on a sixth device ends the oldest session.
- An expired session returns **CC-AUTH-111**. Sign in again. Unsaved changes in open forms are lost.

### 4.3 Sign-in from a new location

If CloudCart detects a sign-in from a country the user has not signed in from before, it sends a confirmation email and blocks the session until it is confirmed (**CC-AUTH-110**). The confirmation link is valid for **1 hour**.

## 5. Passwords

### 5.1 Password requirements

- At least **12 characters**
- At least one uppercase letter, one lowercase letter, one number and one symbol
- Must not match any of your **last 5 passwords**
- Must not contain your email address or store name

A password that fails any rule returns **CC-AUTH-107**. The error message lists which rule failed.

### 5.2 Resetting a forgotten password

1. On the sign-in page, click **Forgot password?**
2. Enter your account email address.
3. Open the email and click **Reset password**.
4. Enter and confirm a new password.

Rules:

- The reset link is valid for **30 minutes** and can be used **once**.
- Requesting a new link invalidates all earlier links.
- You can request up to **3 reset emails per hour**.
- An expired or already-used link returns **CC-AUTH-106**. Request a new link.
- Resetting your password signs you out of all other sessions.

### 5.3 Password reset email not received

Follow the same steps as Section 3.3. If you signed up with Google sign-in and never set a password, the reset email still arrives and lets you create a password.

### 5.4 Enforced password rotation

Enterprise Owners can require staff to change passwords every 30 to 365 days in **Settings > Security**. Staff are prompted to change their password at their next sign-in after the period ends.

## 6. Account lockout

### 6.1 Temporary lockout

After **5 failed sign-in attempts within 15 minutes**, the account is locked for **30 minutes** (**CC-AUTH-103**). The user receives an email saying the account was locked. Sign-in attempts during the lockout do not extend it.

### 6.2 Extended lockout

If an account is temporarily locked **3 times within 24 hours**, it moves to an extended lockout (**CC-AUTH-104**). It stays locked until the user resets their password using the steps in Section 5.2. Waiting does not unlock it.

### 6.3 Unlocking staff accounts

- Owners and Admins can unlock a staff account from **Settings > Staff > [user] > Unlock account**.
- The **Owner account** can be unlocked only by a password reset or by CloudCart Support after identity verification (Section 7.4).

## 7. Two-factor authentication (2FA)

### 7.1 Methods

- **Authenticator app** (TOTP). Codes change every **30 seconds**.
- **SMS**. Codes are valid for **10 minutes**.

An invalid or expired code returns **CC-AUTH-105**. If authenticator codes keep failing, set the phone's date and time to update automatically. TOTP codes depend on an accurate clock.

### 7.2 When 2FA is required

- 2FA is optional on Starter and Growth, but strongly recommended.
- On Enterprise, 2FA is **mandatory for Owner and Admin roles**.

### 7.3 Backup codes

When you turn on 2FA, CloudCart generates **10 single-use backup codes**. Store them safely. Generating new codes invalidates the old ones.

### 7.4 Lost 2FA device

1. Sign in with a backup code, then set up 2FA on the new device.
2. If you have no backup codes and you are a staff member, ask the Owner or an Admin to reset your 2FA from **Settings > Staff > [user] > Reset 2FA**.
3. If you are the **Owner** and have no backup codes, contact CloudCart Support. You must provide a government-issued photo ID and the last 4 digits of the card on the store's billing account. Identity verification takes up to **2 business days**.

CloudCart Support will **never** ask for your password or a 2FA code.

## 8. Shopper (customer) accounts

- Shoppers can create an account on the storefront or check out as guests (see CC-DOC-05 §3).
- The shopper password reset link is valid for **60 minutes**.
- After **10 failed sign-in attempts**, a shopper account is locked for **15 minutes**.
- Merchants cannot see or set shopper passwords. A merchant can send an account invitation email from **Customers > [customer] > Send invite**. The invitation is valid for **7 days**.
- **Data deletion requests:** when a shopper asks for their personal data to be erased, the merchant must process it within **30 days** from **Customers > [customer] > Erase personal data**. Order records are kept in anonymised form for tax purposes.

## 9. Staff roles and permissions

| Permission | Owner | Admin | Staff | Viewer |
|------------|:-----:|:-----:|:-----:|:------:|
| View orders, products, customers | Yes | Yes | Yes | Yes |
| Edit products and inventory | Yes | Yes | Yes | No |
| Fulfil and edit orders | Yes | Yes | Yes | No |
| Issue refunds | Yes | Yes | Only if granted | No |
| Manage discounts | Yes | Yes | Only if granted | No |
| Manage staff | Yes | Yes | No | No |
| Manage API keys and webhooks | Yes | Yes | No | No |
| Change billing, plan and payout bank account | Yes | No | No | No |
| Transfer ownership or close the store | Yes | No | No | No |

- Staff invitations are valid for **7 days**. Expired invitations can be resent.
- **Ownership transfer:** go to **Settings > Account > Transfer ownership**. The new owner must already be an Admin and must accept within **7 days**. After the transfer, the previous Owner becomes an Admin.

## 10. Pausing, closing and reactivating a store

Only the Owner can pause or close a store.

- **Pause plan** ($9/month): the storefront shows a password page and cannot take orders. The admin, products and data stay available. You can pause for up to 6 months.
- **Close store:** billing stops at the end of the current cycle. Store data is kept for **90 days**. During that time the Owner can reactivate the store by signing in and choosing a plan. After 90 days, all data is permanently deleted and cannot be recovered.
- Outstanding fees are charged when the store closes. Pending payouts are still paid out on schedule.

## 11. Account error codes

| Code | Meaning | What to do |
|------|---------|------------|
| CC-AUTH-101 | Invalid email or password | Check credentials. Repeated failures lead to lockout (§6.1). |
| CC-AUTH-102 | Email address not verified | Verify the email address (§3.2). |
| CC-AUTH-103 | Account temporarily locked | Wait 30 minutes or ask an Admin to unlock it (§6.1, §6.3). |
| CC-AUTH-104 | Extended lockout: password reset required | Reset the password (§5.2). |
| CC-AUTH-105 | Invalid or expired 2FA code | Check the device clock, use a backup code (§7). |
| CC-AUTH-106 | Password reset link expired or already used | Request a new link (§5.2). |
| CC-AUTH-107 | Password does not meet requirements | See §5.1. |
| CC-AUTH-108 | SSO sign-in required | Sign in through your company's identity provider (§4.1). |
| CC-AUTH-109 | Email address already registered | Sign in or reset the password instead (§3.1). |
| CC-AUTH-110 | New-location sign-in needs confirmation | Click the link in the confirmation email within 1 hour (§4.3). |
| CC-AUTH-111 | Session expired | Sign in again (§4.2). |
