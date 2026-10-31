# CloudCart Product Catalog and Inventory Guide

**Document ID:** CC-DOC-02 · **Version:** 2.8 · **Last updated:** 2026-10-15

> CloudCart is a fictional product created for the Sun Info Media AI/ML hackathon. All details are invented.

## 1. Overview

This guide explains how to create and manage products, variants and stock in CloudCart. It also covers how stock levels affect what shoppers can buy. Product limits depend on your plan (see CC-DOC-01 §2).

## 2. Creating a product

### 2.1 Steps

1. Go to **Products > Add product**.
2. Enter a title, description, price and SKU.
3. Upload images.
4. Under **Inventory**, choose whether to track quantity (Section 5).
5. Set the status to **Draft** or **Active** and click **Save**.

### 2.2 Field rules

| Field | Rule |
|-------|------|
| Title | Required. Up to 255 characters. |
| SKU | Must be unique within the store. Up to 64 characters. Letters, numbers, hyphens and underscores only. A duplicate SKU returns **CC-INV-301**. |
| Price | Required. Must be 0 or more. A price of 0 marks the product as free. |
| Compare-at price | Optional. Must be higher than the price. Shown as a crossed-out "was" price. |
| Weight | Required for physical products if you use calculated shipping rates. |
| Description | Up to 50,000 characters. Basic HTML is allowed. Scripts are removed. |

### 2.3 Images

- Up to **20 images** per product.
- Formats: JPG, PNG or WEBP. Maximum **20 MB** per image.
- Recommended size: at least 800 × 800 pixels. Smaller images are accepted but may look blurry when zoomed.
- An unsupported format or oversized file returns **CC-INV-304**.

### 2.4 Product status

| Status | Visible on storefront | Can be purchased | Notes |
|--------|----------------------|------------------|-------|
| Draft | No | No | Default for new products. |
| Active | Yes | Yes, if in stock | Counts toward the plan's product limit. |
| Archived | No | No | Kept in order history and reports. Does **not** count toward the plan's product limit. |

When an Active product would take the store over its plan limit, CloudCart blocks the action and returns **CC-INV-306**. Archive unused products or upgrade the plan.

## 3. Variants and options

- A product can have up to **3 options** (for example size, colour and material).
- A product can have up to **100 variants** (the combinations of option values).
- Each variant has its own SKU, price, weight, image and stock level.
- Going over either limit returns **CC-INV-303**. To sell more combinations, split them across separate products, for example one product per colour.
- Deleting a variant that appears in past orders does not change those orders. The order keeps the variant's name and price as they were at the time of purchase.

## 4. Bulk import and export (CSV)

### 4.1 Import limits

- Up to **10,000 rows** and **15 MB** per file.
- The file must be UTF-8 encoded and comma-separated.
- Required columns: `handle`, `title`, `sku`, `price`, `inventory_quantity`.
- Rows with the same `handle` are imported as variants of one product.

### 4.2 How imports run

1. Go to **Products > Import** and upload the file.
2. Choose whether existing products with the same `handle` should be **overwritten** or **skipped**.
3. The import runs in the background. Most imports of 10,000 rows finish within **15 minutes**.
4. When the import finishes, CloudCart emails a summary to the user who started it. Rows with errors are listed with the row number and reason. Valid rows are still imported.

### 4.3 Common import errors

A file that cannot be read at all returns **CC-INV-302**. Common causes:

- The file was saved as Excel (`.xlsx`) instead of CSV.
- The file uses semicolons as separators. Some spreadsheet apps do this by default in some regions.
- The file is not UTF-8. Characters such as é or ₹ show as `�`.
- A required column header is missing or misspelt.

### 4.4 Export

**Products > Export** creates a CSV of all products or of a filtered list. Exports of more than 5,000 products are emailed as a download link that is valid for **7 days**.

## 5. Inventory tracking

### 5.1 Tracking settings

Each variant has two settings:

- **Track quantity:** CloudCart counts stock and reduces it when orders are placed.
- **Continue selling when out of stock:** allows orders when stock is 0 or less. Stock can then go negative. This is how backorders and pre-orders work.

