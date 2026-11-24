# Shopping from Facebook Reels

- `post read` is useful for shopping for products found in a Facebook Reel. [Posts](/opt/hatch/connectors/facebook_cli/references/reading-posts.md) explains how to decode share links.

```sh
/opt/hatch/bin/facebook-cli post read --url '<Reel URL>'
```

- to save recommendations as a local shopping catalog file, use `--out '<file>'`

- If the user asks to choose only from products previously returned to the user, filter just those by verified attributes. A missing or unclear attribute isn't a match, and if none fit, say so without starting another search. This comes before the fresh-search paths below.

- If the response reveals a hard requirement, reuse its context for fresh searches rather than filtering recommendations or reading the Reel again.

- For a named product, a product type, or a hard requirement, leave out `--out` and use [Shopping](/opt/muse/skills/shopping/SKILL.md) for fresh searches with every requirement.

```sh
/opt/hatch/bin/facebook-cli post read --url '<Reel URL>'
```

- `shoppable_products` contains detected products. `featured_products` contains system-generated similar-product candidates; this does not mean the creator tagged or recommended those products. Exact matches, current prices and availability need supporting product data.

## Products from the Reel's shopping sheet

- Check the current request's `product_context` attachment. For `data.entrypoint` = `FB__REELS__SHOP_WITH_MUSE_PILL`, `data.params.system_recommended_product_ids` lists the products Facebook recommended in the Reel's shopping sheet. Older app versions send the same list as `tagged_product_ids`; despite that name, the creator didn't tag these products. They may not appear in the Reel, so describe them as products Facebook recommended. If neither list has IDs, follow the Reel workflow above.

- Use these products instead of the `post read --out` recommendations. Look up each ID, and describe products only from the returned details:

```sh
/opt/hatch/bin/shopping product-details --product-id '<id>' --out '<new file>'
```

- In `shopping.resolve_results`, pass each successful lookup's file in `result_paths` and its `product.id` in `selected_ids`, in list order and before any other results. Keep IDs and lookup errors out of replies.

- If none of the products load, say you couldn't load the products Facebook recommended, without error details. If the user asked to choose only from them, stop there. Otherwise, follow the Reel workflow above.

- If the user asks to choose only from the products that loaded, don't search for others. Otherwise, judge from the user's request and requirements whether those products are enough. If not, use [Shopping](/opt/muse/skills/shopping/SKILL.md) to search for more.

## Find products

- When shopping from Reels, prioritize the stated requirements and instructions. Apply relevant saved hard requirements even when the user did not repeat them, and let explicit current instructions override conflicting ones.

- If a required detail is missing, explain what you couldn't verify.

## Use recommendations

- If the user hasn't specified a product, product type, or hard requirement, use the products from `system_recommended_product_ids` or `tagged_product_ids` when the list is not empty. If neither list has IDs, use the recommendations returned by `post read --out`. Do not filter or reorder these recommendations just to match a soft preference.

- For `post read --out` without a hard requirement, `featured_products_status` describes the next step:

  - `available`: pass the file and all `ordered_featured_product_ids`, unchanged and in order, to `shopping.resolve_results`. These recommendations are ready to use without extra searches. The summary provides the context; the file goes directly to the resolver.

  - `unavailable`: the IDs are empty and no catalog was written. Search for detected products through Shopping, or ask what the user wants if there is no target. This status does not mean the Reel could not be read or that creator tags are missing.

## Present products

- Fresh searches use Shopping's catalog and browser sources, or catalog sources only when requested.

- After the searches are complete, combine all usable files and selected IDs in one `shopping.resolve_results` call. Present the results together as shopping cards with corresponding citation markers. File paths and the availability of the optional recommendation list are internal search details; omit them from progress updates and final replies, even if earlier replies or memory mention them.

- Describe the products you identified, and mention only searches you actually ran and matches you actually found. Base creator-tag or link claims on explicit post data rather than earlier replies.

- Before a purchase, verify the offer and use Shopping's price, delivery and checkout checks.
