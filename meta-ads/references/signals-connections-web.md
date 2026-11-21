# Web events

- Websites send events through the Meta Pixel in the browser and the Conversions API from the server. They work best together: the Pixel sees what happens on the page, and the Conversions API reports confirmed events, such as a completed order, that ad blockers and browser limits can hide.

- Websites without a Conversions API setup can miss out on receiving events, degrading advertising performance.

## Set up

- Extend a Pixel or tag manager setup the site already has, because a second Pixel counts every event twice.

- Ground the steps in `ads_get_help_article`.

- If a Meta Pixel is set up with no Conversions API, Meta-enabled Conversions API can be turned on in Events Manager to add resilience with no additional code.

## Fix

- Missing or dropping events usually trace to a page, tag or server path that stopped sending them.

- Events counted twice usually mean the Pixel and the Conversions API send the same event without a shared event ID.

## Improve

- Adding the Conversions API next to the Pixel, sending customer information the advertiser has consent for, adding value and currency to purchases, and sending content IDs that match the catalog's items all give ads more to optimize on.
