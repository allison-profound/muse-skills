# Social Content Performance

## When they want something written

- For post ideas, what to post next, a series or a plan, read [Social Publishing](/opt/muse/skills/social-publishing/SKILL.md) and write from there, bringing what you've already found so the ideas build on it.

<!-- social-skill-improvements-nov-2026-only:start -->
- For captions and hashtags for an account they manage, including quick ones, read Social Publishing instead of writing from the brief, so the writing matches their voice and facts.

<!-- social-skill-improvements-nov-2026-only:end -->

- Otherwise, for a caption or hashtag request with no analysis question, write from the user's brief and the material they supply, return the draft and stop. Do not fetch account data or establish a reporting period for this branch. The remaining analysis steps apply only to performance questions.

## Scope the question

- For a performance question, identify the network, the account and what the user wants to learn, such as which posts reached the most people, how a launch landed or what to post next. Settle the reporting period and timezone before fetching anything.

- Before you fetch or compare numbers, read the connector doc for each platform you're analyzing, since it says what that platform reports, over what period and how to read it.

- Analyze only accounts the user manages. Take the account from the connector's own account list, ask which one to use when several fit, and stop when a named account is not returned rather than substituting another.

- Comparisons with competitors, peers or industry norms use Social Competitor Analysis, which `muse.skill_search` finds when this session has it. Public figures cannot fill a gap in the user's private metrics.

<!-- social-skill-improvements-nov-2026-only:start -->
- Use the period the user names, or the connector's default.

- Judge results by their goal, like views for reach, saves for useful posts, link clicks for customers or earnings for income, including a goal they shared before, and lead with that number.

<!-- social-skill-improvements-nov-2026-only:end -->

## Gather the evidence

- Retrieve the posts in scope with their publication times and permalinks, then the metrics the question needs. Preserve each connector's returned metric display names exactly rather than replacing them with generic labels or labels from memory.

<!-- social-skill-improvements-nov-2026-only:start -->
- Check which post, account and period each number belongs to before you state it, since people act on these numbers.

<!-- social-skill-improvements-nov-2026-only:end -->

- When you work a number out yourself, use the connector's method and show your work briefly, so they can check it.

- Keep each metric at the level it was returned. Account totals do not describe one post, daily unique-account values do not add up to a unique count across a period, and a missing value is unknown rather than zero.

- Keep metrics with different counting conditions or denominators distinct. Separate organic from paid results and keep follower and non-follower breakdowns when they are returned.

- Use only the account's own data as evidence about its performance. Web results, social search, outside benchmarks and remembered figures do not count.

## Find what actually worked

- Compare like with like, matching format, post age, period and audience basis. Note when a post had paid support or reached an unusual audience.

- Review the complete eligible set before calling a post the best, ranking posts or computing an average. One strong post is an example, not a formula.

- Separate how often a format was used from how well it performed. Do not infer causes, audience intent, sensitive traits or algorithm behavior from a correlation.

<!-- social-skill-improvements-nov-2026-only:start -->
- Rank fairly: equal numbers are ties, and a post with no number for a metric sits out that ranking.

- When different posts lead on different metrics, say who leads on each.

- When they ask how their posts or account are doing, give the declines and weak spots the data shows next to the gains, so the picture is honest.

<!-- social-skill-improvements-nov-2026-only:end -->

## Recommend the next step

- Lead with the answer and support each finding with the values compared. Follow [Presenting social results](references/presenting-results.md) for the format, post labels, links and scope statement.

- When they ask why a number moved or what's working, compare it with the account's own baseline, like the previous period of the same length or its typical post in the same format, and show both numbers.

- Give the reason the data supports and call it likely until the data proves it. When the data leaves the reason open, say so.

- Tie one or two next experiments to the user's objective, with what to measure and when to look again. Promise no outcome.

- When the tools can't show something, like sales, customers, retention or whether the account is restricted, say so plainly, offer the closest measure you have and say what it measures.

- This data can't predict earnings, views or followers, including where a young post will end up. When they ask, or a forecast is tempting, show their past numbers and the period they cover instead.

- Report consent, account-linking and eligibility errors as they are. Do not retry a policy denial or work around it with another tool.

- Analysis does not authorize publishing or changing a campaign. Use [Social Publishing](/opt/muse/skills/social-publishing/SKILL.md) or [Advertising Campaigns](/opt/muse/skills/advertising-campaigns/SKILL.md) when the user wants to act on the findings.

<!-- social-skill-improvements-nov-2026-only:start -->
- Give the next step in the answer itself, sized to what they can do, and put any offer of more help after it, since a question alone leaves them with nothing to try.

- Keep to the numbers they asked about, plus any that cut against your answer. If you call something the best, the lowest, tied, up or down, show the numbers you compared, so the user can follow the logic and check your takeaways.

- If you can't see or share what they asked for, say so and still help as far as you can, with a partial or similar answer, clearly labeled, or a way for them to find out.

<!-- social-skill-improvements-nov-2026-only:end -->

## Available connectors

- [Instagram](/opt/hatch/connectors/instagram/CONNECTOR.md) for the user's posts, owned-post lifetime insights, account insights and metric definitions.

- [Facebook](/opt/hatch/connectors/facebook_cli/CONNECTOR.md) for reactions and comments on personal posts, Page post metrics and managed Page insights<!-- facebook-pages-tranche2-only:start -->, best time to post, content ideas and trends in its niche<!-- facebook-pages-tranche2-only:end -->.

- [Threads](/opt/hatch/connectors/threads/CONNECTOR.md) for the user's posts, post insights, top posts and account insights.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

### When available

- These connectors depend on the user's channel or devices. `muse.connector_search` shows which ones this session has.

- [Upload-Post](/opt/hatch/connectors/upload_post/CONNECTOR.md) for post and platform analytics across the networks connected to Upload-Post.

- [Hootsuite](/opt/hatch/connectors/hootsuite/CONNECTOR.md) for analytics across connected social accounts.

- [vidIQ](/opt/hatch/connectors/vidiq_mcp/CONNECTOR.md) for YouTube channel, video and subscriber analytics.

## Websites

- Open a network's own analytics with `browser.browse` when no connector covers that network, measure or period. Give the task the exact account, period and timezone, and have it return each figure with its metric name and any export it produced.

- [YouTube Studio](https://studio.youtube.com/) for YouTube channel and video analytics.

- [TikTok Studio](https://www.tiktok.com/tiktokstudio/) for TikTok account and post analytics.

- [LinkedIn](https://www.linkedin.com/) for the analytics of company Pages the user administers.

- [Pinterest Analytics](https://analytics.pinterest.com/) for Pin and board performance.

## Alternatives for better results

- Join content results to business outcomes with the user's own website, lead or sales records when they share access. Without that evidence, report engagement as engagement rather than business impact.

- Compare each post with the account's own baseline for the same format rather than with industry averages.

- Offer a follow-up review with `cron.add` when results need time to mature, such as a video's views over its first week.
