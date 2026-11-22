# Threads read commands

- These are subcommands of `/opt/hatch/bin/threads-cli`, and each needs `--account-id` from `accounts`. The defaults and limits below come from the CLI, which rejects invalid values before calling Threads.

- Page sizes take 1 to 50. Pass a returned cursor as `--after` only when the request needs more results.

## The user's account

- `profile` reads the user's own Threads profile.

- `activity-feed` reads activity notifications. `--first` (alias `--limit`) defaults to 50. `--category-filter` narrows the feed to `text_post_app_conversations`, `text_post_app_following`, `text_post_app_private_follow_requests`, `text_post_app_mentions`, `text_post_app_replies`, `text_post_app_user_follows`, `text_post_app_quote_posts` or `text_post_app_reposts`.

- `liked-media` and `saved-posts` read the posts the user liked or saved. Both accept `--since`, `--until`, `--sort-order`, `--after` and `--first` (alias `--limit`), which defaults to 10.

```sh
/opt/hatch/bin/threads-cli activity-feed --account-id <account_id> --first 20 --category-filter text_post_app_mentions
/opt/hatch/bin/threads-cli liked-media --account-id <account_id> --since 2026-03-01 --until 2026-03-20 --sort-order asc
/opt/hatch/bin/threads-cli saved-posts --account-id <account_id> --limit 20 --after <cursor>
```

## Insights

- `insights-overview` reads account insights, such as views, likes, quotes, replies, reposts, traffic sources, demographics and clicks on the links in the user's bio. It requires `--start-date` and `--end-date` in YYYY-MM-DD. `--sections` takes a comma-separated subset of `summary`, `views`, `interactions`, `followers`, `demographics`, `profile_links`, `featured_link` and `all`.

- `insights-overview` returns `featured_link_insights`, the clicks on the podcast, podcast episode or newsletter featured on the user's profile. Threads returns it only for a profile that features exactly one of them.

- `post-insights --post-id ID` reads insights for one of the user's posts. Besides its counts, the result has the clicks on each link in the post, its save rate and how that compares with the user's typical post, who saw the post (gender, age, countries and cities) and that audience's top interests and communities. The audience breakdowns stay empty until the post has reached 100 viewers.

- `post-insights` returns `top_outperforming_metric` when the post did better than the user's typical post on follows, profile visits, viewers or views. Its value is `FOLLOWS`, `PROFILE_VISITS`, `VIEWERS` or `VIEWS`: the first of them, in that order, on which the post did better.

- `post-insights --include-ai-summary` adds `ai_summary`, the Meta AI summary of the post's performance that the Threads app shows. It can take around ten seconds. Threads has no summary for some posts, such as those under 100 views, and the result then has no `ai_summary`.

- `top-posts` returns the most-viewed posts and the service's top three most-liked posts between the required `--start-date` and `--end-date`. `--count` sets how many most-viewed posts come back and defaults to 10.

- `insights-overview --time-zone-id` and `top-posts --time-zone-name` default to `America/Los_Angeles`. Pass the user's IANA time zone, such as `Europe/London`, when the dates should follow their calendar.

```sh
/opt/hatch/bin/threads-cli insights-overview --account-id <account_id> --start-date 2026-03-13 --end-date 2026-03-20 --sections followers
/opt/hatch/bin/threads-cli post-insights --account-id <account_id> --post-id <post_id>
/opt/hatch/bin/threads-cli top-posts --account-id <account_id> --start-date 2026-03-13 --end-date 2026-03-20 --count 5
```

## Other profiles

- `user-profile` reads a profile with exactly one of `--user-id`, a numeric user FBID, or `--username`, a handle with or without the `@`. It accepts no profile URL.

- `user-profile --username` returns an empty `profiles` list when the handle does not exist or the account cannot see that profile.

- `profile-threads`, `profile-replies` and `profile-media` read a user's posts, replies and media posts with `--user-id`, `--after` and `--first` (alias `--limit`), which defaults to 20.

- `profile-threads` and `profile-replies` also accept `--since` and `--until`, as unix seconds or a date such as `2026-11-20`. `--since` ends the page at the first older post.

- With `--since`, a reply inside the range keeps the post it answers even when that post is older, and an older pinned post on the first page is left out without ending the page.

- `followers` and `following` read a user's lists with `--user-id`, `--first` and `--after`. `following` defaults to 20 accounts per page.

- `followers` and `following` accept `--since` and `--until`, as unix seconds or a date, only for the account's own lists. Each row then carries `followed_at` in unix seconds.

- On these four commands and `feedback-hub-tab`, `--since` is inclusive and `--until` is exclusive, though a date-only `--until` includes that whole day.

- `--until` leaves out rows at or after that time, so a page can be short or empty while `has_next_page` is true.

```sh
/opt/hatch/bin/threads-cli user-profile --account-id <account_id> --user-id <user_id>
/opt/hatch/bin/threads-cli user-profile --account-id <account_id> --username <username>
/opt/hatch/bin/threads-cli profile-threads --account-id <account_id> --user-id <user_id> --first 10 --after <cursor>
/opt/hatch/bin/threads-cli followers --account-id <account_id> --user-id <user_id> --first 10
/opt/hatch/bin/threads-cli followers --account-id <account_id> --user-id <own_user_id> --since 2026-11-18
```

## Posts and reactions

