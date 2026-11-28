# Book a Duffel offer

- Use this guide once the user picks a complete offer to book. [Uncertain results](recovery.md) covers what follows a timeout, an unknown outcome or a Link action.

## Prepare passengers and seats

- Read `~/memory/travel/PROFILE.md` first when it exists and this conversation has not read it yet: it holds each traveler's seat and cabin preferences and loyalty programs, which the seat proposal and the loyalty question below use. When it does not exist, the user has no saved preferences yet.

- `seat-options --offer-id OFFER` returns bookable seats for each passenger with their `position` (window, aisle or middle), and the flag repeats for a short list of offers. A zero price means no added fee, and an omitted seat is unavailable. Each seat also carries `exit_row` and `over_wing` when they apply, an upper `deck` when the map states one, the airline's `disclosures`, such as limited recline or no window, and each traveler's price in `available_for`. The flight's `cabin` names the class of its bookable seats, or each seat does when they differ. `flights_summary` counts, per flight and in seats (each seat once, whatever the number of travelers), the bookable, free and paid seats, the free ones by position and in exit rows, and gives the paid seats' per-traveler price range when one currency covers them. Flights Duffel returned no seat map for are listed under `segments_without_seat_map`, and a `seat_map_request_failed` result means the request itself failed and availability is unknown. Adjacent seats share a row and section on the same side of the aisle.

- Choose at most one seat per passenger and segment. Repeat `--seat PASSENGER:SEGMENT:SEAT`, with one-based numbers, once per seat, such as `--seat 1:1:28B --seat 2:1:28C`; the CLI reads each flag as one seat.

- When the user picks an offer, run `seat-options` for it and propose a free seat for each traveler on each flight: their saved or stated preference, otherwise a window or aisle, with travelers who fly together side by side. Weigh each seat's facts before choosing. An `exit_row` seat brings extra legroom and the airline's exit-row conditions, so offer it to a traveler who wants legroom and skip it for a child, an infant's adult or anyone a disclosure excludes. Pass over a seat whose `disclosures` say limited recline, no window or a lavatory beside it unless nothing else fits. `over_wing`, `deck` and `cabin` say where it is.

- Name each proposed seat in the review message with its position, what makes it the pick and that it is free, as a choice the traveler can change or decline before validation, and carry their answer into `--seat`. A reply that says nothing about seats keeps the proposed ones, which the approval card then shows. When no free seat fits, when `flights_summary` shows few free seats or none in their preferred position, or when a paid seat fits much better than any free one, name the cheapest paid seat that fits with its price, once, and keep the booking moving without waiting for a seat choice.

- When Duffel returned no seat map for a flight, say so once in that same review message, with the airline assigning that flight's seats at check-in, and go on with the booking here. The airline's website is not a place to look for that flight's seat map or to pick its seats, so no browser task is started for it.

- A `seat_map_request_failed` result is a different case: the request failed, so whether those flights have seats to choose is unknown, and nothing in it says how the airline assigns them. Its `seat_map_status` and `seat_map_error_codes` carry what came back. Say once in that same review message that the seat map could not be read, and keep the booking moving without waiting for a seat choice.

- The fare's own bag allowance is on each flight row. When the user wants more checked bags than it includes, or asks to add one, `bag-options --offer-id OFFER` lists the bags the airline sells with that offer: each traveler's bags per journey, with type, weight limit, how many can be added and the price per bag. An empty list means Duffel sells no extra bags for it, so the airline's site is the place to add them after booking.

- Add each bag with `--bag BAG:QUANTITY` on `validate-booking` and `book`, using `bag` from that list, such as `--bag 1-1.1-checked-23kg:1`. Bag prices are added to the total the user approves, so the user should know each bag and its price before they approve.

