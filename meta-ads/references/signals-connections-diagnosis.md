# Diagnose a data connection

- Datasets and catalogs have different health. Read both when the advertiser has both, because ads built from a catalog depend on the dataset's events matching its items.

- When a partner integration sends the data, such as Shopify shown by a connected Shopify connector, a partner-integrations read or a data source that names it, also follow that partner's monitoring section, which can include a status read of its own, before calling the connection healthy:
  - Shopify: [Shopify store setup](/opt/hatch/connectors/shopify/references/meta-ads-shopify-sma.md)

- Lead with the few findings that matter most for the advertiser's ads, in plain words.

## Datasets

- A dataset's health is whether events arrive, how many, how well they match people, and whether any are counted twice. Read it with the dataset tools in the datasets section of [tool routing](tool-routing.md).

- What to look at:
  - freshness: whether events still arrive, and when the last one came
  - volume: events per day against the advertiser's real activity, and sudden drops
  - match quality: how well events match people, which rises with more customer information, such as email and phone
  - coverage: how much of the advertiser's real activity reaches Meta
  - deduplication: an event sent by both the Pixel and the Conversions API shares one event ID, so it is counted once
  - parameters: value and currency on purchases, and content IDs that match the catalog

## Catalogs

- A catalog's health is whether its feed updates, whether its items are accepted, and whether events match its items. Read it with the catalog health tools in the catalogs section of [tool routing](tool-routing.md).

- What to look at:
  - feed uploads: list the catalog's feeds with `ads_catalog_list_product_feeds`, then read each feed's upload sessions with `ads_catalog_get_product_feed_upload_sessions`, and check whether the latest succeeded and are recent. When the feed list returns no data, say the feed list returned no data, so feed uploads are unchecked; do not say upload sessions or upload history returned no data.
  - items: errors, rejected items and missing details, such as price, availability or images
  - event matching: whether the connected dataset's events name items in the catalog
