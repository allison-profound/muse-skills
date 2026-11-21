# Data connections

- A data connection brings an advertiser's data into Meta through datasets and catalogs.

- A dataset carries events, such as purchases, page views and leads, each sent with details about the person and the event that make it more valuable to the advertiser. Datasets take events from:
  - the web, such as ecommerce purchases and site traffic, through the Meta Pixel, the Conversions API or both
  - apps, such as installs and in-app purchases, through the Meta SDK or the Conversions API
  - a CRM, such as a lead changing status, through the Conversions API
  - offline sales, such as point-of-sale purchases, through the Conversions API

- A catalog describes the items an advertiser sells. It improves the quality of ads and reduces setup, since ads can be built from its items.

- A catalog works best connected to a dataset, so events name the items people viewed or bought.

- Data connections rely on external data sources, so they can change or degrade without notice. Never assume a connection exists or works because the advertiser believes it does, an earlier conversation found it healthy, or a related asset exists, such as a catalog or an installed app. Read its current state before relying on it. Recurring monitoring helps keep setups optimal.

- To check an existing connection, first find out what sends its data, such as the platform that runs the website. A connected platform connector, such as Shopify, or a dataset or catalog source that names a partner tells you. When a partner reference covers that technology, follow its monitoring section, which can include a status read of its own, before telling the advertiser the connection works.

## Datasets

### Set up

- A dataset connection comes from one of two methods:
  - a partner integration, where a platform the advertiser uses, such as Shopify or WooCommerce, sends the events out of the box
  - a direct integration, where the advertiser adds the Meta Pixel or the Conversions API to their own code

- Before setting one up, learn what the advertiser wants to connect, such as a website or another system, and what technology runs it. That can indicate whether a partner integration can be used to maintain the connection.

- For a website, find out whether it is a Shopify store by running `shopify meta-app status --website <site>` as [Shopify store setup](/opt/hatch/connectors/shopify/references/meta-ads-shopify-sma.md) describes, before asking the advertiser what it runs on.

- When a partner reference covers that technology, use its instructions:
  - Shopify: [Shopify store setup](/opt/hatch/connectors/shopify/references/meta-ads-shopify-sma.md)

- Otherwise, or when the technology is unknown, use the reference for the channel the events come from:
  - web: [web events](signals-connections-web.md)
  - apps: [app events](signals-connections-app.md)
  - CRM: [CRM events](signals-connections-crm.md)
  - offline sales: [offline events](signals-connections-offline.md)

### Monitor

- A working dataset can degrade: events stop, volume drops or match quality falls. Read its health as the datasets section of [diagnosis](signals-connections-diagnosis.md) describes, and tell the advertiser what changed and what it means for their ads.

- A partner integration can have its own monitoring steps, in addition to the health checks above. When a partner reference covers the advertiser's technology, follow its monitoring section too:
  - Shopify: [Shopify store setup](/opt/hatch/connectors/shopify/references/meta-ads-shopify-sma.md)

### Fix

- Read the dataset's health with [diagnosis](signals-connections-diagnosis.md) before proposing a fix, then use the partner or channel reference for the source that sends its events.

### Improve

- A working dataset can still give ads more to optimize on. Diagnosis shows where, such as missing events, little customer information, or purchases without value and currency.

- Better data pays off when campaigns use it, such as a sales campaign optimizing for purchases once purchase events arrive.

## Catalogs

### Set up

- A catalog connection comes from a partner integration, where the platform syncs the advertiser's items, or from a product feed that Meta fetches on a schedule.

- For a website, check whether it is a Shopify store with `shopify meta-app status --website <site>` before asking what it runs on.

- When a partner reference covers the advertiser's technology, use its instructions:
  - Shopify: [Shopify store setup](/opt/hatch/connectors/shopify/references/meta-ads-shopify-sma.md)

- Otherwise, create the catalog and its product feed as the catalogs section of [write operations](writes.md) describes.

- Connect the catalog to the dataset that sends its events, so those events name its items.

### Monitor

- A working catalog can degrade: its feed stops updating or its items are rejected. Read its health as the catalogs section of [diagnosis](signals-connections-diagnosis.md) describes, and tell the advertiser what changed and what it means for their ads.

- A partner integration can have its own monitoring steps, in addition to the health checks above. When a partner reference covers the advertiser's technology, follow its monitoring section too:
  - Shopify: [Shopify store setup](/opt/hatch/connectors/shopify/references/meta-ads-shopify-sma.md)

### Fix

- Read the catalog's health with [diagnosis](signals-connections-diagnosis.md) before proposing a fix, then use the partner reference or the catalogs section of [write operations](writes.md).
