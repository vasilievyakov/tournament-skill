# Spec format

One JSON object. `title` and `items` are required.

```json
{
  "title": "Loading indicator for the app",
  "question": "Which indicator looks better in the interface?",
  "format": "single-elimination",
  "lang": "en",
  "blind": true,
  "stage": "dark",
  "stage_height": 220,
  "text_size": "32px",
  "seed": 7,
  "task": "Put the winning indicator into the Spinner component.",
  "source": "design/loaders.md",
  "css": [".ld{width:56px;height:56px}", "@keyframes spin{to{transform:rotate(360deg)}}"],
  "items": [
    { "id": "S1", "label": "Morning starts here", "text": "Morning starts here", "note": "about the ritual" },
    { "id": "L1", "label": "Ring", "html": "<div class=\"ld ring\"></div>" },
    { "id": "P1", "label": "Shop window photo", "image": "shots/window.png", "stage": "light" },
    { "id": "C1", "label": "With reduce", "code": "const sum = xs.reduce((a, b) => a + b, 0)" }
  ]
}
```

## Top-level fields

| Field | What it does | Default |
|---|---|---|
| `title` | page title and tournament name in the result | required |
| `question` | the question the options are compared by | empty |
| `format` | `single-elimination` (up to 64) or `round-robin` (up to 10) | `single-elimination` |
| `lang` | interface language: `en` or `ru` | `ru` |
| `blind` | hide names during duels | `true` |
| `stage` | option stage background: `panel`, `dark`, `light` | `panel` |
| `stage_height` | minimum stage height, px | 260 |
| `text_size` | font size for `text` options, any CSS value | adaptive 20-30px |
| `seed` | number for a repeatable draw; random without it | random |
| `task` | what the agent should do with the winner; copied into the result | none |
| `source` | where the options came from; copied into the result | none |
| `css` | shared CSS for `html` options, a string or an array of strings | none |

## Option

| Field | What it does |
|---|---|
| `id` | unique key; `V1`, `V2`... when missing |
| `label` | name shown in the results and in the JSON |
| `text` | option text; `note` is a small caption under it |
| `html` | option markup; styles come from `css` |
| `image` | path relative to the spec (embedded into the page), URL or data URI |
| `code` | code snippet in monospace |
| `stage` | stage background for this option, overrides the shared one |

Each option has exactly one content field out of `text`, `html`, `image`, `code`.

## Result

```json
{
  "tournament": "...", "question": "...", "format": "single-elimination", "seed": 7,
  "champion": { "id": "S1", "label": "..." },
  "runner_up": { "id": "S4", "label": "..." },
  "ranking": [ { "place": "1", "items": [ { "id": "S1", "label": "..." } ] }, { "place": "3–4", "items": [] } ],
  "matches": [ { "round": 1, "winner": { "id": "S1" }, "loser": { "id": "S2" } } ],
  "why": "the user's reason, if written",
  "task": "from the spec", "source": "from the spec"
}
```

In a round robin, places carry `wins` and there is no `runner_up`: see the second place in `ranking`.
