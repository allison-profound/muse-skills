# Cast native hosts

<!-- podcast-designed-voices-only:start -->
Use these steps for an episode whose narration language isn't English, or an English episode in a regional variety (`--language en-SG` for Singapore English or Singlish, `en-IN`, `en-GB`, `en-AU` and the like), once the language is settled and before researching or writing. Host names still follow the name rules in the skill.

1. Run `cast` with the command in the skill, in the same turn you read this file. Add only what the user asked for or clearly implied:
   - `--locale` for a variety, such as `pt-PT` or `ja-KANSAI`;
   - for each host: `--voice NAME=VOICE_ID` for a voice they chose (`current` is your own), `--series-voice NAME=VOICE_ID` for a series host, `--traits NAME=TEXT` only for how the user themselves said a voice should sound, personality words such as "sly" or "grumpy" included (never for traits you infer from a story character's role or personality, since a host with traits skips your saved voices), `--gender NAME=F` or `NAME=M` when a gender is given or implied by the name or role (such as "grandpa"), `--host-language NAME=en` for a bilingual show, and `--accent NAME=TEXT` for a requested accent;
   - a voice name the user gives for a host ("use Helio for the host", "Aria as the co-host") is the voice they chose for that host, not the host's name: pass `--voice NAME=VOICE_NAME` (cast accepts a voice's display name) and name the hosts by the skill's name rules;
   - `--new-voices` when they asked for new voices;
   - for an audio story or drama with several speaking characters: each character (as many as the story needs, narrator included) as `--host`, the main voice first.

2. Pass each entry of the plan's `speakers` to `generate` as `--speaker`, its `locale` as `--language` (so a variety such as `pt-PT` keeps its own native-speech description), and each name in its `no_style` as `--no-style`. When the plan has `choose`, first pick for each listed host the candidate whose description fits the user's traits, and pass it as that host's `--speaker` instead of the one in `speakers`.

3. Tell the user, once each and in one sentence in the conversation's language:
   - when the plan has a `note`, that the audio may sound a little accented;
   - when a host's voice ends up different from what the plan or the user chose, which host changed and why.

4. For a series, record the voice IDs as its cast, and pass them with `--series-voice` for later episodes.
<!-- podcast-designed-voices-only:end -->