<!-- traveler-profiles-off-only:start -->
- When the user picks an offer, call `wallet.list_payment_methods` with `provider: "stripe-link"` and `wallet.get_user_info` in the same turn. Fill the trip email and phone from the conversation, `~/USER.md` and `wallet.get_user_info`. Use the user's own name for a passenger only when the conversation shows the user is flying; each other passenger needs their own legal name. Show the prefilled name, email and phone in your question so the user can correct a name that differs from their ID.
<!-- traveler-profiles-off-only:end -->
<!-- traveler-profiles-only:start -->
- When the user picks an offer, call `wallet.list_payment_methods` with `provider: "stripe-link"`, `wallet.get_user_info` and `/opt/hatch/bin/duffel travelers` in the same turn. `travelers` lists the user's saved travelers, each with an `id`, names, `relationship` (`self` is the user), `saved_fields` and `missing_for_booking`, and leaves their saved details out. Match each passenger to a saved traveler by name or relationship, the user only when the conversation shows the user is flying.
<!-- traveler-profiles-only:end -->
- In the same `wallet.get_user_info` result, `agent_wallet_spend_limits` holds the user's Link limits in minor units. When the offer is in the wallet's `default_spend_request_currency` and its total is above `per_transaction.limit` or the `daily` or `thirty_day` `remaining`, tell the user before collecting details: they can raise the limit in Link, which covers every Link card, or book on the airline's own site. `book` refuses such a purchase before the approval card with `link_spend_limit_exceeded`. When the currency differs or `default_spend_request_currency` is absent, skip this check and let `book` decide.
<!-- duffel-link-at-approval-only:start -->

- Link's connection waits for `book`, which stops before the approval when Link can't pay: collect the traveler details first, and leave Link out of those messages.
<!-- duffel-link-at-approval-only:end -->

<!-- traveler-profiles-off-only:start -->
- Show the chosen trip in that same message, so the traveler can ask for changes before validation: each flight with its date, times and flight number, the cabin and the fare brand exactly as the offer names it, bags, change and refund terms, each proposed seat, and the total. Then ask for what is still missing: usually each traveler's birth date and gender (`m` or `f`), and each traveler's legal given and family name when not already known.<!-- duffel-link-at-approval-off-only:start --> If Link is `not_connected`, ask for what is still missing first, then end that message with Link's connection link (`next_action.markdown`, unchanged), so the user connects while answering.<!-- duffel-link-at-approval-off-only:end -->
<!-- traveler-profiles-off-only:end -->
<!-- traveler-profiles-only:start -->
- Show the chosen trip in that same message, so the traveler can ask for changes before validation: each flight with its date, times and flight number, the cabin and the fare brand exactly as the offer names it, bags, change and refund terms, each proposed seat, and the total.
- Name each saved traveler whose saved profile the booking will use, and leave their details out of your reply. Where this chat shows cards, `validate-booking` puts each one's profile card in it, for the user to check or edit. The account details from `wallet.get_user_info` stay out of your reply too.
- Traveler details go in the secure traveler form, so values you don't already have stay out of this conversation and its transcript. The exceptions are what the form can't take or reach: a passport, the account holder's `--customer-*` details from the chat or the wallet, and details a command's `next` says to ask for in chat, which it does when this chat can show no card or the saved details can't be read.
- For a saved traveler whose `missing_for_booking.flight` lists fields, run `/opt/hatch/bin/duffel traveler-request --purpose flight --traveler ID` with one `--field` per listed field. Other passengers need no `email` or `phone`. For a passenger who is not saved yet, run it without `--traveler`, with `--field born_on --field gender`, adding `--field email --field phone` for the first passenger.
- Add what you already know from the conversation, `~/USER.md` or `wallet.get_user_info` with one `--prefill FIELD=VALUE` per field, such as `--prefill given_name=Dana --prefill email=dana@example.com`, so the card opens filled in for the user to confirm. Any detail the user gave in chat can be prefilled this way, a Known Traveler or redress number included. Prefill `relationship` whenever the user says who the traveler is to them: `self` for the user, `partner` for a wife, husband or partner, or `child`, `parent`, `family`, `friend`, `colleague` or `other`, as in `--prefill relationship=partner --prefill given_name=Alexandra`.
- Each run asks for a secure card in this chat, and a note after the result says whether the card is on screen. When it is, tell the user to add the details in the card and end your reply: the chat continues when they save, and `travelers` shows the new or updated traveler. When it is not, the command's `next` says what to ask in chat instead.<!-- duffel-link-at-approval-off-only:start --> If Link is `not_connected`, end that message with Link's connection link (`next_action.markdown`, unchanged), so the user connects while answering.<!-- duffel-link-at-approval-off-only:end -->
- When every passenger is saved with nothing missing, validate right away without asking for details.
<!-- traveler-profiles-only:end -->

