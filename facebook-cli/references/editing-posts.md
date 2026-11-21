# Editing Facebook posts

- These commands are useful for editing the message text of posts the user authored on a Facebook profile<!-- facebook-group-posts-only:start --> or in a Group<!-- facebook-group-posts-only:end -->. The existing post and attachments stay in place.

## Find the post

- Use the `post_id` returned in this conversation by `timeline fetch`<!-- facebook-group-posts-only:start -->, `groups posts`<!-- facebook-group-posts-only:end --> or `post read`. If the intended post is unclear, ask the user which date or topic they mean.

- If the user provides a Facebook post link, follow [Reading posts](/opt/hatch/connectors/facebook_cli/references/reading-posts.md) to read or resolve the link and obtain its `post_id`.

- If `post read` command returns a non-empty `mentions` list, editing that post isn't supported.

## Replace the text

```sh
/opt/hatch/bin/facebook-cli post edit --post-id '<returned post ID>' --message '<complete replacement text, 1–1024 characters>'
```

- The command replaces the whole message. For a partial correction, combine the requested change with the rest of the user's original wording. If only an excerpt or media description is available, ask for the complete replacement text.

- Individual media captions are separate from the post's message text and stay unchanged.

- Adding `@name` to the new text doesn't create a mention, and adding mentions isn't supported.

## Confirm the outcome

- An edit receipt returns `post_id` and `post_url`. Show the returned post link and confirm the edit.

- A timeout, malformed receipt or unknown outcome may mean the edit succeeded. Follow [Reading posts](/opt/hatch/connectors/facebook_cli/references/reading-posts.md) to read the same post and compare its text with the requested replacement. If readback leaves the outcome unclear, report it as unconfirmed and ask the user to check Facebook before deciding on another edit.

- If approval was denied or the preflight explicitly refused the edit, report that this attempt made no change.

## Related actions

- [Facebook Pages](/opt/hatch/connectors/facebook_cli/references/pages.md) for editing published posts or drafts on a Page the user manages.
