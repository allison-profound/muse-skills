# Google Flights

- Flight Booking's [Read Google Flights](/opt/muse/skills/flight-booking/references/google-flights-read.md) owns the Google Flights read: when it runs, the browser's assignment (which both address commands print), how its trips are written and merged, and how a tapped trip is routed with `flights route`. This guide covers only what Duffel adds to it. Both Duffel commands here send nothing to Duffel and sell nothing; `--help` lists their flags.

## The address, with Duffel

- `duffel gflights-url` builds the trip's exact Google Flights address like `flights gflights-url`, with one Duffel fact: an airline filter (`airlines`) that keeps only the airlines Duffel can't sell or often prices above their own sites, because Duffel's first list covers the rest. It takes the trip flags **Read Google Flights** lists, `--currency` and `--country` for the trip's currency and the traveler's country as [flight comparison](/opt/muse/skills/flight-booking/references/flights.md) settles them, and `--browser-reader` when the flags describe everything the traveler asked for:

```sh
/opt/hatch/bin/duffel gflights-url --origin SFO --destination JFK --departure-date 2026-12-10 --adults 1 --cabin economy --currency USD --country us --browser-reader
```

- Without `--currency` and `--country` the page prices in the currency Duffel quotes the account in (US dollars, or Canadian dollars for a Canadian account) and that country. Duffel's offers come in that currency too, and `flights merge` matches the page's trips with Duffel's offers only in one currency, so a trip priced in another currency books on its airline's site rather than with Muse; say so when the traveler asks for one.

- Name an airline the traveler asked for with `--airlines`, as its IATA code (`UA` for United), since the filter takes codes; that search stays unmarked for the runtime reader, so the browser reads it and keeps the filter. Add `--all-airlines` only when the traveler asked for nonstop flights or a wider comparison, or when Duffel's search failed or has nothing that meets the request, such as no nonstop when the traveler asked for one; then the browser's narrowed read is too narrow, so send its task an update with the `--all-airlines` address for the same trip. Otherwise leave it off, so the search stays on the airlines that can beat the first list.

- Run Duffel's search in the same step as the browser task, covering every airport, date and cabin the request allows; it takes seconds and its offers join the first list. Duffel's search takes `--max-connections N` for stops, up to two cabins, and no `--seat-infants`:

```sh
/opt/hatch/bin/duffel search --origin SFO --destination JFK --departure-date 2026-12-10 --adults 1 --cabin economy --limit 300 > /tmp/sfo-jfk-duffel.json 2>/tmp/sfo-jfk-duffel.txt
```

- Write the browser's trips with the `currency` `duffel gflights-url` printed, then merge them as Flight Booking's [Merge the sources](/opt/muse/skills/flight-booking/references/merge.md) describes, with Duffel's file under `--duffel` and the connector files of the first merge.

## Duffel and the browser's trips

- `flights merge` matches each browser trip to a Duffel offer on the same flights in the same cabin at about the same price or lower. That trip books with Muse: its row points at the Duffel offer, its price is Duffel's, and the facts the browser didn't report are filled from the offer (`filled_from_duffel`: each direction's fare brand, the bags, and the change and refund terms). Bags are what the fare includes: "0 checked" means a checked bag costs extra, not that checked bags aren't allowed; when neither source states an allowance, it is unknown. When the traveler will check a bag, Duffel's `fare_options` can show a fare on the same flights that includes one.

- A browser trip Duffel didn't match keeps the airline booking policy's route. When its entry has a `duffel_recheck` command, Duffel may still sell those exact flights even though the broad search didn't return them: before booking on the airline's site, run that command into a new file and route the tapped trip again with `flights route --trips MERGED_FILE --offer /offers/N --duffel RECHECK_FILE`. When it now routes to `duffel`, book with Duffel; otherwise continue with the first decision. Run the re-check once per tapped trip.

- When `decision.verify_price` is true, Google Flights' price for this airline often differs from the airline's own: confirm it with Duffel or on the airline's site before calling it the price.

- Pass `--device-browser` to `flights merge` and `flights route` when the browser status lists a device browser (the Chrome extension or the in-app browser) for this message. An airline whose site refuses Muse's cloud browser, such as United, then routes to `airline_site` with `decision.browser` set to `device` instead of a hand-off; follow `decision.instructions` for it.

- `duffel route` is not part of Flight Booking's flows: `flights merge` decides every trip, browser trips included, and `flights route` decides a tapped one again. The command remains only as the older form of the same routing for a browser-only search file.

## Talk about results

- Name the airlines, flights and fares. Duffel, Google Flights, these commands and the policy are intermediaries the traveler never transacts with, so a good reply doesn't name them, including when it says where a fact came from. The traveler chooses flights and sees where each one books.

- A Google Flights price is the price shown at `checked_at`. The airline or Duffel confirms the final price at checkout, as Flight Booking's checkout guidance describes.

## Related skills

- [Flight Booking](/opt/muse/skills/flight-booking/SKILL.md)

- Use `muse.skill_search` to find other skills and `muse.connector_search` to find other connectors.