<!-- traveler-profiles-off-only:start -->
- Validation also needs the adult with each lap infant, and passport details only when it asks. The CLI sets `title` from gender and gives every passenger the first passenger's email and phone, so ask for a title or a second contact only when the traveler wants one. Ask for a traveler's loyalty account number as one optional item in that same question when the travel profile lists their program with the airline or a partner that credits it, lists the airline among the ones they fly, or the travel history shows an earlier flight on it. Use a number they already gave, and when they have none, book without it rather than asking again.
<!-- traveler-profiles-off-only:end -->
<!-- traveler-profiles-only:start -->
- Validation also needs the adult with each lap infant, and passport details only when it asks. The CLI sets `title` from gender and gives every passenger the first passenger's email and phone, so ask for a title or a second contact only when the traveler wants one.
- A saved traveler's loyalty accounts come from their profile, and the CLI adds the ones the offer takes. Every flight `traveler-request` card offers loyalty programs as optional, so leave `loyalty_accounts` out of `--field`: a traveler without the number at hand still saves and books. When the traveler's `loyalty_programs` lacks a program and the travel profile lists it with the airline or a partner that credits it, lists the airline among the ones they fly, or the travel history shows an earlier flight on it, tell the user once that they can add it in that traveler's card: their `traveler-request` card when one is shown, otherwise the profile card `validate-booking` shows. Wait for their answer before `book`. When they save it, run `validate-booking` again, so the booking carries the number, and when they have none, book without it rather than asking again.
<!-- traveler-profiles-only:end -->

<!-- traveler-profiles-off-only:start -->
- All traveler details for this booking are for its `validate-booking` and `book` only. Keeping them out of memory, and out of replies apart from the prefilled name, email and phone shown for confirmation, protects the traveler's identity.
<!-- traveler-profiles-off-only:end -->
<!-- traveler-profiles-only:start -->
- A detail a traveler gives in chat for this booking, such as a passport, is for its `validate-booking` and `book` only. Keeping it out of memory and out of replies protects the traveler's identity.
<!-- traveler-profiles-only:end -->

- Put passengers in `data.passengers` in search order:

```json
{
  "data": {
    "passengers": [{
      "given_name": "Legal given name",
      "family_name": "Legal family name",
      "born_on": "1990-01-01",
      "gender": "f",
      "email": "trip-contact@example.com",
      "phone_number": "+14155550123"
    }]
  }
}
```

<!-- traveler-profiles-only:start -->
- A saved traveler's passenger is `{"traveler_id": "ID"}` with the `id` from `travelers`. The CLI fills their saved legal name, birth date, gender, email, phone, and the Known Traveler number, redress number and loyalty accounts the offer takes, without showing them to you. `validate-booking` names the saved Known Traveler and redress numbers the booking carries in `saved_identity_documents`, by passenger and type, so you can tell the user one is on the booking. A field you put beside `traveler_id` replaces the saved one, so add only what the traveler asks to change. An empty `identity_documents` or `loyalty_programme_accounts` list leaves the saved ones out of this booking. The full form above is for a passenger whose details came through chat: this chat can show no card, or the saved details can't be read.
<!-- traveler-profiles-only:end -->

- For a lap infant, add `"accompanying_adult": N` with the adult's one-based position. A required passport goes in the passenger's `identity_documents` array with `type: "passport"`, the number as `unique_identifier`, an uppercase two-letter `issuing_country_code` and `expires_on` as `YYYY-MM-DD`. A Known Traveler Number (TSA PreCheck, Global Entry, NEXUS or SENTRI) or a redress number goes in the same array as `{"type": "known_traveler_number", "unique_identifier": "NUMBER"}` or `{"type": "passenger_redress_number", "unique_identifier": "NUMBER"}`, with no `expires_on`; both are US-issued, so the CLI fills in `issuing_country_code`. Validation refuses the number anywhere else, such as a top-level passenger field. `book` lists the identity documents the order was created with in `identity_documents_on_order`, by passenger and type, so you can tell the user a number is on the booking; act on `identity_document_warning` only when it appears. Identity details come from the traveler, since an empty or invented document makes the booking fail or tickets the wrong person, and a traveler who has not been born cannot be ticketed. For an unborn traveler, booking waits until birth, and later fares, availability and seats are unknown until then.

