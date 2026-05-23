#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import mimetypes
import os
import random
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "3000"))
TENOR_KEY = os.environ.get("TENOR_KEY", "LIVDSRZULELA")
GIF_RESULT_CACHE = {}


GENRES = {
    "tech": [
        ("Deploy Friday", "It worked locally, so obviously production is being dramatic."),
        ("Bug Report", "Steps to reproduce: exist near the codebase."),
        ("AI Pairing", "I asked for a fix and got a philosophical essay plus semicolons."),
        ("Cache Magic", "The app is fast because it is confidently showing yesterday."),
    ],
    "movies": [
        ("Interval Twist", "The hero was actually the loading spinner all along."),
        ("Sequel Energy", "Same plot, bigger budget, louder keyboard clicks."),
        ("Villain Arc", "When the app asks you to update before opening."),
        ("Plot Armor", "That one button no one tests but everyone clicks."),
    ],
    "games": [
        ("Side Quest", "Opened settings for one thing, emerged with a new identity."),
        ("Final Boss", "The Wi-Fi password taped behind the router."),
        ("Achievement", "Clicked the wrong thing and discovered a feature."),
        ("Lag Spike", "My strategy is loading. Please respect the process."),
    ],
    "office": [
        ("Meeting Invite", "This could have been a voice note with confidence."),
        ("Deadline", "Plenty of time left, if we redefine plenty."),
        ("Status Update", "Blocked by reality. ETA depends on reality."),
        ("Spreadsheet Mood", "I came, I filtered, I forgot why."),
    ],
    "school": [
        ("Exam Prep", "Chapter one: confidence. Chapter two: panic."),
        ("Group Project", "Everyone contributed vibes."),
        ("Homework", "Due tomorrow means started tomorrow, spiritually."),
        ("Attendance", "Present in body, buffering in mind."),
    ],
    "sports": [
        ("Comeback Plan", "Down by 20, but the playlist says we believe."),
        ("Coach Mode", "My tactic is shouting useful words randomly."),
        ("Fitness Tracker", "Recorded 4,000 steps searching for motivation."),
        ("Replay Review", "After careful analysis, still blaming the referee."),
    ],
    "food": [
        ("Snack Logic", "A small bite became a full product launch."),
        ("Recipe Step", "Add salt to taste. My taste is chaos."),
        ("Delivery ETA", "Five minutes away since the invention of time."),
        ("Diet Plan", "Starting after this very important research meal."),
    ],
    "travel": [
        ("Packing", "Three outfits for one day, zero chargers for survival."),
        ("Airport Mode", "Arrived early just to sprint professionally later."),
        ("Road Trip", "Playlist ready, route questionable, snacks approved."),
        ("Hotel Wi-Fi", "Connected, but emotionally unavailable."),
    ],
    "family": [
        ("Family Tech Support", "I touched one setting and became IT department."),
        ("Relative Question", "What do you do? Short answer: complicated."),
        ("Photo Time", "One normal picture after 43 negotiations."),
        ("Dinner Table", "Breaking news: everyone has a strong opinion."),
    ],
    "random": [
        ("Tiny Crisis", "Opened one tab. Now conducting a life audit."),
        ("Inbox Zero", "A beautiful myth from ancient productivity folklore."),
        ("Weekend Plan", "Rest, chores, and pretending chores are optional."),
        ("Brain Update", "Installation stuck at 73% because someone said 'quick question'."),
    ],
}


class MemeHandler(BaseHTTPRequestHandler):
    server_version = "MemeClicker/1.0"

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        path = "index.html" if parsed.path in {"/", ""} else parsed.path.lstrip("/")
        target = (STATIC / path).resolve()
        if not str(target).startswith(str(STATIC.resolve())) or not target.is_file():
            self.send_error(404, "Not found")
            return

        content_type, _ = mimetypes.guess_type(target.name)
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/genres":
            self.send_json({"genres": list(GENRES.keys()), "memes": GENRES})
            return
        if parsed.path == "/api/gif":
            params = urllib.parse.parse_qs(parsed.query)
            query = " ".join(
                value[0]
                for key, value in params.items()
                if key in {"genre", "title", "text"} and value and value[0]
            )
            self.send_json(find_gif(query))
            return

        path = "index.html" if parsed.path in {"/", ""} else parsed.path.lstrip("/")
        target = (STATIC / path).resolve()
        if not str(target).startswith(str(STATIC.resolve())) or not target.is_file():
            self.send_error(404, "Not found")
            return

        content_type, _ = mimetypes.guess_type(target.name)
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(target.read_bytes())

    def send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


def find_gif(query):
    clean_query = " ".join(query.split())[:120]
    if not clean_query:
        return {"ok": False, "url": None}
    if clean_query in GIF_RESULT_CACHE:
        return choose_gif(GIF_RESULT_CACHE[clean_query])

    params = urllib.parse.urlencode(
        {
            "q": f"{clean_query} funny meme",
            "key": TENOR_KEY,
            "limit": "8",
            "media_filter": "gif,tinygif",
            "contentfilter": "medium",
        }
    )
    url = f"https://g.tenor.com/v1/search?{params}"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "MemeClicker/1.1"})
        with urllib.request.urlopen(request, timeout=7) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "url": None, "error": str(exc)}

    gif_urls = []
    for item in payload.get("results", []):
        media = item.get("media", [{}])[0]
        gif = media.get("gif") or media.get("tinygif")
        gif_url = gif.get("url") if gif else None
        if gif_url:
            gif_urls.append(gif_url)

    GIF_RESULT_CACHE[clean_query] = gif_urls
    return choose_gif(gif_urls)


def choose_gif(gif_urls):
    if not gif_urls:
        return {"ok": False, "url": None}
    return {"ok": True, "url": random.choice(gif_urls), "source": "tenor"}


def main():
    server = ThreadingHTTPServer((HOST, PORT), MemeHandler)
    print(f"Meme Clicker running at http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
