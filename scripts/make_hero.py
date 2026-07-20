#!/usr/bin/env python3
"""
CFTrust blog hero image generator.

Matches the style Christian built by hand for the first post (post_1_thumb.png):
navy background, bold stacked white caps title, gold verse reference below.
Renders via the gordon-playwright service (already running in the stack) so no
new host dependencies are needed — HTML/CSS in, PNG out.

Usage:
    python3 scripts/make_hero.py "Buried Treasure" "MATTHEW 25:14-30" blog-talents.png
"""

import base64
import sys
import requests

PLAYWRIGHT_URL = "http://localhost:3005/screenshot"
WIDTH, HEIGHT = 960, 480

TEMPLATE = """
<!DOCTYPE html>
<html><head><style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    width: {width}px; height: {height}px;
    background: #0e2c52;
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
  }}
  .verse {{
    color: #e3c25c;
    font-weight: 800;
    font-size: 28px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 24px;
  }}
</style></head>
<body>
  <div class="title">{title}</div>
  <div class="verse">{verse}</div>
</body></html>
"""


def make_hero(title: str, verse: str, out_path: str):
    # Rough font-size tiers so long titles don't overflow the card.
    title_size = 64 if len(title) < 20 else 48 if len(title) < 36 else 36

    html = TEMPLATE.format(width=WIDTH, height=HEIGHT, title_size=title_size,
                            title=title, verse=verse)
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
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: make_hero.py <title> <verse> <output_path>")
        sys.exit(1)
    make_hero(sys.argv[1], sys.argv[2], sys.argv[3])