<!-- traveler-profiles-off-only:start -->
- Add each traveler's loyalty account to their passenger whenever they have one for the airline or a partner program that credits it, as `"loyalty_programme_accounts": [{"airline_iata_code": "DL", "account_number": "ACCOUNT_NUMBER"}]`, with one object per programme. It puts their status and mileage earning on the booking, and a traveler without the number at hand still books. Validation confirms whether the airline supports it, and the user decides whether to drop an account that fails.
<!-- traveler-profiles-off-only:end -->
<!-- traveler-profiles-only:start -->
- Validation confirms whether the airline supports each saved loyalty account. When one fails, the user decides whether to drop it. `"loyalty_programme_accounts": []` beside that traveler's `traveler_id` books without their saved accounts.
<!-- traveler-profiles-only:end -->

- Leave out the fields the CLI owns, which are `id`, `infant_passenger_id`, `user_id`, `type`, `selected_offers`, `services`, `payment` and `payments`.

## Validate and book

```sh
/opt/hatch/bin/duffel validate-booking --offer-id OFFER --booking-json JSON
```

- Validation refreshes the offer and checks travelers, documents, seats and loyalty, without payment or approval. Ask for every `required_missing` and `invalid` item together and rerun until `ready_to_book: true`.
<!-- traveler-profiles-only:start -->
- For a saved traveler, ask for a missing or invalid profile field with `traveler-request` and that `--field`, the same way as above. `passenger_age` is different: the traveler's age on the final flight's departure date differs from the age the offer was searched with, so confirm that age with the user and search again with it, and ask for `born_on` only when they say the saved birth date is wrong. A passport is not part of a saved traveler yet, so ask for one in chat when validation needs it. `traveler_details_unavailable` means their saved details couldn't be read or used: its `error` names the cause, and its `next` says what to do.
<!-- traveler-profiles-only:end -->

<!-- duffel-payment-readiness-only:start -->
<!-- duffel-link-at-approval-off-only:start -->
- Validation also checks whether Link can pay. `payment_setup_required` means `book` would stop for Link setup, even when `ready_to_book` is true. Share its `next_action.markdown` unchanged at the end of the same message that asks for any missing details, so the user sets up Link while answering, and don't run `book` until Link is ready. Keep the offer and booking JSON and follow its `resume`; the user doesn't pick the flight again.
<!-- duffel-link-at-approval-off-only:end -->
<!-- duffel-link-at-approval-only:start -->
- Validation also checks whether Link can pay, and says nothing about it: collect the traveler details first. When Link isn't ready, `book` stops before the approval with the setup step and the same flights for the airline's website, as **Book** describes.
<!-- duffel-link-at-approval-only:end -->
<!-- duffel-payment-readiness-only:end -->

- Treat `selected_offer` as the current itinerary, price, bags and fare terms. Check each slice's `from` and `to` against the chosen airports, and stop if they differ.

<!-- traveler-profiles-off-only:start -->
- Pass the account holder's email and legal name on the first `validate-booking`, using what the user said and filling only missing fields from `wallet.get_user_info`, with `--customer-email`, `--customer-given-name` and `--customer-family-name`, so a first booking needs no extra round for its payment profile. Validation ignores them once a profile is stored. Pass the same three flags to `book` only when validation returned `customer_profile_stored: false`. This profile is the account holder, not a passenger, and it is created only after purchase approval.
<!-- traveler-profiles-off-only:end -->
<!-- traveler-profiles-only:start -->
- A first booking also sets up a payment profile for the account holder, who is the user, not a passenger. The CLI takes their legal name and email from the user's own saved traveler (`relationship: self`), so the three `--customer-*` flags are needed only for what validation lists as missing: `customer_email`, `customer_given_name` or `customer_family_name`. Pass those on `validate-booking` and on `book`, from what the user said and else `wallet.get_user_info`. When neither has them, open the user's own traveler card with `/opt/hatch/bin/duffel traveler-request --purpose profile --field email --prefill relationship=self`, adding `--traveler ID` when their own traveler is saved, or one `--prefill` for each part of their name you know when it is not, and validate again once they save. Validation ignores all of this once a profile is stored (`customer_profile_stored: true`).
<!-- traveler-profiles-only:end -->

