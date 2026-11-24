# Facebook Pages Insights

- These commands show how a Page the user manages is performing, from the whole Page's trend over a time window down to individual posts, so you can answer with Facebook's own numbers.

## Read Page insights and posts

```sh
/opt/hatch/bin/facebook-cli pages account-insights --page-id '<page_id>' [--time-range <LAST_7D, LAST_14D, LAST_28D (the default) or LAST_90D>] [--metrics <follower_count,views,unique_viewers,engagement_including_clicks,profile_visits,new_followers,unfollowers<!-- facebook-creators-metrics-only:start -->,net_followers,engagement<!-- facebook-creators-metrics-only:end --><!-- facebook-pages-tranche2-monetization-only:start --><!-- facebook-pages-tranche2-only:start -->,earnings<!-- facebook-pages-tranche2-only:end --><!-- facebook-pages-tranche2-monetization-only:end --><!-- facebook-creators-metrics-only:start -->,views_by_follower_status,messaging_conversations,published_content,one_minute_video_views,top_hashtag_count,top_post_format,top_reel_length,top_fans,followers_by_age,followers_by_gender,followers_by_country,followers_by_city,followers_by_age_and_gender,audience_interests,audience_format_preferences,published_content_by_type,video_views_by_upload_type<!-- facebook-creators-metrics-only:end --> (default: views,unique_viewers)>]
```

- `pages account-insights` reads the whole Page's metrics over a time window, along with the Page's name. It's the best starting point for "how is my Page doing," because it shows the overall trend before you look at individual posts.

```sh
/opt/hatch/bin/facebook-cli pages posts list --page-id '<page_id>' [--time-range <LAST_7D, LAST_14D, LAST_28D (the default) or LAST_90D>] [--fields <views,unique_viewers,engagements,engagements_including_clicks,clicks,link_clicks,saves<!-- facebook-pages-tranche2-monetization-only:start -->,qualified_views<!-- facebook-pages-tranche2-monetization-only:end --><!-- facebook-creators-metrics-only:start -->,net_follows,negative_feedback,private_shares,interaction_rate,comment_rate,reaction_rate,share_rate,save_rate,video_view_rate,video_watch_time,video_average_watch_time,video_average_percentage_viewed,video_effective_watch_rate,video_completion_rate,video_hide_rate,video_like_through_rate,video_retention_graph,video_relative_retention_graph,views_by_country,views_by_paid_organic,views_by_follower_status,engagement_by_follower_status,views_by_audio_language,views_by_traffic_source,video_views_by_age_and_gender_bucket,share_breakdown<!-- facebook-creators-metrics-only:end --><!-- facebook-pages-tranche2-monetization-only:start --><!-- facebook-pages-tranche2-only:start -->,earnings,earnings_by_program,stars_earnings,unified_program_earnings<!-- facebook-pages-tranche2-only:end --><!-- facebook-pages-tranche2-monetization-only:end --><!-- facebook-creators-metrics-only:start -->,quality_signals<!-- facebook-creators-metrics-only:end --> (default: views,engagements)>] [--limit <1 to 10>] [--cursor '<cursor>']
```

- `pages posts list` returns the Page's posts in the time window in batches, each with its metrics and activity. Keep following the returned `cursor` before you rank posts or sum up the window, so the answer covers every post in it, and if you stop early, say which posts you read.

- For the Page's best posts or for post ideas, pass `--time-range LAST_90D` with the metric that fits the owner's goal, such as `link_clicks` or `saves`, because 28 days often holds only a few posts.

```sh
/opt/hatch/bin/facebook-cli pages posts get --page-id '<page_id>' --post-ids '<up to 10 IDs>' [--fields <views,unique_viewers,engagements,engagements_including_clicks,clicks,link_clicks,saves<!-- facebook-pages-tranche2-monetization-only:start -->,qualified_views<!-- facebook-pages-tranche2-monetization-only:end --><!-- facebook-creators-metrics-only:start -->,net_follows,negative_feedback,private_shares,interaction_rate,comment_rate,reaction_rate,share_rate,save_rate,video_view_rate,video_watch_time,video_average_watch_time,video_average_percentage_viewed,video_effective_watch_rate,video_completion_rate,video_hide_rate,video_like_through_rate,video_retention_graph,video_relative_retention_graph,views_by_country,views_by_paid_organic,views_by_follower_status,engagement_by_follower_status,views_by_audio_language,views_by_traffic_source,video_views_by_age_and_gender_bucket,share_breakdown<!-- facebook-creators-metrics-only:end --><!-- facebook-pages-tranche2-monetization-only:start --><!-- facebook-pages-tranche2-only:start -->,earnings,earnings_by_program,stars_earnings,unified_program_earnings<!-- facebook-pages-tranche2-only:end --><!-- facebook-pages-tranche2-monetization-only:end --><!-- facebook-creators-metrics-only:start -->,quality_signals<!-- facebook-creators-metrics-only:end --> (default: views,engagements)>]
```

- `pages posts get` reads up to 10 posts you already know, with their lifetime metrics. Use it to compare posts the user named, or to fetch metrics `posts list` didn't include, without listing the Page's posts again.

- Each command returns only its default metrics unless you pass `--metrics` or `--fields`. Pass the ones the user asks about, such as `follower_count`, and pass every supported value when the user asks for all of them. Limit any claim about missing data to what you requested.

## Compare with a baseline

Facebook reports each window's total ending now: the last 7, 14, 28 or 90 days. When it also has the same-length period just before, `pages account-insights` returns that metric as `rendered_text` in the form `<this window> vs <the window before> in prior period (<change>)`, with a null `value`.

- Use that comparison as the baseline, since it's Facebook's own count for the same length of time. Give both numbers, the change and the window exactly as returned.

- When a metric comes back without one, work the earlier period out from a window and one twice as long, like LAST_7D and LAST_14D. The longer total minus the shorter one is the earlier period, as long as both reads are for the same Page and metric, in the same timezone, and end on the same date, and say you worked it out from the two totals. If they don't line up, give each window's total with its own dates.

- Subtracting works for counts that add up day by day, like views, engagements, clicks, profile visits, new followers and unfollowers. Viewers count each person once per window and follower count is a snapshot, so give those windows side by side.

- For a 28-day answer with no comparison returned, the 62 days before come from LAST_90D minus LAST_28D. Give them as an average per 28 days, labeled as an average.

- Count the posts in each window, since posting less often is a common reason for lower views. When the Page is newer than the longer window, say it's too new to compare and give its numbers so far.

<!-- facebook-prosumers-combined-only:start -->
- New followers minus unfollowers in one window is the net follower change. Both are counts of follows and unfollows, not follower totals.

<!-- facebook-prosumers-combined-only:end -->

## What the reads can't show

<!-- facebook-prosumers-combined-only:start -->
- The reads have no sales, orders, store visits, bookings or names of the people who saw a post. Say so when asked, and offer the closest measure, like link clicks for people heading to buy, called by its own name.

- `messaging_conversations` counts conversations for the whole Page over its window, so keep it apart from any one post.

- Follows, unfollows and profile visits are Page totals for the window, so tie one to a post only as a likely timing match.

- On Facebook, a post reaches people through their connections, like friends and followers, and through recommendations in Feed and Reels, and only some followers see any one post. So use a follower and non-follower split only when the reads return one<!-- facebook-creators-metrics-only:start -->, like `views_by_follower_status`<!-- facebook-creators-metrics-only:end -->, and otherwise say it isn't available rather than working it out from viewers and followers.

<!-- facebook-prosumers-combined-only:end -->
