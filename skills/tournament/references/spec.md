# Формат spec

Один JSON-объект. Обязательны `title` и `items`.

```json
{
  "title": "Слоган для городской пекарни",
  "question": "Какой слоган лучше встанет на вывеску?",
  "format": "single-elimination",
  "lang": "ru",
  "blind": true,
  "stage": "dark",
  "stage_height": 220,
  "text_size": "32px",
  "seed": 7,
  "task": "Поставь победителя на вывеску и в шапку сайта.",
  "source": "docs/brand/slogans.md",
  "css": [".ld{width:56px;height:56px}", "@keyframes spin{to{transform:rotate(360deg)}}"],
  "items": [
    { "id": "S1", "label": "Утро начинается здесь", "text": "Утро начинается здесь", "note": "про ритуал" },
    { "id": "L1", "label": "Кольцо", "html": "<div class=\"ld ring\"></div>" },
    { "id": "P1", "label": "Фото витрины", "image": "shots/window.png", "stage": "light" },
    { "id": "C1", "label": "Через reduce", "code": "const sum = xs.reduce((a, b) => a + b, 0)" }
  ]
}
```

## Поля верхнего уровня

| Поле | Что делает | По умолчанию |
|---|---|---|
| `title` | заголовок страницы и имя турнира в результате | обязательно |
| `question` | вопрос, по которому сравнивают | пусто |
| `format` | `single-elimination` (до 64) или `round-robin` (до 10) | `single-elimination` |
| `lang` | язык интерфейса: `ru` или `en` | `ru` |
| `blind` | прятать названия в дуэлях | `true` |
| `stage` | фон сцены варианта: `panel`, `dark`, `light` | `panel` |
| `stage_height` | минимальная высота сцены, px | 260 |
| `text_size` | размер текста для `text`-вариантов, любое CSS-значение | адаптивный 20-30px |
| `seed` | число для повторяемой жеребьевки; без него сетка случайная | случайный |
| `task` | что агенту сделать с победителем; попадает в результат | нет |
| `source` | откуда варианты; попадает в результат | нет |
| `css` | общий CSS для `html`-вариантов, строка или массив строк | нет |

## Вариант

| Поле | Что делает |
|---|---|
| `id` | уникальный ключ; без него `V1`, `V2`... |
| `label` | название в итогах и в JSON |
| `text` | текст варианта; `note` — мелкая подпись под ним |
| `html` | разметка варианта; стили из `css` |
| `image` | путь относительно spec (вшивается в страницу), URL или data URI |
| `code` | фрагмент кода моноширинным |
| `stage` | фон сцены для этого варианта, перекрывает общий |

У варианта ровно одно поле содержимого из `text`, `html`, `image`, `code`.

## Результат

```json
{
  "tournament": "...", "question": "...", "format": "single-elimination", "seed": 7,
  "champion": { "id": "S1", "label": "..." },
  "runner_up": { "id": "S4", "label": "..." },
  "ranking": [ { "place": "1", "items": [ { "id": "S1", "label": "..." } ] }, { "place": "3–4", "items": [] } ],
  "matches": [ { "round": 1, "winner": { "id": "S1" }, "loser": { "id": "S2" } } ],
  "why": "текст человека, если написал",
  "task": "из spec", "source": "из spec"
}
```

В круговом турнире у мест есть `wins`, а `runner_up` нет: смотри второе место в `ranking`.
