# Deal search

- A deal search looks for the same item and variant for less across merchants, and also looks for current promotions or promo codes at the stores that sell the product.

## Find a deal

- Establish the product's usual price, then research where deals for it or its category appear, such as Newegg for electronics.

- Search thoroughly with `browser.browse` for listings below the usual price, and separately for current sales and coupon or promo codes at the sellers themselves.

## Deal search text

- When applicable, put this in place of `<optional deal search context>`:

```text
Also look for a better price on this exact item and variant. Start with Bing Shopping, opening https://www.bing.com/shop/topics?q= with the exact brand, model and variant as the search, which lists other sellers of the same item with prices. Check the brand's official store and up to 3 other established retailers. Skip a store whose page doesn't load or shows a security check. Count a price only once you've seen it on the seller's own product page, and compare delivered prices including shipping. Report each cheaper offer through browser.report.products. Promotions and codes: Look for current promotions and promo codes for this item. Open the agents.md page for the store the user named, or else the store where you first found the item (the store's domain followed by /agents.md). Only promotion related information and promo codes are useful here. A missing page is normal. Put each code in the summary with its store, terms and where you saw it. For both: leave out savings under 2% or $1, and offers or codes that need an email, an account or a first order.
```

## Run the deal search

- For a product already shown, the browser task cannot see this conversation, so start it with this brief, with the deal search text above in place of `<deal search>`:

```json
{
  "task_id": "new",
  "task": "Find a lower price for this exact item and variant: <brand, model and variant>, currently <price> at <store> (<product URL>). Do not search Amazon. <deal search> Check <store> for promotions and codes. Report cheaper offers from their dedicated product pages, with image_url as the page's primary product image (a direct absolute HTTPS URL), price as the regular price, sale_price only for an actual sale, and availability in_stock only when it can be added to cart. Say in the summary when nothing is cheaper. This is price research only: do not purchase, enter checkout, add items to cart, sign up, or request payment/shipping details."
}
```
