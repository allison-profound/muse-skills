# Meta Ads chart renderer

- `render-chart` draws a line or bar chart locally from returned figures and writes it to a file. Never write chart HTML or SVG yourself.

```sh
/opt/hatch/bin/meta-ads-cli render-chart --chart-json '<json-object>'
```

- `--out-dir` defaults to `workspace/charts`. Never set it to `workspace/your_files`, because chart widgets reject paths in the Library.

## Build the chart object

- The object accepts exactly these keys and rejects any other:
  - `type`, either `line` for a trend or `bar` for comparing periods
  - `title`, naming the object and period as a table caption would, up to 200 characters
  - `metric`, up to 40 characters, and `unit`, one of `currency`, `percent` or `number`
  - `currency`, the account's three-letter ISO code, required with `unit` `currency` and rejected otherwise
  - `x_labels`, 2 to 92 labels of up to 16 characters each
  - `series`, 1 to 8 objects of `{name, values}`, with one value per label and `name` required when there are two or more
  - `reference`, optional, as `{label, value}`

- Each value is the tool's own number as a string, copied exactly without a currency symbol, such as `"1234.50"`. A period with no data is `null`, never `0`, and a series with no values at all is left out.

- Use `reference` only for a returned value, such as the prior period or the advertiser's own target, never an invented benchmark.

## Show the chart

- The command returns a `widget` object whose `kind` is `html_file` and whose `data` holds `path` and `fallback_text`, plus a `full_view` object with its own `path`. Pass that `data` object unchanged as the arguments of `widget.create_html_file_widget`, and never put the full-view path, an image link or a second link to the chart in the answer.

- Make both calls before writing the answer, then place the returned `embed_token` on its own line where the chart belongs. An unplaced token shows nothing, so never describe a chart whose token you did not place.

- One question gets one chart with nothing beside it. When more objects qualify than eight series hold, plot the leading eight on the measure asked about and say how many you plotted out of how many.

- Correct only an input error the renderer reports. If it still fails, or the widget fails, give the figures in a list or table, say once that the chart could not be shown and do not retry.

## Performance-trend report card

- `ads_insights_performance_trend` renders its own interactive report card. On success the tool result already includes a `sandbox_link` (a `sandbox://workspace/.ads-performance/…html` path) and a `_present_ads_performance_card` directive — the report file has already been written for you.
- If the user explicitly asked for **no card** (for example "no card", "don't show the card", "just text"), answer in prose with the decisive figures following the analytical-answer rules in [metrics](metrics.md), and do not place the `sandbox_link` — honor their request. If the user only asked for the numbers in text (for example "just tell me", "in text", "give me the numbers") without ruling out the card, answer in prose but you may still place the `sandbox_link` on its own line below; do not withhold the text they asked for. The rest of this section applies only when the user did not ask for a text answer.
- To show the card, place that `sandbox_link` on its own line as a Markdown link, e.g. `[Ad performance trend](sandbox://workspace/.ads-performance/…html)`. That line becomes the interactive card (one expandable card per ad set or ad, with its metric tiles and a trend chart). For a single level, do not call `render-chart`, `widget.create_html_file_widget`, or `render-performance-trend` for the same data, and do not write the card's HTML yourself.
- The card already shows each ad set's or ad's metric tiles, trend charts, status, objective and percent changes. Do not restate that data in prose — no summary table, no per-ad metric list, no repeating each percent change. Answer at the level the owner asked about and let the card carry the rest: if they ask about the account overall, name the level you actually have (the trend tool has no account-wide total — it covers ad, ad set and campaign) rather than labeling a sub-level figure as the account's trend; do not walk through each campaign, ad set or ad in prose. Below the card, give the takeaway: when the owner is deciding something or asking why results changed or what to do, lead with one specific recommendation grounded in the returned data — the single decisive figure and a next step. When the owner only asked how something is doing or trending, answer in one line with the headline figure at the level they asked and offer to dig deeper (for example "Want me to look into which ads are moving it?") rather than prescribing a step they did not ask for.
- Group performance-trend results by the `ad_account_id` used for each call. Different accounts get separate cards, even when their names match. For an account with one result, post its existing `sandbox_link`, labeled with the account name. If an account is not established, keep its per-call card separate rather than guessing.

- If one account has more than one level or entity (for example an ad set and an ad, from separate `ads_insights_performance_trend` calls), combine only that account's results into one card instead of posting its per-call links:
  - Take each call's own `scorecard` object, add the call's `"ad_account_id"` and a `"section_label"` (e.g. `"Ad set"`, `"Ad"`), and nest them as the `children` of one stack. Preserve the returned account and campaign names; never put different accounts in one stack.
  - Save that JSON with the `write` tool as a file in `workspace/.ads-performance/`, for example `workspace/.ads-performance/combined.json` holding `{"component":"stack","children":[{"component":"table","ad_account_id":"<account-id>","name_header":"Ad set","section_label":"Ad set","rows":[…]},{"component":"table","ad_account_id":"<account-id>","name_header":"Ad","section_label":"Ad","rows":[…]}]}`. Pass the combined scorecard only through this file, not with `--scorecard-json`: it is far larger than one command argument allows, and ad names inside it can contain quotes or shell syntax.
  - Run `meta-ads-cli render-performance-trend --scorecard-json-file combined.json` once (the file name is relative to `workspace/.ads-performance/`). Checking the command's help does not render the card; run it with the saved file.
  - Post the `sandbox_link` it returns for that account. Repeat separately for every other account, so a two-account comparison shows two cards. Each account's combined card renders its levels as labeled sections. If you cannot build a combined JSON or the renderer rejects mixed accounts, use the existing per-call cards without combining accounts.
- If the result has no `sandbox_link` (older data or a render error), fall back to the analytical-answer rules in [metrics](metrics.md): give the decisive figures in prose and do not retry the card.
