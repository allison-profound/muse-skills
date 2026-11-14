# Google Flights

- Google Flights is read in a `browser.browse` task. Two Duffel commands make no network request: `duffel gflights-url` builds the exact search address the browser starts from, and `duffel route` gives each trip the browser found its booking route. They sell nothing, and `duffel gflights-url --help` and `duffel route --help` list their flags.

- Before a user-facing search, read [Flight Booking](/opt/muse/skills/flight-booking/SKILL.md), which compares sources and builds the flight list, together with Duffel's [docs](/opt/hatch/connectors/duffel/CONNECTOR.md).

## Search Google Flights in a browser task

- The browser task takes several minutes. Follow the chat's acknowledgment guidance before it starts.

- Get the trip's exact Google Flights search address with the trip flags described below, `/opt/hatch/bin/duffel gflights-url --origin SFO --destination JFK --departure-date 2026-12-10 --adults 1 --cabin economy`, which prints `search_url`. Add `--return-date` for a round trip.

- Right away, start one `browser.browse` task with `task_id` `new` and `url` set to `search_url`, before Duffel's search, so the browser works while Duffel searches. The browser can't see this conversation, so write its assignment yourself with:
  - **The trip:** route, dates, travelers with ages, cabin, and any limit the traveler set, such as a time of day or nonstop only. The page is already searched for it, so the browser keeps its filters.
  - **The goal:** research only, without buying anything or signing in, and stay on that site. Read up to the number of trips the traveler wants to compare, as complete trips with one total, from the first results page, choosing on both price and travel time. Don't open booking options or seller pages: booking links come from `duffel route`.
  - **Limits:** at most three searches, each read from its first results page only. Wait for each page's results to appear rather than pausing for a fixed time. Don't reload pages: on Google Flights a reload starts the search over and can bring back a bot check, and on some checks a reload hangs for minutes. If the site shows a CAPTCHA or an "unusual traffic" page, stop and report it as blocked without trying to clear it or change environment.
  - **The report, per trip:** the airlines; each flight's number, date, airports and local departure and arrival times; stops and layovers; total duration; the total price for all travelers and its currency; the cabin and fare name or fare code shown; and the bags included, when the site shows them.

- Then, in the same turn, run Duffel's search for the same trip when Duffel is available. It takes seconds, and its offers are the first list:

```sh
/opt/hatch/bin/duffel search --origin SFO --destination JFK --departure-date 2026-12-10 --adults 1 --cabin economy --limit 300 > /tmp/sfo-jfk-duffel.json 2>/tmp/sfo-jfk-duffel.txt
```

- Still in that turn, without waiting for the browser, show Duffel's useful offers as the first list, as Duffel's docs describe, and end the reply by saying in your own words that you're still checking more options in the background, which takes a few more minutes, and will message only if something better turns up. Wait for the browser instead when Duffel has no useful offers or the traveler asked for an airline it doesn't sell, such as United.

- When the traveler chooses a first-list trip while the browser is still searching, let it finish and route its trips before booking. When a trip is marked `better`, suggest it in a sentence or two before booking and let the traveler choose; otherwise go ahead with their choice. When the traveler changes the request, close the old search's window (`browser.windows` with `action` `close` and its `task_id`).

- When the browser reports, write its trips to `/tmp/<route>-browser.json` as `{"currency": "USD", "offers": [...]}`, one offer per trip in the flight-row format from [Flight rows](/opt/muse/skills/flight-booking/references/flight-rows.md) ("Rows from a verified website fare"), with a stable `id` such as `gf_0`. Leave out facts the browser didn't report.

- Then route the trips with Duffel's results, as below. When the first list was shown, follow up only with the routed trips marked `better`; otherwise present one list.

- The trip flags: `--origin` and `--destination` with up to three comma-separated airports, `--departure-date`, `--return-date` for a round trip, `--adults`, one `--child-age` per seated traveler aged 2 to 17 on the final travel date, `--lap-infants`, `--seat-infants`, one `--cabin` (`economy`, `premium_economy`, `business` or `first`), `--max-stops N`, and `--airlines`. Duffel takes `--max-connections N` for stops, up to two cabins, and no `--seat-infants`.

## Route each trip

```sh
/opt/hatch/bin/duffel route --search /tmp/sfo-jfk-browser.json --duffel /tmp/sfo-jfk-duffel.json --out /tmp/sfo-jfk-trips.json > /tmp/sfo-jfk-routes.json
```

- Without Duffel, run `duffel route --search FILE` without `--duffel` or `--out`. With Duffel, `--out` writes the trips again with the facts the browser didn't report filled from the Duffel offer on the same flights at about the same price: each direction's fare brand, the bags, and the change and refund terms. `filled_from_duffel` names what was filled, and the rows `route` writes point at that file.

