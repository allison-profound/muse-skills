# Facebook Pages Publishing

- These commands create, edit, publish, schedule and delete posts on a Page the user manages, either directly or through a saved draft.

## Draft, publish or schedule Posts

```sh
/opt/hatch/bin/facebook-cli pages drafts create --page-id '<page_id>' --text '<exact text, up to 1,024 characters, no leading or trailing spaces>' [--file '<static PNG or JPEG up to 10 MiB, or MP4>' ... up to 80, in post order] [--media-caption '<1-based file index>=<caption>' ...]
```

- `pages drafts create` saves a new post on the Page without publishing it. Use it when the user wants to review or edit the post later, or wants another Page Admin to see it first.

```sh
/opt/hatch/bin/facebook-cli pages drafts show --page-id '<page_id>' --draft-id '<draft_id>'
```

- `pages drafts show` reads a saved draft as it's stored in Facebook, including its text, attachments and their media IDs.

```sh
/opt/hatch/bin/facebook-cli pages drafts edit --page-id '<page_id>' --draft-id '<draft_id>' [--text '<complete replacement text>'] [--media '<kept media ID or file:PATH>' ... in final order | --clear-media | --remove-media-id '<media ID>' ...] [--media-caption '<1-based index in the resulting order>=<caption, empty to clear>' ...]
```

- `pages drafts edit` changes a draft's text, attachments or captions and leaves anything you don't pass as it is.

```sh
/opt/hatch/bin/facebook-cli pages drafts publish --page-id '<page_id>' --draft-id '<draft_id>' --privacy PUBLIC [--scheduled-publish-time <Unix seconds, 10 minutes to 29 days ahead>]
```

- `pages drafts publish` publishes or schedules the saved draft as it is, without keeping a copy. The approval shows the draft's full text and media, so it's the natural last step after the user has reviewed a draft.

```sh
/opt/hatch/bin/facebook-cli pages drafts delete --page-id '<page_id>' --draft-id '<draft_id>'
```

- `pages drafts delete` permanently removes a draft and its attachments. It shows the draft and all its attachments for approval.

```sh
/opt/hatch/bin/facebook-cli pages posts create --page-id '<page_id>' --text '<exact text, up to 1,024 characters, no leading or trailing spaces>' --privacy PUBLIC [--file '<static PNG or JPEG up to 10 MiB, or MP4>' ... up to 80, in post order] [--media-caption '<1-based file index>=<caption>' ...] [--scheduled-publish-time <Unix seconds, 10 minutes to 29 days ahead>]
```

- `posts create` publishes a new post right away, or schedules it, without saving a draft first. It's the quickest route when the user already has the final text and media.

- A Page post whose only media is one MP4 publishes as a Reel. Use `posts create` with one MP4 `--file` to publish or schedule it directly. Use `drafts create` with one MP4 `--file` to save it without publishing. `drafts publish --draft-id` later publishes or schedules that draft as a Reel and takes no `--file`.

```sh
/opt/hatch/bin/facebook-cli pages posts reschedule --page-id '<page_id>' --post-id '<scheduled post more than 5 minutes from publishing>' --scheduled-publish-time <new Unix seconds, 10 minutes to 29 days ahead>
```

- `posts reschedule` moves a scheduled post to a new time.

```sh
/opt/hatch/bin/facebook-cli pages posts cancel-schedule --page-id '<page_id>' --post-id '<scheduled post more than 5 minutes from publishing>'
```

- `posts cancel-schedule` unschedules the post and turns it back into a draft, though a publisher already running may still publish it.

<!-- facebook-prosumers-combined-only:start -->
- A draft can start as text and get its photos or video later through `drafts edit`, so when the user asks for drafts before you schedule, save each with `drafts create` and any media they've given, and say which still need some.

- Before you publish, schedule, reschedule or cancel a scheduled post, show the post, the Page and the weekday, date, time and timezone, and wait for their yes. Read a time the user names in their own timezone, so the time you schedule is the one they approved.

<!-- facebook-prosumers-combined-only:end -->

<!-- facebook-post-editing-only:start -->
## Edit a published post

```sh
/opt/hatch/bin/facebook-cli pages posts edit --page-id '<page_id>' --post-id '<post_id>' --text '<complete replacement text, 1–1024 characters>'
```

- `posts edit` replaces the whole message of a published post. For a partial correction, combine the requested change with the rest of the original message. A Page analytics `caption_excerpt` may be shortened, so ask for the complete replacement text when that is all the available text.

- Attachments and individual media captions stay unchanged. The existing post remains in place.

- An edit receipt returns `page_id`, `post_id` and `post_url`. Show the returned post link and confirm the edit.

- A timeout, malformed receipt or unknown outcome may mean the edit succeeded. Read the same post and compare its text with the requested replacement. If readback leaves the outcome unclear, report it as unconfirmed and ask the user to check Facebook before deciding on another edit.

<!-- facebook-post-editing-only:end -->
## Confirm the outcome

- Only `state: published` confirms publication, `scheduled` means publication is pending, and only `state: deleted` confirms deletion. Show a returned `post_url` as a clickable link.

- A post ID returned with an unknown outcome helps reconcile the attempt but proves neither publication nor a schedule.

- The draft, publish and schedule commands get a fresh request ID in their receipt or error. Use it to investigate that attempt, but it does not make a retry safe.

- After an unknown outcome, a timeout, a disconnect, a malformed receipt or a refusal, ask the user to check the Page, post or draft in Facebook. Don't attempt another write unless the user asks.