- `post` reads one post with exactly one of `--url` or `--post-id` (alias `--id`). For a `threads.com` or `threads.net` permalink or share link, pass the original URL unchanged to `--url`. Use `fetch-post-comments` for its replies.

- `fetch-post-comments` (alias `comments`) reads comments for up to 10 posts in `--post-ids`. It accepts `--since`, `--until`, `--sort-order` (default `desc`), `--limit` (alias `--first`, default 50), `--after` and repeated or comma-separated `--author-id`.

- `fetch-post-likers` (alias `likers`) reads likers with the same options, filtered by up to 50 `--reactor-id` values instead of `--author-id`, and without `--hidden-only`.

- `fetch-post-reposts` (alias `reposts`) and `fetch-post-quotes` (alias `quotes`) read a post's reposts and quote posts with the same options as `fetch-post-comments`, without `--author-id` or `--hidden-only`.

- Both return `post_groups[]`, one per post, with `media_id`, `reposts` or `quotes`, `error`, `has_next_page`, `end_cursor` and `total_count`.

- A repost row carries `user_id`, `username`, `name`, `profile_url`, `post_id`, `created_at`, `created_at_ts`, `follows_you` and `follower_count`.

- A quote row carries `quote_post_id`, `quote_url`, `quote_text`, `author_id`, `author_username`, `author_name`, `post_id`, `created_at`, `created_at_ts`, `like_count`, `reply_count`, `author_follows_you` and `author_follower_count`.

- `total_count` is the number of rows when they are the whole time window, which is a first page with no next page. Otherwise it is null.

- On these four commands, `--since` and `--until` take unix seconds or a date such as `2026-11-20`. `--since` is inclusive and `--until` is exclusive, though a date-only `--until` includes that whole day.

- `--sort-order` is `desc`, newest first, or `asc`.

- `--after` pages one post at a time, because one cursor is applied to every post in the call.

- `fetch-post-comments --hidden-only` lists only the replies hidden for everyone. It works only on the account's own posts, and a post the account does not own comes back with an `error` on its group. The time window and paging flags still apply.

- With `--hidden-only`, a page can be short or empty while `has_next_page` is true, and `total_count` is null.

- `fetch-post-likers`, the `like` tab of `feedback-hub-tab` and the like items of `feedback-hub-overview` return only the likers the account may see. A post's author sees all of them. Anyone else does not see accounts with private likes, and on a ghost post sees at most their own like.

- A liker list can be shorter than the post's like count, because private likes, likes on ghost posts and reactions are left out.

- Rows of `fetch-post-likers` and `fetch-post-comments` carry `created_at_ts` in unix seconds.

- `fetch-post-comments` rows also carry `author_username`, `is_direct_reply` and `parent_id`.

- `is_hidden` on a `fetch-post-comments` row is true or false only for a reply the account could hide itself: one on the account's own post that answers the post or one of the account's own replies. It is null everywhere else.

- Post rows of `profile-threads`, `profile-replies`, `profile-media` and `liked-media` carry `repost_count` and `quote_count`.

- `feedback-hub-overview --post-id ID` summarizes a post's like, repost and quote counts. `feedback-hub-tab --post-id ID --tab-type TYPE` pages through the accounts behind one tab, where `--tab-type` is `like`, `repost` or `quote` and `--first` defaults to 20.

- `feedback-hub-tab` accepts `--since` and `--until`, as unix seconds or a date. With `--since` it reads the `like`, `repost` and `quote` tabs newest first and ends the page at the first older item.

- `--sort-type` on both feedback hub commands is `default`, `recent` or `most_recent`.

```sh
/opt/hatch/bin/threads-cli post --account-id <account_id> --url https://www.threads.com/@<username>/post/<shortcode>
/opt/hatch/bin/threads-cli post --account-id <account_id> --post-id <post_id>
/opt/hatch/bin/threads-cli fetch-post-comments --account-id <account_id> --post-ids <post_id>,<post_id> --limit 20 --after <cursor>
/opt/hatch/bin/threads-cli fetch-post-likers --account-id <account_id> --post-ids <post_id> --reactor-id <user_id>
/opt/hatch/bin/threads-cli fetch-post-reposts --account-id <account_id> --post-ids <post_id> --since 2026-11-18
/opt/hatch/bin/threads-cli fetch-post-comments --account-id <account_id> --post-ids <post_id> --hidden-only
/opt/hatch/bin/threads-cli feedback-hub-tab --account-id <account_id> --post-id <post_id> --tab-type repost --first 10
```

## Discovery

- `trends` reads trending topics, with `--first` defaulting to 15.

- `search --query TEXT` searches Threads by keyword and returns the Top tab. `--recent 1` returns the Recent tab instead, `--trend-fbid` digs into a trend from `trends`, and `--first` (default 20) with `--after` pages the results.

- `feed --variant for_you` or `--variant following` reads the For You or Following feed, with `--first` (default 20) and `--after`. `--sort-by top` or `--sort-by recent` applies only to Following.

```sh
/opt/hatch/bin/threads-cli trends --account-id <account_id> --first 10
/opt/hatch/bin/threads-cli search --account-id <account_id> --query "AI news" --recent 1
/opt/hatch/bin/threads-cli search --account-id <account_id> --query "<trend name>" --trend-fbid <trend_fbid>
/opt/hatch/bin/threads-cli feed --account-id <account_id> --variant following --sort-by recent
/opt/hatch/bin/threads-cli feed --account-id <account_id> --variant for_you --after <cursor>
```
