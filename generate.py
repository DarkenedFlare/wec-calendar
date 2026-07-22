#!/usr/bin/env python3
"""
Builds docs/wec.ics from every YAML file in data/.

Two event shapes are supported per round:
  - Rounds with a `sessions:` list get one VEVENT per session
    (Free Practice 1/2/3, Qualifying, Hyperpole, Race), with real
    local start times converted to UTC.
  - Rounds with `past_event: true` (or no `sessions:` list) get a
    single all-day VEVENT spanning `start` to `end`.

Add a new season by dropping in a new file like data/2027.yaml
(same shape as data/2026.yaml) - no code changes needed.

Run manually with:  python3 generate.py
CI runs this automatically on every push (see .github/workflows/build.yml).
"""
import glob
import datetime
import yaml

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

DATA_GLOB = "data/*.yaml"
OUTPUT_PATH = "docs/wec.ics"
CALNAME = "WEC Calendar"


def escape(text):
    if text is None:
        text = ""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def load_events():
    events = []
    for path in sorted(glob.glob(DATA_GLOB)):
        with open(path) as f:
            doc = yaml.safe_load(f)
        season = doc["season"]
        for ev in doc["events"]:
            events.append({**ev, "season": season})
    return events


def build_allday_vevent(ev, build_stamp):
    start = datetime.date.fromisoformat(str(ev["start"])).strftime("%Y%m%d")
    end_exclusive = (
        datetime.date.fromisoformat(str(ev["end"])) + datetime.timedelta(days=1)
    ).strftime("%Y%m%d")

    uid = f"wec-{ev['season']}-r{ev['round']:02d}@parker-wec-calendar"
    summary = f"WEC Round {ev['round']}: {ev['name']}"
    location = f"{ev['circuit']}, {ev['location']}"

    desc_parts = [f"FIA WEC {ev['season']} Round {ev['round']} - {ev['name']}."]
    if ev.get("notes"):
        desc_parts.append(ev["notes"])
    description = " ".join(desc_parts)

    return "\n".join([
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{build_stamp}",
        f"DTSTART;VALUE=DATE:{start}",
        f"DTEND;VALUE=DATE:{end_exclusive}",
        f"SUMMARY:{escape(summary)}",
        f"LOCATION:{escape(location)}",
        f"DESCRIPTION:{escape(description)}",
        "END:VEVENT",
    ])


def build_session_vevent(ev, session, index, build_stamp):
    tz = ZoneInfo(ev["timezone"])
    local_start = datetime.datetime.fromisoformat(session["start"]).replace(tzinfo=tz)
    utc_start = local_start.astimezone(datetime.timezone.utc)
    utc_end = utc_start + datetime.timedelta(minutes=session["duration_minutes"])

    dtstart = utc_start.strftime("%Y%m%dT%H%M%SZ")
    dtend = utc_end.strftime("%Y%m%dT%H%M%SZ")

    uid = f"wec-{ev['season']}-r{ev['round']:02d}-s{index:02d}@parker-wec-calendar"
    summary = f"WEC R{ev['round']}: {ev['name']} - {session['name']}"
    location = f"{ev['circuit']}, {ev['location']}"

    desc_parts = [f"FIA WEC {ev['season']} Round {ev['round']} - {ev['name']}."]
    if ev.get("notes"):
        desc_parts.append(ev["notes"])
    desc_parts.append(
        "Times pulled from FIA WEC's own event feed and may be provisional - "
        "reconfirm close to race week."
    )
    description = " ".join(desc_parts)

    return "\n".join([
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{build_stamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{escape(summary)}",
        f"LOCATION:{escape(location)}",
        f"DESCRIPTION:{escape(description)}",
        "END:VEVENT",
    ])


def main():
    build_stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    events = load_events()
    def sort_key(e):
        anchor = e.get("start") or e["sessions"][0]["start"]
        return (e["season"], str(anchor))

    events.sort(key=sort_key)

    vevent_blocks = []
    for ev in events:
        if ev.get("sessions"):
            for i, session in enumerate(ev["sessions"], start=1):
                vevent_blocks.append(build_session_vevent(ev, session, i, build_stamp))
        else:
            vevent_blocks.append(build_allday_vevent(ev, build_stamp))

    vevents = "\n".join(vevent_blocks)

    calendar = "\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Parker//WEC Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{CALNAME}",
        "X-WR-TIMEZONE:UTC",
        "REFRESH-INTERVAL;VALUE=DURATION:P1D",
        "X-PUBLISHED-TTL:P1D",
        "",
        vevents,
        "",
        "END:VCALENDAR",
        "",
    ])

    with open(OUTPUT_PATH, "w") as f:
        f.write(calendar)

    n_events = sum(len(e["sessions"]) if e.get("sessions") else 1 for e in events)
    print(f"Wrote {n_events} calendar entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
