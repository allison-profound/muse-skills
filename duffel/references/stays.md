# Duffel hotel stays

- `stay-search`, `stay-rates` and `stay-quote` are hidden from `--help`, so use them as shown here.

- Duffel books rates paid by card, in US or Canadian dollars. Each hotel a search returns comes with its cheapest such rate, and the quote says when it's paid: now or at the hotel.

## Search

- Get the destination's coordinates from `map.geocode`, after loading the `map` namespace with `tool_search.load_tool_namespace`. Pass the destination as the user named it in `--location`.

```sh
/opt/hatch/bin/duffel stay-search --location "PLACE" \
  --latitude LAT --longitude LNG \
  --check-in 2026-12-04 --check-out 2026-12-06 --room 2 > /tmp/hotels-PLACE.json
```

- Pass one `--room` per room: the number of adults, then any child ages after a colon, such as `--room 2:5,9`.

- Optional flags: `--radius-km` (1–20, default 5), `--free-cancellation` to keep only hotels that offer it, and `--limit` (1–10, default 6) for how many hotels to price. A search can take a minute.

- The JSON goes to the file. Stderr lists each hotel with its prices, room, cancellation terms, and the `search_result` and `rate` IDs the next commands take.

- `stay-rates` shows the full details of a rate the search chose, as the search found it. It takes `--search-result` and `--rate` plus the same stay flags, and works for 30 minutes after the search.

## Hotel cards

- To show the hotels as cards, pass the search file unchanged to `travel.create_hotel_results_widget`, with up to four `hotel_id` values in `hotel_ids`. The cards read the hotels, prices and photos from it.
<!-- hotel-sources-only:start -->

- The same file is a `hotels compare --shown duffel=FILE` source when the Google Hotels read reports, as Hotel Booking's [Google Hotels read](/opt/muse/skills/hotel-booking/references/google-hotels-read.md) describes.
<!-- hotel-sources-only:end -->

## Quote

```sh
/opt/hatch/bin/duffel stay-quote --search-result SEARCH_RESULT_ID --rate RATE_ID
```

- Quote the rate the user picked before asking for guest details, so they confirm the price first.

- Read `~/memory/travel/PROFILE.md` before asking for guest details when it exists and this conversation has not read it yet: it holds each guest's loyalty programs and room and bed preferences, which the booking below uses. When it does not exist, the user has no saved preferences yet.

- When the user presses Book on a card, the selection gives the `search_result_id` and `rate_id` to quote.

- The quote has the current price and terms: what's charged now, any amount due at the property, the total, the cancellation terms and the rate's `conditions`. The user needs to see these before booking, including anything that changed since the search.

- A fee paid at the hotel, such as a resort fee, can appear only in `conditions` while the quote's hotel fees are zero (`due_at_property` for a pay-now rate, `fees_at_property` for a guarantee), so the total may not include it.

- `ok: false` with a `code` means the rate can't be booked here, and `error` says why.

- `ok: false` without a `code` means the quote request failed, not that the rate is gone. `retriable: true` means quoting again is safe.

- A quote can be booked for up to 30 minutes.

## Book

```sh
/opt/hatch/bin/duffel book --quote-id QUOTE_ID \
  --booking-json '{"guests":[{"given_name":"GIVEN","family_name":"FAMILY"}],"email":"EMAIL","phone_number":"PHONE"}'
```

- List the lead guest first in `guests`, with no more guests than the search had travelers. The hotel holds the booking under the lead guest.

- `email` and `phone_number` are the lead guest's. The phone needs its `+` country code.

<!-- traveler-profiles-only:start -->
- A saved traveler's guest is `{"traveler_id": "ID"}` with the `id` from `/opt/hatch/bin/duffel travelers`, in place of their names. With a saved traveler as the lead guest, leave out `email` and `phone_number`: the CLI fills them from that traveler's saved details without showing them to you, and the approval says they come from saved traveler details. A value you put in `--booking-json` replaces the saved one, so add only what the user asks to change.

- The lead guest's details go in the secure traveler form, so values you don't already have stay out of this conversation and its transcript. When `missing_for_booking.hotel` lists fields for the lead guest, run `/opt/hatch/bin/duffel traveler-request --purpose hotel --traveler ID` with one `--field` per listed field before booking. For a lead guest who is not saved yet, run it without `--traveler`, with `--field email --field phone` and one `--prefill FIELD=VALUE` for each detail the user already gave you, `relationship` included. Other guests need only their names.

- Each run asks for a secure card in this chat, and a note after the result says whether the card is on screen. When it is, tell the user to add the details in the card and end your reply: the chat continues when they save. When it is not, the command's `next` says what to ask in chat instead. `traveler_details_unavailable` means saved details couldn't be read or used: its `error` names the cause, and its `next` says what to do.
<!-- traveler-profiles-only:end -->

- If the quote names a `loyalty_programme` and the user has a number for it, add it as `loyalty_programme_account_number` in `--booking-json`.

<!-- traveler-profiles-off-only:start -->
- If the quote's `next_step` asks for the account holder's details, add `--customer-email`, `--customer-given-name` and `--customer-family-name`.
<!-- traveler-profiles-off-only:end -->
<!-- traveler-profiles-only:start -->
- When the quote's `next_step` says the account has no Duffel traveler profile yet, follow it. `book` takes the account holder's details from the user's own saved traveler (`relationship: self`), and the `next_step` says which `--customer-*` flags or `traveler-request` to use when that traveler lacks one.
<!-- traveler-profiles-only:end -->

- `book` asks the user to approve, then books with their Link card. A pay-now rate is charged at booking. A guarantee rate charges nothing at booking. The guest pays at the hotel, and the card guarantees the booking, so the hotel can charge it as the rate's terms allow. The approval shows the hotel, dates, rooms, guests, room, amounts and cancellation terms.

- `booking_confirmed` includes the hotel's booking `reference`. `supplier_confirmed_details_pending` means the hotel confirmed the booking and the reference comes later.

- `booking_outcome_unknown` means the booking may exist. Booking the same quote or stay again could book it twice.

- `booking_rejected` and `booking_not_sent` mean nothing was booked. Their `next_action` says what can happen next.

- To cancel a stay, read [cancelling a hotel stay](stay-cancel.md). These commands can't look up or change a stay yet.
