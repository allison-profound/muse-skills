# Compare and book stays

- Use this guide for a stay request. Add flights, activities or a wider trip plan only when the user wants them.

## Establish dates and occupancy

- Resolve the destination or property, check-in and check-out dates, room count and the guests in each room. A request for one named night can mean a one-night stay, so state that assumption. Use local dates at the destination.

- Get each child's exact age before pricing, because age changes eligibility and rates. Do not search children as adults or guess their ages, and search again when occupancy or ages change.

- Use relevant past stays and stated preferences, the travel profile's included, for location, room and bed, service, budget and payment timing. One stay is not a standing preference, and it never establishes accessibility needs or acceptance of a nonrefundable rate.

- For a broad destination, center the search on the stated purpose, event or known location, and say where you searched. Do not hold back results for a preference questionnaire. With the first shortlist, offer to focus on a neighborhood, office, venue or transit stop, using verified travel times.

## Search promising sources

- Use `muse.connector_search` to find lodging connectors available in this session, and read their docs before using them.
<!-- hotel-sources-only:start -->

<!-- google-hotels-beside-connectors-only:start -->
- [Hotel sources](sources.md) covers which sources to run for the stay, the one step that runs them with the Google Hotels read, and the cards; the rest of this section covers what each search needs.
<!-- google-hotels-beside-connectors-only:end -->
<!-- google-hotels-beside-connectors-off-only:start -->
- [Hotel sources](sources.md) covers which sources to run for the stay, the one step that runs them, and the cards, with the Google Hotels read as the search where no connector covers the stay; the rest of this section covers what each search needs.
<!-- google-hotels-beside-connectors-off-only:end -->
<!-- hotel-sources-only:end -->

- Use browser tasks for interactive searches and confirm a promising rate with the actual seller. Neither a working connector nor a discount label proves the best value.

- Match dates, occupancy, room, bed, meals, cancellation terms and payment timing before comparing prices. A cheaper third-party rate may lose breakfast, status credit, upgrades, flexibility or direct support, and a direct rate is not automatically better.

- For a rental, include cleaning and service fees, deposits, house rules and check-in arrangements, and explain how it differs from a serviced hotel.

## Rank the full stay

- Alongside the total, weigh the amount due now and at the property, the exact room and bed, verified travel time to what matters, cancellation and deposit terms, included meals and parking, useful benefits, and check-in and check-out times.

- A nightly rate alone is not comparable. Keep offers with missing mandatory fees, estimated totals or unknown current cancellation terms out of the bookable shortlist until checked.

- A passed cancellation deadline is not a refundable rate. Never fill a missing fact with the property's reputation, and state the gap when it matters to the choice.

## Show the location and options

- Present the comparison as [booking presentation](/opt/muse/assets/booking/references/presentation.md) describes, with stable option labels. Follow a connector's own result layout when its docs supply one.

- For native result cards from one connector, follow that connector's documented preview size and See all behavior. For text comparisons, follow booking presentation and any applicable connector text-result guidance. Use the comparison table when comparing different sellers, and honor explicit requests for a map.
<!-- hotel-sources-only:start -->

<!-- google-hotels-beside-connectors-only:start -->
- <!-- expedia-hotel-merge-off-only:start -->Expedia's hotels are their own card list and the other connectors' hotels share one<!-- expedia-hotel-merge-off-only:end --><!-- expedia-hotel-merge-only:start -->The connectors' hotels, Expedia's among them, share one card list<!-- expedia-hotel-merge-only:end -->, and the Google Hotels cards follow as one more list when the read finds a lower total or a hotel worth adding, as [Google Hotels read](google-hotels-read.md) describes. A seller's total on those cards is Google's listing until the seller's checkout confirms it.
<!-- google-hotels-beside-connectors-only:end -->
<!-- google-hotels-beside-connectors-off-only:start -->
- <!-- expedia-hotel-merge-off-only:start -->Expedia's hotels are their own card list and the other connectors' hotels share one<!-- expedia-hotel-merge-off-only:end --><!-- expedia-hotel-merge-only:start -->The connectors' hotels, Expedia's among them, share one card list<!-- expedia-hotel-merge-only:end -->. Where no connector covers the stay, the Google Hotels cards are the list, as [Google Hotels read](google-hotels-read.md) describes, and a seller's total on them is Google's listing until the seller's checkout confirms it.
<!-- google-hotels-beside-connectors-off-only:end -->
<!-- hotel-sources-only:end -->

## Complete the chosen reservation

