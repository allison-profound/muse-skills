# Produce a podcast episode

## Generate the episode

- Choose the host names and synthesis voice IDs with [Cast the hosts](../SKILL.md#cast-the-hosts). In this two-host example, set `HOST_NAME` and `HOST_VOICE_ID` to the main host's name and synthesis voice ID, and `COHOST_NAME` and `COHOST_VOICE_ID` to the co-host's name and synthesis voice ID. Use the same names in the script's speaker labels and the `--speaker` mappings; quote each mapping so names with spaces stay one argument. Voice IDs must be synthesis IDs, not display names, `saved_voice_id` or `profile_id`.

- Run the helper with the script, a title, a description, one `--speaker` per host, the target length in minutes, a cover prompt and the topics file:

```sh
/opt/muse/skills/generate_podcast/scripts/podcast-helper generate \
  --script /tmp/script.txt \
  --title "How the Tides Work" \
  --description "$HOST_NAME and $COHOST_NAME explain how the moon moves the oceans" \
  --speaker "$HOST_NAME=$HOST_VOICE_ID" \
  --speaker "$COHOST_NAME=$COHOST_VOICE_ID" \
  --minutes 6 \
  --cover-prompt "ocean tides under a full moon" \
  --topics-file /tmp/topics.md
```

- Before synthesizing, the helper checks the script's length against `--minutes` (a number or a range such as `5-8`) and its format: speaker tags, unmapped names, text before the first tag, and markup that would be read aloud. When something is off it renders nothing and prints `ok: false` with a one-line `script check:` error. Fix only what it lists and run the same command again.

- Run `generate` with exec's `yield_ms` at 120000. When the render finishes within that wait, deliver the episode in the same reply. A longer render comes back on its own when it finishes; don't promise the user a finish time.

- For another episode in an existing series, pass `--series-id`. Take it from the schedule's body or from the most recent episode in that series in `manifest read`. Use the returned UUIDv4 for new schedules; existing schedules can keep passing their job ID. Without the flag, regenerating an episode with the same slug keeps its stored series ID if it has one; otherwise the helper starts a new series.

- A series groups episodes whether or not they are published. `feed_url` identifies the public feed an episode was published to.

- The helper synthesizes the script, writes `~/workspace/podcasts/<slug>/<slug>.mp3` and records the episode in the catalog. It prints JSON with `episode_id`, `series_id`, `slug`, `path`, `duration_secs` and `cover`. `episode_id` is an opaque UUIDv4 assigned by the catalog on first insertion and preserved when that catalog episode is updated, published or reused. Use it for analytics instead of the title-derived `slug`. `series_id` identifies the series; reuse it for later episodes. When it also published, the JSON adds `feed_url`, `episode_url` and `subscription_links`.

- For a freshly rendered episode, inspect `speakers` for the effective voice IDs and `tts_diagnostics` for substitutions or validation warnings. These TTS fields may be absent when reusing an older episode. If a requested voice became a default, tell the user which voice was used; do not claim the requested voice was honored or change saved preferences.

<!-- podcast-designed-voices-only:start -->
- A private episode needs nothing more. Add `--publish` and `--feed-title` only when publishing is authorized, as [publishing and delivery](publishing.md) explains.

<!-- podcast-designed-voices-only:end -->
<!-- podcast-designed-voices-off-only:start -->
- Add `--publish` and `--feed-title` only when publishing is authorized, as [publishing and delivery](publishing.md) explains.

<!-- podcast-designed-voices-off-only:end -->
- Check [language support](languages.md), including for existing scripts and scheduled episodes. Synthesis follows the conversation's language by default. Pass `--language`, such as `es` or `pt_BR`, only to honor an explicit request, and write the script in that language.

<!-- podcast-designed-voices-only:start -->
- When a saved voice hosts, pass `--language` with the script's language, such as `en`, `es` or `ja`, even if the user didn't ask for a language; this takes precedence over the rule above. Without the flag the language falls back to the app's, so a script in an unsupported language would reach synthesis instead of failing early.

<!-- podcast-designed-voices-only:end -->
- English sounds best. Other languages can come out rough, so tell the user non-English audio may be imperfect, and try another `--speaker` voice when one sounds wrong for the language.

## Add cover art

- Always pass `--cover-prompt` with a short description of the episode's theme. The helper generates square cover art itself, so do not call `media.generate_image` for a cover.

- With `--series-id`, the first episode that passes it generates the series cover and later episodes in the series reuse it. Without it, every episode gets its own art.

- Never pass `--cover-image`. Publishing accepts only generated art or the bundled default, so a published episode with `--cover-image` fails. When the user supplies an image, describe it in `--cover-prompt`.

- The result's `cover_source` says where the cover came from: `generated` for new art, `reused` for the series' existing cover (the helper then ignores `--cover-prompt`), `default` for the bundled default and `existing` for any other image. Describe the cover to the user from that value, and say you generated a cover from their image only when it is `generated`.

- Without a cover prompt, the helper uses the user's avatar or the bundled default. An avatar cover cannot be published.

## Change a cover

- Regenerate the cover through the helper so the catalog points to a new file:

```sh
/opt/muse/skills/generate_podcast/scripts/podcast-helper update-cover \
  --slug <slug> \
  --cover-prompt "starry night over a mountain lake"
```

- Present the new `cover` path it prints. Never copy, move or rename an image over the old cover path, and never present the old path again, because delivered previews and library rows reference it and clients cache by path.

- In a series, `update-cover` changes only that episode. The show cover, the other episodes and later `--series-id` episodes keep the shared cover.

- An episode that is already published keeps its old art in the public feed, and the result says `already_published`. Publishing it again would duplicate it, so cover changes on a published episode stay local.

## Handle a failed render

- When any part of synthesis fails, the helper stops and returns `ok: false` with the error.

- Check [language support](languages.md) before retrying. An unsupported narration language is not a transient failure, even if the tool reports empty/truncated audio or suggests retrying. Briefly explain the podcast limitation, offer three to five supported alternatives and stop this episode's retries.

- For a supported language with a transient backend failure, retry the same command later with the same voices, backing off about 5 minutes, then 10, 30 and 60. Schedule each retry rather than waiting, and tell the user you will deliver the episode once synthesis recovers.

- When the helper returns `generation_trace_id`, pass it as `--retry-generation <generation_trace_id>` on every retry of that generation. Keep that ID across retries; it links the attempts for reliability measurement and does not schedule or perform a retry itself. A new episode or a corrected request starts without this flag.

- If it still fails after the hour-long retry, stop. Cancel the scheduled retry, report the error and suggest trying again later.

- Never swap in a different voice or speech engine to get around a transient failure.

<!-- podcast-designed-voices-only:start -->
- A `designed voice can't be used for podcasts`, `designed voice can't host this podcast` or `podcast language not supported` error does not clear on retry. It says why: the voice service refused that saved voice, its voice file is unusable, the episode's language isn't supported, the saved voice library couldn't be read, or another host's voice is neither a catalog voice nor a saved design. Tell the user why, offer a catalog voice, and generate again with their choice. When the error lists the supported languages and the script is in one of them, generate again with that `--language`.

<!-- podcast-voice-feature-only:start -->
<!-- podcast-voice-design-only:start -->
- When the saved voice itself can't be used, offer a newly designed voice too.

<!-- podcast-voice-design-only:end -->
<!-- podcast-voice-feature-only:end -->
- When that error names a voice the cast plan picked for a host (a `saved`, `library` or `current` host), not one the user asked for, don't ask: run `cast` again with the same arguments plus `--exclude-voice VOICE_ID`, generate with the new plan, and say once in the reply which host's voice changed and why. The helper also remembers the refused voice, so later plans skip it.

<!-- podcast-designed-voices-only:end -->
- A `not allowed to use voiceID` error does not clear on retry, because that voice is not permitted. For a newly chosen cast, select another permitted voice from [Podcast preferred voices](podcast_preferred_voices.json), avoiding IDs already assigned to other speakers. Consult the full catalog only for a user-requested voice or voice characteristics, or when the shortlist has run out of distinct voices. If the rejected voice was explicitly requested or belongs to an established series' cast, explain the problem and ask before changing it. Fix an authentication failure or an invalid request rather than retrying it. [The speech reference](/opt/muse/skills/spoken-audio/references/speech.md) explains how to check voice IDs after an opaque HTTP 500.

## Use the other helper commands

- `manifest read` prints the catalog. `episodes` lists each episode with its `episode_id`, any `series_id`, `slug`, `title`, `path`, `topics`, `cover` and any `feed_url`. `feed` is the show published most recently and `feeds` lists every show.

- `generate-slug --title "<title>"` prints the slug a title produces, which ends with today's date.

- `manifest add-episode` and `manifest update-episode` edit a catalog row by hand. Use them only to repair a record. `generate`, `publish` and `update-cover` keep the catalog consistent on their own.
