# Tests for the game

Run a local server in the repo root first: `python3 -m http.server 8765`, then:

| Script | What it checks |
|---|---|
| `layout_call.py [size]` | Call screen on 15 screen sizes, with 0/3/8 waiting lines, before and after dispatch and during a broadcast: no cut or covered buttons, address, transcript and questions visible |
| `layout_screens.py` | Start screen, cut-scene, map, units, radio, team card, help request, pause and end screen on 10 sizes |
| `all_scenarios.py` | Plays all incidents correctly from start to finish: each must close, score 70+ and have no broken text |
| `bot_play.py d|m N` | A random player plays N full shifts (computer or phone) and checks units and incidents never get stuck |
| `tap_while_rendering.py` | A tap on a question still counts when the call updates under the finger |
| `perf_phone.py` | Frame time and tap response on a phone with a 4x slower CPU |

Before every release: `python3 tools/make-sw.py` (only changed files are downloaded again by players).