- Bags are what the fare includes: "0 checked" means a checked bag costs extra, not that checked bags aren't allowed. When neither source states an allowance, it is unknown. When the traveler will check a bag, Duffel's `fare_options` can show a fare on the same flights that includes one.

- `duffel route` gives every offer one route from the airline booking policy, and each entry of `routes` carries its finished flight row in `row`:

| `decision.route` | Meaning | The row |
|---|---|---|
| `duffel` | Duffel sells the same flights at the Google price or within a small margin. | Points at the Duffel offer, with the default "Book with Muse" button. |
| `connector` | The airline's own connector sells it. | The default button. |
| `airline_site` | Book on the airline's website in a visible browser task. | "Book on aa.com", for example. |
| `handoff_link` | Muse can't book this airline. The traveler books it from a link. | "Open on united.com", for example. |

- Use each entry's `row` unchanged in `widget.create_list_widget`, including its `flight_action`, so every row's button matches where it books. `lines` summarize the routes, and `decision.reason` says why, such as `united_booking_unsupported` or `no_duffel_match`.

- `better` lists the trips Duffel didn't match that beat the first list, and each entry's `better` says how: `cheaper` than its cheapest trip by the larger of $20 or 5%, `shorter` than its fastest trip by an hour for no more money, or `no_first_list` when Duffel had no offers. It compares totals as each source states them, so check a cheaper trip's bags against what the traveler needs before calling it better.

- Pass `--prefer airline_site` when the traveler wants to use miles, points, credits or status. The policy applies it to airlines that allow that route.

- Pass `--device-browser` when the browser status lists a device browser (the Chrome extension or the in-app browser) for this message, here and when routing a tapped trip. An airline whose site refuses Muse's cloud browser, such as United, then routes to `airline_site` with `decision.browser` set to `device` instead of a hand-off.

## When the traveler taps a row

- When the traveler taps a row to book it, route it again before acting: `duffel route --search FILE --offer /offers/N`, with `--duffel FILE` when Duffel ran. A tapped Duffel row is the Duffel offer, so follow Duffel's booking guide for it. Follow the returned `decision` and its `instructions` for where to book, whatever the row's button said.

- A tap on a planning list's "Add to plan" adds the flight to the plan; it doesn't start booking. Route the flight when the traveler later chooses to book it.

- When the tapped trip's route entry has a `duffel_recheck` command, Duffel may still sell those exact flights even though the broad search didn't return them. Before booking on the airline's site, run that command into a new file and route the tapped offer again with it: `duffel route --search FILE --offer /offers/N --duffel RECHECK_FILE`. When it now routes to `duffel`, book with Duffel. Otherwise continue with the first decision. Run the re-check once per tapped trip.

- `duffel`: follow [Booking](/opt/muse/skills/flight-booking/references/booking.md) and Duffel's booking guide for the matched Duffel offer.

- `decision.instructions`, when present, says why the airline books where it does and what to avoid, such as no browser checkout. Follow it.

- When `decision.verify_price` is true, Google Flights' price for this airline often differs from the airline's own: confirm it with Duffel or on the airline's site before calling it the price.

- `airline_site`: book the same flights on the airline's website with [browser booking](/opt/muse/assets/booking/references/browser-booking.md) in a visible browser task. Start from `decision.link` when it is present. Without one, find the airline's official website by searching for the airline named in `decision.airline` and confirm the domain belongs to that airline before entering anything; never book through a comparison site or another seller. Confirm the flights, travelers and total there before checkout. `decision.traveler_note`, when present, is what the traveler may be told about why it books there; say it in your own words.

- When `decision.browser` is `device`, follow `decision.instructions`: ask once whether to book it in the traveler's own browser, then start the booking task with `browser` set to `device`. When they'd rather not, handle it like `handoff_link` with the decision's link.

- `handoff_link`: don't start a browser task for this airline. Reply in your own words with what `decision.traveler_note` says, then the `decision.link` to the airline's site as a link the traveler opens (without one, name the airline's official website rather than linking a comparison site), then a short list of what to pick there: each flight with its date and time, the fare shown, the travelers, and any bags or seats they wanted. The traveler hears only what the note says, which may be that Muse can't book this trip rather than the whole airline; `instructions` are for you. The booking is still open: ask the traveler to say when it's booked, and don't call the trip booked until they do.

## Talk about results

- Name the airlines, flights and fares. These commands, Duffel and the policy are internal details; the traveler chooses flights and sees where each one books.

- A Google Flights price is the price shown at `checked_at`. The airline or Duffel confirms the final price at checkout, as Flight Booking's checkout guidance describes.

## Related skills

- [Flight Booking](/opt/muse/skills/flight-booking/SKILL.md)

- Use `muse.skill_search` to find other skills and `muse.connector_search` to find other connectors.
