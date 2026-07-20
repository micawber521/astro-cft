#!/usr/bin/env python3
"""
CFTrust blog hero image generator.

Matches the style Christian built by hand for the first post (post_1_thumb.png):
bold stacked white caps title, gold verse reference below, text-shadow for
legibility over any background. Renders via the gordon-playwright service
(already running in the stack) so no new host dependencies are needed —
HTML/CSS in, PNG out.

Background rotates through the Astro starter's own placeholder gradients
(blog-placeholder-2/3/4/5.jpg) instead of a flat color, so posts don't all
look identical. blog-placeholder-1.jpg and blog-placeholder-about.jpg are
excluded — both have Astro's own logo/mascot baked into the image, not just
a plain gradient. Rotation position persists in .hero_state.json.

Usage:
    python3 scripts/make_hero.py "Don't Bury the Father's Treasure" "MATTHEW 25:14-30" blog-talents.png
"""

import base64
import json
import mimetypes
import sys
from pathlib import Path

import requests

PLAYWRIGHT_URL = "http://localhost:3005/screenshot"
WIDTH, HEIGHT = 960, 480

SCRIPT_DIR   = Path(__file__).parent
PUBLIC_DIR   = SCRIPT_DIR.parent / "public"
STATE_PATH   = SCRIPT_DIR / ".hero_state.json"
BG_ROTATION  = [
    "blog-placeholder-2.jpg",
    "blog-placeholder-3.jpg",
    "blog-placeholder-4.jpg",
    "blog-placeholder-5.jpg",
]

TEMPLATE = """
<!DOCTYPE html>
<html><head><style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    width: {width}px; height: {height}px;
    background-image:
      linear-gradient(rgba(0,0,0,0.40), rgba(0,0,0,0.40)),
      url({bg_data_uri});
    background-size: cover;
    background-position: center;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    font-family: Arial, Helvetica, sans-serif;
  }}
  .title {{
    color: #f5f0e6;
    font-weight: 900;
    font-size: {title_size}px;
    text-transform: uppercase;
    text-align: center;
    line-height: 1.05;
    letter-spacing: 1px;
    padding: 0 50px;
    text-shadow: 0 2px 14px rgba(0,0,0,0.85);
  }}
  .verse {{
    color: #e3c25c;
    font-weight: 800;
    font-size: 28px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 24px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.85);
  }}
</style></head>
<body>
  <div class="title">{title}</div>
  <div class="verse">{verse}</div>
</body></html>
"""


def _next_background() -> str:
    state = {"next_index": 0}
    if STATE_PATH.exists():
        try:
            state = json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    idx = state.get("next_index", 0) % len(BG_ROTATION)
    state["next_index"] = idx + 1
    STATE_PATH.write_text(json.dumps(state))
    return BG_ROTATION[idx]


def _bg_data_uri(filename: str) -> str:
    path = PUBLIC_DIR / filename
    mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def make_hero(title: str, verse: str, out_path: str, background: str = None):
    background = background or _next_background()
    bg_data_uri = _bg_data_uri(background)

    # Rough font-size tiers so long titles don't overflow the card.
    title_size = 64 if len(title) < 20 else 48 if len(title) < 36 else 36

    html = TEMPLATE.format(width=WIDTH, height=HEIGHT, title_size=title_size,
                            title=title, verse=verse, bg_data_uri=bg_data_uri)
    data_url = "data:text/html;base64," + base64.b64encode(html.encode()).decode()

    resp = requests.post(PLAYWRIGHT_URL, json={
        "url": data_url,
        "full_page": False,
        "viewport": {"width": WIDTH, "height": HEIGHT},
    }, timeout=30)
    resp.raise_for_status()
    png_b64 = resp.json()["screenshot_b64"]

    with open(out_path, "wb") as f:
        f.write(base64.b64decode(png_b64))
    print(f"wrote {out_path} (background: {background})")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: make_hero.py <title> <verse> <output_path>")
        sys.exit(1)
    make_hero(sys.argv[1], sys.argv[2], sys.argv[3])
