# Demo assets

## Recording the demo GIF

Recommended tools:

| OS | Tool | Notes |
|---|---|---|
| Windows | [ScreenToGif](https://www.screentogif.com/) | Free, built-in editor, exports optimised GIF |
| macOS / Windows | [LICEcap](https://www.cockos.com/licecap/) | Lightweight, records direct to GIF |
| Linux | [Peek](https://github.com/phw/peek) | Simple GUI, GIF/WebM output |

**Suggested settings:**
- Resolution: **1280 × 800 px** (crop to the browser window)
- Duration: **≤ 30 seconds**
- Output file name: `demo/demo.gif`

**Suggested flow to record:**
1. Start the app: `PYTHONPATH=src uvicorn instruct_edit.app:app --reload`
2. Open `http://localhost:8000` in a browser
3. Drag `demo/samples/city_street.jpg` onto the upload panel
4. Type `make it sunset` and click **Edit**
5. Wait for the before/after result to appear
6. Optionally expand the **LLM Reasoning** section to show the JSON

> `demo.gif` is listed in `.gitignore` and should **not** be committed. Upload it
> separately (e.g. via GitHub releases or a direct commit if file size permits).

---

## Sample images

| File | Suggested instruction | Notes |
|---|---|---|
| `city_street.jpg` | `make it sunset` | Tests sky replacement with scene preservation |
| `living_room.jpg` | `turn the wall blue` | Tests colour-change with furniture preservation |
| `mountain_lake.jpg` | `add autumn foliage` | Tests seasonal / colour-grading change |

Images are 800 × 600 px JPEGs sourced from [Picsum Photos](https://picsum.photos) (CC0).

---

## Adding the GIF to the README

Once recorded, the top-level `README.md` already references it:

```markdown
![demo](demo/demo.gif)
```

Then uncomment the GIF reference in the top-level `README.md` (line 12):

```markdown
<!-- add once GIF is recorded: ![demo](demo/demo.gif) -->
```

Change it to:

```markdown
![demo](demo/demo.gif)
```

Then drop the file in `demo/` and push.