- If Link connects before the traveler details arrive, confirm it in one line and wait for them. Once the details are in, validate and `book`; the approval card handles the card choice.

- Book once with the same booking JSON and seats, after Link is connected as [Link by Stripe](/opt/hatch/connectors/stripe-link/CONNECTOR.md) describes. Add `--payment-method-id ID` only for a card the user chose for this purchase. Otherwise, approval preselects the default card or a usable card if none is default. The user can change it there.

```sh
/opt/hatch/bin/duffel book --offer-id OFFER --booking-json JSON --seat 1:1:28B --seat 2:1:28C
```

- `book` revalidates before any payment request. Its single approval covers the itinerary, travelers, seats and fees, fare terms, total, the first-time profile, a one-time card, 3DS and immediate ticketing. When the card shows an "Authorized up to" amount, the airline's final total may be charged up to that amount if it settles slightly above the approved total after the order is sent. Any change to the flight, fare, date, passengers, services or total before payment needs a fresh approval.

- `book` reads the live offer itself, including one whose quote expired, and the approval card shows its current total and fare terms. When they differ from what was last quoted, the card says what changed. If Duffel no longer sells the offer, `book` returns `offer_unavailable` with `next_step: search_again`: search the same route and dates again and let the user choose, since a different flight is a new purchase for them to pick.

- When the price changes after approval, `book` closes that checkout and re-quotes the offer in the same call; see `next_step: requote` in [recovery](recovery.md).

- Held orders, Duffel balance payment, inline cards and raw order APIs are not supported.

<!-- duffel-link-at-approval-off-only:start -->
- If Link is not connected, explain the one-time card and share its connection link.
<!-- duffel-payment-readiness-only:start -->
  When `book` itself stops for Link setup, its `resume` says how to continue: once Link is ready, rerun the same `book` unchanged rather than starting the booking over.
<!-- duffel-payment-readiness-only:end --> For an airline-site fallback, use `browser.browse` and follow `~/docs/chat/payments-and-purchases.md`. Use Wallet for payment or assign browser takeover for the user to enter payment on the merchant site. Do not pass card details in task text. If neither supported route works, stop with the itinerary prepared and say that payment is blocked.
<!-- duffel-link-at-approval-off-only:end -->
<!-- duffel-link-at-approval-only:start -->
- When Link isn't connected or has no card it can use, `book` stops before the approval with a setup step, once the traveler details are in. Ask once, in about 60 words: why Link is needed, in your own words from the stop's `why`, its `next_action.markdown` unchanged, and the airline's website as the other way. Muse is told when Link connects. Then run the same `book` command again.

- When the traveler would rather not connect Link, book the same flights on the airline's website through [browser booking](/opt/muse/assets/booking/references/browser-booking.md), with the approval at checkout, as the stop's `browser_alternative` describes: route the trip again with `flights route --trips MERGED_FILE --offer POINTER --without-duffel` when it came from a merged list, else `duffel route --carriers CODES --without-duffel`, and book from the decision, from its link when there is one. Say in the task why the website: the user chose not to pay through Link. Follow `~/docs/chat/payments-and-purchases.md` there, with browser takeover for the user's own card, and keep card details out of task text.
<!-- duffel-link-at-approval-only:end -->

- Prefer one offer that covers the whole itinerary. Split it into separate bookings only with the user's agreement before the first `book`. Explain that each booking has its own approval, payment and terms, that later offers are not held, and that a later failure can leave earlier tickets booked.

- For a split trip, validate both tickets before booking either, so a price change or missing detail shows up before any purchase. Then book each ticket's `id` with its own `book`.
