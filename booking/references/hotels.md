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
- Each connector's hotels are their own card list, and the Google Hotels cards follow as one more list when the read finds a lower total or a hotel worth adding, as [Google Hotels read](google-hotels-read.md) describes. A seller's total on those cards is Google's listing until the seller's checkout confirms it.
<!-- google-hotels-beside-connectors-only:end -->
<!-- google-hotels-beside-connectors-off-only:start -->
- Each connector's hotels are their own card list. Where no connector covers the stay, the Google Hotels cards are the list, as [Google Hotels read](google-hotels-read.md) describes, and a seller's total on them is Google's listing until the seller's checkout confirms it.
<!-- google-hotels-beside-connectors-off-only:end -->
<!-- hotel-sources-only:end -->

## Complete the chosen reservation

- Once the user picks a rate, continue with its seller and answer questions from that seller's data.

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