- Once the user picks a rate, continue with its seller and answer questions from that seller's data.
<!-- hotel-sources-only:start -->

- Before booking a stay the user chose from a card list, from the card or in chat, run `/opt/hatch/bin/hotels route --file FILE --hotel-id ID` with the file behind the list (the connector's unchanged search file, the merged file or the Google Hotels card file) and the card's hotel id. Whenever you know which rate the user chose, from the hotel's details or named in chat, add that rate's `--offer-id` and `--rate-id`: without them the hotel's offer in the file is routed, and an Expedia hotel's other rates book by their own terms. It reads the file as saved and contacts no seller. Its `route` says where the stay books: `in_chat` continues with the connector's own booking commands as its doc describes, and `expedia_web`, `agoda_site` and `seller_site` book on that site in a browser task that starts from `booking_url`, through [browser booking](/opt/muse/assets/booking/references/browser-booking.md). `hotels route --help` describes the output. When it answers that the file doesn't list the hotel or the rate (a hotel See all added, or a rate quoted since the search), the booking review's own terms decide the same way, as the connector's doc describes. A stay found on a site with no file behind it books through browser booking as the bullets below describe.
<!-- hotel-sources-only:end -->

- Follow [checkout](/opt/muse/assets/booking/references/checkout.md) for the final refresh. For a stay, look for changes to the room, bed, view, fees, cancellation terms and benefits.

- The final review shows the property and address, dates, occupancy, exact room and rate, full total, payment timing, deposit or card hold, inclusions, benefits, and the cancellation deadline with its timezone.

- Use native checkout only when fresh provider data marks that exact rate as eligible. When a rate needs the provider's own checkout, show its validated link, and continue through it with [browser booking](/opt/muse/assets/booking/references/browser-booking.md) once the user has asked to finish the booking. Never switch property, room or terms to force a particular checkout route.
<!-- hotel-sources-only:start -->

- A stay picked from a Google Hotels card books on the seller the card names, in a browser task from the hotel's Google Hotels page, as [Google Hotels read](google-hotels-read.md) describes.
<!-- hotel-sources-only:end -->

<!-- expedia-payment-readiness-only:start -->
- When native checkout will charge the stay to Link, the connector's validation also checks whether Link can pay, after the guest details, as its docs describe. When it can't, share the setup step it returns before booking. Once Link is ready, continue the same booking from where it stopped, keeping the room and rate the user chose.

<!-- expedia-payment-readiness-only:end -->
- When the seller refuses the card or billing details in native checkout, offer the recovery options the connector returns, or the same property and dates on the seller's website through [browser booking](/opt/muse/assets/booking/references/browser-booking.md).

- When a browser task books the stay, say in its assignment why that website rather than a connector: a member rate, points or status; a better price there; available lodging connectors do not sell the chosen rate; no lodging booking connector is available; a connector booking that failed; or the user asked for that site.

- In the confirmation, include the room, the amount still due at the property and the cancellation deadline, and check the account record when one is available.

<!-- travel-browser-preapproval-only:start -->
## Book on the seller's website

- When the stay books on the seller's site (an Agoda or Google Hotels card, an `expedia_web` rate, a property or booking site Muse found) and `permissions.preapprove` is available and `wallet.list_payment_methods` shows Link connected, with `purchase_preapproval_eligible: true` and a usable card, the user approves the booking before the browser task, and the task books without another card. Follow [approve first](/opt/muse/assets/booking/references/approve-first.md). Without the tool or such a card, or for a booking in the user's own browser (`browser` set to `device`), book as **Complete the chosen reservation** describes, with the approval at checkout, and ask no payment question.

- Signing in carries the guest's status only on the hotel's own site, so the task signs in there with the saved login when the profile lists their program with that chain, and pays with the wallet card unless the profile says the card saved there. A stay sold through another site earns the program's benefits only when that site says so, so claim none there. Two rooms or stays the site books as separate orders follow approve first's **Several bookings**.

- A Google Hotels card shows Google's listing of one seller's total, not the seller's room, payment timing or cancellation terms. Before the review, read them from the seller's page in a research task, as browser booking's **Research offers** describes. A connector's rate already carries its terms.

- `intent` reads like "Book <hotel>, <room and rate>, <dates>, <guests>". `requirements` carry the room, the cancellation terms, payment timing and inclusions. `max_total` is the full stay total including taxes and fees, also for a pay-at-property rate, since the card may be charged later. The task starts from the card's booking page or the rate's validated link, and the confirmation names the cancellation deadline.
<!-- travel-browser-preapproval-only:end -->