If **Track quantity** is off, the product is always available and stock is not counted.

### 5.2 When stock changes

| Event | Effect on stock |
|-------|-----------------|
| Item added to cart | No change. Carts do **not** reserve stock. |
| Shopper reaches the payment step | Stock is reserved for **15 minutes** (see CC-DOC-05 §4.2). |
| Order placed and paid | Reserved stock is deducted. |
| Payment fails or times out | Reservation is released. |
| Order cancelled before fulfilment | Stock is restocked automatically. |
| Return received (CC-DOC-03 §7) | Restocked only if the merchant selects **Restock item**. |

### 5.3 Manual adjustments

- Adjust stock from **Products > [product] > Inventory** or **Inventory > Adjust**.
- Every adjustment needs a reason: Received, Correction, Damaged, Theft or loss, or Other.
- If **Continue selling when out of stock** is off, stock cannot be set below 0. Trying to do so returns **CC-INV-305**.
- The full adjustment history is kept for **2 years** under **Inventory > History**.

### 5.4 Storefront sync delay

Stock changes normally appear on the storefront within **60 seconds**. If the storefront still shows an old stock level after **15 minutes**:

1. Check that the change was saved under **Inventory > History**.
2. Clear your browser cache or check the page in a private window.
3. If the stock level is still wrong, contact Support with the SKU and the time of the change. This is treated as a **High** priority issue (CC-DOC-07 §2).

## 6. Inventory locations

- A location is a warehouse, shop or other place where stock is kept. The number of locations depends on the plan (CC-DOC-01 §2). Adding one over the limit returns **CC-INV-307**.
- Each variant has a separate stock level per location.
- Orders are fulfilled from the location with the highest **priority** that has enough stock for the whole order. You set priority in **Settings > Locations**.
- **Transfers:** move stock between locations from **Inventory > Transfers**. Stock is deducted from the source when the transfer is marked **Shipped** and added to the destination when it is marked **Received**. You cannot transfer more than the available stock at the source (**CC-INV-308**).
- A location that still holds stock or has unfulfilled orders cannot be deleted. Move the stock and fulfil or reassign the orders first.

## 7. Low-stock alerts

- The default low-stock threshold is **5 units** per variant. You can set any value from 0 to 1,000 in **Settings > Inventory**, or override it per variant.
- CloudCart emails a daily low-stock digest at **08:00** store time to Owners and Admins, listing every variant at or below its threshold.
- The `inventory.low_stock` webhook fires in real time when a variant reaches its threshold (CC-DOC-06 §4).
- Setting the threshold to 0 sends alerts only when a variant is out of stock.

## 8. Unavailable and out-of-stock products

On the storefront, a product is shown as **Sold out** and cannot be added to the cart when all of these are true:

- **Track quantity** is on,
- available stock is 0 or less, and
- **Continue selling when out of stock** is off.

You can choose to hide sold-out products from collections and search in **Settings > Storefront > Hide sold-out products**. They stay reachable by direct link.

If a shopper reports that a product shows as available but checkout says it is unavailable, they are most likely seeing **CC-CHK-203**. Another shopper reserved or bought the last units. See CC-DOC-05 §6.

## 9. Inventory error codes

| Code | Meaning | What to do |
|------|---------|------------|
| CC-INV-301 | Duplicate SKU | Use a unique SKU (§2.2). |
| CC-INV-302 | CSV import file cannot be read | Check the format, encoding and headers (§4.3). |
| CC-INV-303 | Variant or option limit exceeded | Up to 100 variants and 3 options per product (§3). |
| CC-INV-304 | Image upload failed | JPG, PNG or WEBP up to 20 MB (§2.3). |
| CC-INV-305 | Stock cannot go below zero | Turn on overselling or adjust the quantity (§5.3). |
| CC-INV-306 | Product limit for plan reached | Archive products or upgrade (§2.4). |
| CC-INV-307 | Location limit for plan reached | Remove a location or upgrade (§6). |
| CC-INV-308 | Transfer exceeds available stock | Lower the transfer quantity (§6). |
