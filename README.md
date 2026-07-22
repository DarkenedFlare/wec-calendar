# WEC Calendar Feed

A subscribable `.ics` feed for the FIA World Endurance Championship.
Subscribe once, and your calendar app pulls in updates whenever the
data here changes — no re-importing a file every year.

## One-time setup (about 5 minutes)

1. **Create a new GitHub repo** (public — GitHub Pages needs public
   for a free hosted URL). Name it anything, e.g. `wec-calendar`.

2. **Push these files to it:**
   ```bash
   cd wec-calendar
   git init
   git add .
   git commit -m "Initial WEC calendar feed"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

3. **Enable GitHub Pages:**
   - Go to your repo → **Settings** → **Pages**
   - Under "Build and deployment", set **Source** to `Deploy from a branch`
   - Set **Branch** to `main` and folder to `/docs`
   - Save. GitHub will give you a URL like:
     `https://<your-username>.github.io/<your-repo>/`

4. **Your feed URL** is that address plus `wec.ics`:
   ```
   https://<your-username>.github.io/<your-repo>/wec.ics
   ```

5. **Subscribe in your calendar app:**
   - **Apple Calendar (Mac):** File → New Calendar Subscription → paste the URL
   - **Apple Calendar (iPhone):** Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar → paste the URL
   - **Google Calendar:** Other calendars (+) → From URL → paste the URL
   - **Outlook:** Add calendar → Subscribe from web → paste the URL

   Tip: replacing `https://` with `webcal://` in the URL makes some
   apps recognize it as a subscription automatically when you tap a link.

## Session times: where they come from, and how to refresh them

FIA WEC publishes a real per-event `.ics` export at
`https://www.fiawec.com/en/race/calendar/<race-id>` — that's the
actual source for every practice/qualifying/hyperpole/race time in
`data/2026.yaml`, even though the public race pages still show
"TBC." Treat these as provisional until close to race week.

To refresh a round's times:

1. Find its race page on fiawec.com (e.g. `/en/race/lone-star-le-mans-2026`)
   and grab the numeric ID from the "Add to my calendar" link at the
   bottom of the page.
2. Open `https://www.fiawec.com/en/race/calendar/<that-id>` — it
   returns a raw `.ics` with each session's local start time and
   timezone.
3. Update the matching round's `sessions:` block in `data/2026.yaml`
   with any changed times.
4. Commit and push. (FIA's own DTEND values are inconsistent, so
   this project ignores them and uses standard session lengths
   instead — FP 90min, Qualifying 12min, Hyperpole 10min, Race per
   its published duration. Adjust `duration_minutes` per session if
   you want to override that.)

Known race IDs so far: Prologue 5042, Imola 4948, Spa 4949, Le Mans 4951,
São Paulo 4952, Austin 4953, Fuji 4954, Qatar 4947, Bahrain 4955.

The full 2026 season now has real session-level times throughout —
including the four rounds that already happened (Prologue, Imola,
Spa, Le Mans, São Paulo), which used the site's own post-event
timetable rather than the calendar export. Le Mans has a different
session structure than the other rounds (FP1-4, split Hyperpole
rounds for each class, a warm-up, then the 24-hour race) — see
`data/2026.yaml` for the exact shape if you're adding a similar
24-hour round in a future season.

## Updating the calendar (every year, or whenever dates change)

1. Edit or add a file in `data/` — e.g. copy `data/2026.yaml` to
   `data/2027.yaml` and fill in the new season's rounds.
2. Commit and push to `main`.
3. GitHub Actions automatically re-runs `generate.py` and commits the
   refreshed `docs/wec.ics` — no need to run anything locally.
4. Everyone subscribed sees the update on their calendar app's next
   refresh (usually within a day; refresh intervals vary by app and
   aren't something a feed can force faster).

## Files

- `data/*.yaml` — the actual event data, one file per season. This is
  the only thing you normally need to touch.
- `generate.py` — reads all files in `data/` and builds `docs/wec.ics`.
  Run locally with `python3 generate.py` if you want to preview a
  change before pushing.
- `docs/wec.ics` — the generated feed GitHub Pages serves. Don't hand-edit
  this; it gets overwritten by the build.
- `.github/workflows/build.yml` — the GitHub Action that rebuilds the
  feed automatically on every push to `data/` or `generate.py`.
