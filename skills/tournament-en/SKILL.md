---
name: tournament-en
description: Pairwise tournament of options. When there are many options and the user cannot pick one, this skill builds a one-off page that shows two options side by side; the user clicks or presses an arrow key for the better one until a winner emerges, and gets a final ranking plus a JSON result for the agent. Works for anything that can be shown: text (names, slogans, headlines), images, HTML and CSS (logos, buttons, animations), code snippets. Use when the user says "let's run a tournament", "pairwise", "head to head", "I can't choose", "help me pick from these", "/tournament", or when there are more than five options and the user hesitates. Not for one or two options (ask in chat) and not for scoring on a scale or labeling data.
---

# Tournament

You run a tournament of options: the user compares options in blind pairs, and the page runs the bracket, computes the ranking and exports the result as JSON. The tournament logic lives in `scripts/build.py` and `assets/template.html`; never hand-write the page, write only the spec.

## When to use

- Three or more options, and the user cannot choose or asks for help choosing.
- The options can be shown: text, image, HTML/CSS, code.
- The decision is a matter of taste or overall feel, easier to sense in a pair than to describe with criteria.

With one or two options, ask in chat. For a score on a scale or for labeling a reference set, use another tool.

## Loop

1. **Collect the options.** Take them from the conversation or files, or generate them if asked. Each option is one object with `id`, `label` and exactly one content field: `text`, `html`, `image` or `code`. Keep options comparable: the same presentation, no hints in the label about which one is "right".
2. **Pick a format.**
   - `single-elimination` (default): a knockout bracket, `n - 1` duels, up to 64 options. Fast but noisy: a strong option can drop out early after an unlucky pairing.
   - `round-robin`: everyone meets everyone, `n(n-1)/2` duels, up to 10 options. Gives a full ranking; use it for up to 6-7 options or when second and third place matter.
   - More than 64 options: pre-filter first, or run several groups and a final among the group winners.
3. **Write the spec** following `references/spec.md` and keep it next to the project, not in a temp folder: `<project>/.tournament/<topic>.json`. Put shared CSS for HTML options into `css`: every option renders in its own shadow DOM, so candidate styles cannot break the page or each other.
4. **Build and open the page:**
   `python3 <skill folder>/scripts/build.py <spec.json> --open`
   The script validates the spec, embeds images and prints the number of duels. Tell the user in one line what is open, how many duels there will be and how to choose (click or ← / →, undo with Z).
5. **The user plays and pastes the JSON** (button "Copy result"). Progress is stored in the browser: the page can be closed and reopened.
6. **Apply the result.** The JSON has `champion`, `runner_up` (knockout), `ranking` with places, all `matches` and `why` if the user wrote a reason. Follow the `task` field if the spec had one. Report briefly: winner, second place, what you did.

## Reading the result

- A knockout winner is the user's decision, not a measurement. If the final was close (the user hesitated, `why` is empty) or the stakes are high, offer a rematch: a round robin among the top 3-4 with a different `seed`.
- In a round robin, a tie for first place means no decision yet: offer a duel between the leaders only.
- Do not retell the whole bracket. What matters is the winner, the runner-up and surprises: an option you thought was strong and that dropped out first.

## Rules

- Blind by default (`blind: true`): duels show "Left" and "Right", names appear only in the results. Turn it off only when the name is part of the option.
- Do not rig the bracket or drop options you dislike: agree on any pre-filtering with the user before the tournament.
- Animated options in a pair start at the same moment; Space restarts both animations.
- The page has no external dependencies and works from a file. Interface language `lang`: `en` or `ru`; set `"lang": "en"` for English.

## Check

`python3 <skill folder>/tests/selftest.py [spec.json ...]` builds pages, plays the tournament in headless Chrome and checks the number of duels, the ranking, undo and the export. Run it after any change to the template or the script.
