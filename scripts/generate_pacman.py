#!/usr/bin/env python3
"""
Generates a custom Neon Cyberpunk Pac-Man Contribution Arcade SVG (Dark & Light)
for QttSaed's GitHub profile.
"""
import os
import math
import random
import urllib.request
import re
from datetime import datetime, timedelta


def fetch_real_contributions(username: str = "QttSaed"):
    """Fetch public contribution levels (0..4) from GitHub if available."""
    levels = {}
    try:
        url = f"https://github.com/users/{username}/contributions"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", errors="ignore")
        # Match data-date="YYYY-MM-DD" ... data-level="N"
        for m in re.finditer(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html):
            levels[m.group(1)] = int(m.group(2))
        for m in re.finditer(r'data-level="(\d)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html):
            levels[m.group(2)] = int(m.group(1))
    except Exception:
        pass
    return levels


def build_svg(dark: bool = True) -> str:
    cols = 52
    rows = 7
    cell_size = 13
    gap = 3
    step = cell_size + gap  # 16px
    grid_x0 = 44
    grid_y0 = 62
    grid_w = cols * step - gap  # 829
    grid_h = rows * step - gap  # 109
    width = 900
    height = 224

    # Theme palette (Dark Cyberpunk Indigo/Cyan vs Clean Light)
    if dark:
        bg_card = "#0b0f19"
        bg_inner = "#0f172a"
        border_col = "#1e293b"
        text_muted = "#64748b"
        text_bright = "#e2e8f0"
        empty_cell = "#162033"
        empty_stroke = "#1e293b"
        eaten_cell = "#111827"
        level_colors = {
            0: "#162033",
            1: "#1e3a8a",  # Deep Indigo Blue
            2: "#0284c7",  # Sky Blue
            3: "#06b6d4",  # Electric Cyan
            4: "#38bdf8",  # Bright Neon Cyan
            5: "#a855f7",  # Cyberpunk Purple highlight
        }
        wall_color = "#06b6d4"
        wall_glow = "#22d3ee"
        dot_color = "#fde047"
    else:
        bg_card = "#f8fafc"
        bg_inner = "#f1f5f9"
        border_col = "#cbd5e1"
        text_muted = "#64748b"
        text_bright = "#0f172a"
        empty_cell = "#e2e8f0"
        empty_stroke = "#cbd5e1"
        eaten_cell = "#f1f5f9"
        level_colors = {
            0: "#e2e8f0",
            1: "#bae6fd",
            2: "#38bdf8",
            3: "#0284c7",
            4: "#0369a1",
            5: "#6366f1",
        }
        wall_color = "#0284c7"
        wall_glow = "#38bdf8"
        dot_color = "#eab308"

    # Fetch real contribution data and blend with deterministic arcade pattern
    # so the board always looks rich and active across all 52 weeks
    real_levels = fetch_real_contributions("QttSaed")
    rng = random.Random(20261119)

    # Maze wall cells (symmetric classic arcade obstacles inside the 52x7 grid)
    wall_blocks = [
        # (col_start, row_start, col_span, row_span)
        (4, 1, 3, 1), (4, 5, 3, 1),
        (10, 2, 1, 3), (13, 1, 4, 1), (13, 5, 4, 1),
        (20, 1, 1, 2), (20, 4, 1, 2),
        (24, 2, 4, 3),  # Center Ghost House box
        (31, 1, 1, 2), (31, 4, 1, 2),
        (35, 1, 4, 1), (35, 5, 4, 1), (41, 2, 1, 3),
        (45, 1, 3, 1), (45, 5, 3, 1),
    ]
    wall_set = set()
    for cs, rs, cw, rh in wall_blocks:
        for c in range(cs, cs + cw):
            for r in range(rs, rs + rh):
                wall_set.add((c, r))

    # Build a long continuous closed loop for Pac-Man across the entire 52-week board
    # Guaranteed never to hit any cell in wall_set!
    waypoints = [
        (1, 0), (19, 0), (19, 3), (32, 3), (32, 0), (50, 0),
        (50, 6), (32, 6), (32, 3), (30, 3), (30, 6), (21, 6),
        (21, 0), (30, 0), (30, 3), (19, 3), (19, 6), (11, 6),
        (11, 4), (3, 4), (3, 2), (9, 2), (9, 6), (1, 6), (1, 0)
    ]

    def expand_waypoints(wps):
        path = [wps[0]]
        for nxt in wps[1:]:
            cx, cy = path[-1]
            nx, ny = nxt
            while (cx, cy) != (nx, ny):
                if cx < nx:
                    cx += 1
                elif cx > nx:
                    cx -= 1
                elif cy < ny:
                    cy += 1
                elif cy > ny:
                    cy -= 1
                path.append((cx, cy))
        return path

    pac_path = expand_waypoints(waypoints)
    total_steps = len(pac_path) - 1  # closed loop
    dur_sec = 26.0

    # Record the first step index when Pac-Man visits each cell
    first_visit = {}
    for idx, cell in enumerate(pac_path[:-1]):
        if cell not in first_visit:
            first_visit[cell] = idx

    # Assign visual level to each cell (c, r)
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=cols * 7 - 1)

    grid_levels = {}
    for c in range(cols):
        for r in range(rows):
            if (c, r) in wall_set:
                grid_levels[(c, r)] = -1
                continue
            d = (start_date + timedelta(days=c * 7 + r)).strftime("%Y-%m-%d")
            real_lvl = real_levels.get(d, 0)
            if real_lvl > 0:
                grid_levels[(c, r)] = min(5, real_lvl + 1)
            elif (c, r) in first_visit:
                # Cells along Pac-Man's corridor are bright commit blocks to eat!
                grid_levels[(c, r)] = rng.choice([2, 3, 3, 4, 4, 5])
            else:
                # Background contribution pattern across the year so the grid looks rich & full
                roll = rng.random()
                if roll < 0.38:
                    grid_levels[(c, r)] = 0
                elif roll < 0.65:
                    grid_levels[(c, r)] = 1
                elif roll < 0.84:
                    grid_levels[(c, r)] = 2
                elif roll < 0.95:
                    grid_levels[(c, r)] = 3
                else:
                    grid_levels[(c, r)] = 4

    # Power Pellets at 4 strategic corners on Pac-Man's path
    power_pellets = {(1, 0), (50, 0), (50, 6), (1, 6)}

    def cell_center(c, r):
        return (grid_x0 + c * step + cell_size / 2.0, grid_y0 + r * step + cell_size / 2.0)

    out = []
    out.append(f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">')
    out.append(f'''  <defs>
    <linearGradient id="cardBorder" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.7"/>
      <stop offset="50%" stop-color="#3b82f6" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#a855f7" stop-opacity="0.7"/>
    </linearGradient>
    <linearGradient id="barGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="50%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#a855f7"/>
    </linearGradient>
    <filter id="neonGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.2" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="pacGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.8" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <!-- Vector Ghost Template -->
    <g id="ghostBody">
      <path d="M -7.5,6 L -7.5,-1.5 A 7.5,7.5 0 0,1 7.5,-1.5 L 7.5,6 L 5,3.8 L 2.5,6 L 0,3.8 L -2.5,6 L -5,3.8 Z" />
      <circle cx="-2.7" cy="-2" r="2.1" fill="#ffffff"/>
      <circle cx="2.7" cy="-2" r="2.1" fill="#ffffff"/>
      <circle cx="-2.0" cy="-2" r="1.1" fill="#1d4ed8"/>
      <circle cx="3.4" cy="-2" r="1.1" fill="#1d4ed8"/>
    </g>
  </defs>''')

    # Outer Arcade Card
    out.append(f'  <rect x="2" y="2" width="{width-4}" height="{height-4}" rx="14" fill="{bg_card}" stroke="url(#cardBorder)" stroke-width="1.8"/>')
    out.append(f'  <rect x="12" y="38" width="{width-24}" height="146" rx="10" fill="{bg_inner}" stroke="{border_col}" stroke-width="1"/>')

    # Top Arcade HUD Header
    out.append(f'''  <g font-family="'Fira Code', 'Consolas', 'Segoe UI', monospace" font-size="11" font-weight="700">
    <circle cx="24" cy="21" r="5.5" fill="#facc15" filter="url(#neonGlow)"/>
    <path d="M 24,21 L 30,17.5 L 30,24.5 Z" fill="{bg_card}"/>
    <text x="36" y="25" fill="#22d3ee" letter-spacing="1">PAC-MAN // CONTRIBUTION ARCADE</text>
    <text x="340" y="25" fill="{text_muted}">1UP <tspan fill="{text_bright}">04820</tspan></text>
    <text x="455" y="25" fill="{text_muted}">HIGH SCORE <tspan fill="#38bdf8">99990</tspan></text>
    <text x="615" y="25" fill="{text_muted}">STAGE <tspan fill="#a855f7">QttSaed</tspan></text>
  </g>''')

    # Top-Right Legend (Less ... More)
    lx = 748
    out.append(f'  <text x="{lx - 30}" y="25" font-family="\'Segoe UI\', sans-serif" font-size="10" fill="{text_muted}">Less</text>')
    for i, lv in enumerate([0, 1, 2, 3, 4, 5]):
        out.append(f'  <rect x="{lx + i*15}" y="15" width="11" height="11" rx="2.5" fill="{level_colors[lv]}" stroke="{empty_stroke}" stroke-width="0.6"/>')
    out.append(f'  <text x="{lx + 6*15 + 4}" y="25" font-family="\'Segoe UI\', sans-serif" font-size="10" fill="{text_muted}">More</text>')

    # Month Labels & Day Labels
    months = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    for idx, m_name in enumerate(months):
        mx = grid_x0 + int(idx * (cols / 12.0)) * step + 6
        out.append(f'  <text x="{mx}" y="54" font-family="\'Fira Code\', \'Segoe UI\', sans-serif" font-size="9.5" font-weight="600" fill="{text_muted}">{m_name}</text>')

    for r_idx, d_name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        dy = grid_y0 + r_idx * step + 10
        out.append(f'  <text x="18" y="{dy}" font-family="\'Fira Code\', \'Segoe UI\', sans-serif" font-size="9" fill="{text_muted}">{d_name}</text>')

    # Draw 52x7 Grid Cells
    for c in range(cols):
        for r in range(rows):
            x = grid_x0 + c * step
            y = grid_y0 + r * step
            lvl = grid_levels[(c, r)]
            if lvl == -1:
                # Base dark cell under maze wall
                out.append(f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="3" fill="{eaten_cell}"/>')
                continue

            col = level_colors[lvl]
            if (c, r) in first_visit:
                # Animated commit block that gets eaten when Pac-Man arrives!
                visit_step = first_visit[(c, r)]
                t_eat = max(0.01, min(0.96, visit_step / float(total_steps)))
                t_pre = max(0.0, t_eat - 0.004)
                t_respawn = 0.985
                out.append(
                    f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="3.2" fill="{col}" stroke="{empty_stroke}" stroke-width="0.6">'
                    f'<animate attributeName="fill" dur="{dur_sec}s" repeatCount="indefinite" '
                    f'keyTimes="0;{t_pre:.4f};{t_eat:.4f};{t_respawn:.4f};1" '
                    f'values="{col};{col};{eaten_cell};{eaten_cell};{col}"/>'
                    f'</rect>'
                )
                # Glowing pac-dot or power pellet in the center of the corridor cell
                cx, cy = cell_center(c, r)
                if (c, r) in power_pellets:
                    out.append(
                        f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.2" fill="#fde047" filter="url(#neonGlow)">'
                        f'<animate attributeName="r" dur="0.9s" repeatCount="indefinite" values="3.2;4.8;3.2"/>'
                        f'<animate attributeName="opacity" dur="{dur_sec}s" repeatCount="indefinite" '
                        f'keyTimes="0;{t_pre:.4f};{t_eat:.4f};{t_respawn:.4f};1" values="1;1;0;0;1"/>'
                        f'</circle>'
                    )
                else:
                    out.append(
                        f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.7" fill="{dot_color}">'
                        f'<animate attributeName="opacity" dur="{dur_sec}s" repeatCount="indefinite" '
                        f'keyTimes="0;{t_pre:.4f};{t_eat:.4f};{t_respawn:.4f};1" values="0.95;0.95;0;0;0.95"/>'
                        f'</circle>'
                    )
            else:
                out.append(
                    f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="3.2" fill="{col}" stroke="{empty_stroke}" stroke-width="0.6"/>'
                )

    # Draw Neon Arcade Maze Walls (Double-lined glowing rounded boxes!)
    out.append('  <g filter="url(#neonGlow)">')
    for cs, rs, cw, rh in wall_blocks:
        wx = grid_x0 + cs * step + 1
        wy = grid_y0 + rs * step + 1
        ww = cw * step - gap - 2
        wh = rh * step - gap - 2
        out.append(
            f'    <rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="5" '
            f'fill="{bg_card}" stroke="{wall_color}" stroke-width="2.2"/>'
        )
        if ww > 20 and wh > 20:
            # Ghost house inner gate
            out.append(
                f'    <rect x="{wx+4}" y="{wy+4}" width="{ww-8}" height="{wh-8}" rx="3" '
                f'fill="none" stroke="#a855f7" stroke-width="1.2" stroke-dasharray="6 3"/>'
            )
    out.append('  </g>')

    # Build Pac-Man translation & rotation keyframes
    trans_vals = []
    rot_vals = []
    key_times = []
    for idx, (c, r) in enumerate(pac_path):
        cx, cy = cell_center(c, r)
        trans_vals.append(f"{cx:.1f},{cy:.1f}")
        key_times.append(f"{idx / float(total_steps):.4f}")
        if idx < total_steps:
            nc, nr = pac_path[idx + 1]
        else:
            nc, nr = pac_path[1]
        dx, dy = nc - c, nr - r
        if dx > 0:
            angle = 0
        elif dx < 0:
            angle = 180
        elif dy > 0:
            angle = 90
        else:
            angle = 270
        rot_vals.append(str(angle))

    kt_str = ";".join(key_times)
    tr_str = ";".join(trans_vals)
    rot_str = ";".join(rot_vals)

    # Pac-Man Vector Character (Outer group translates, inner group rotates, path chomps!)
    out.append(f'''  <g filter="url(#pacGlow)">
    <g>
      <animateTransform attributeName="transform" type="translate" dur="{dur_sec}s" repeatCount="indefinite"
        keyTimes="{kt_str}" values="{tr_str}" />
      <g>
        <animateTransform attributeName="transform" type="rotate" dur="{dur_sec}s" repeatCount="indefinite"
          calcMode="discrete" keyTimes="{kt_str}" values="{rot_str}" />
        <path fill="#facc15" d="M 0,0 L 8.2,4.8 A 9.5,9.5 0 1,1 8.2,-4.8 Z">
          <animate attributeName="d" dur="0.28s" repeatCount="indefinite"
            values="M 0,0 L 8.0,5.2 A 9.5,9.5 0 1,1 8.0,-5.2 Z;M 0,0 L 9.4,0.8 A 9.5,9.5 0 1,1 9.4,-0.8 Z;M 0,0 L 8.0,5.2 A 9.5,9.5 0 1,1 8.0,-5.2 Z" />
        </path>
      </g>
    </g>
  </g>''')

    # 4 Vector Ghosts patrolling corridors (guaranteed zero wall intersections)
    ghost_configs = [
        ("blinky", "#ef4444", [(12, 0), (18, 0), (18, 6), (12, 6), (12, 0)], "10.5s"),
        ("pinky", "#ec4899", [(2, 0), (8, 0), (8, 6), (2, 6), (2, 0)], "9.5s"),
        ("inky", "#22d3ee", [(33, 0), (39, 0), (39, 6), (33, 6), (33, 0)], "11s"),
        ("clyde", "#f97316", [(43, 0), (49, 0), (49, 6), (43, 6), (43, 0)], "9s"),
    ]

    assert not (set(pac_path) & wall_set), "Pac-Man path intersects wall!"
    for g_name, g_col, g_wps, g_dur in ghost_configs:
        g_path = expand_waypoints(g_wps)
        assert not (set(g_path) & wall_set), f"Ghost {g_name} intersects wall!"
        g_steps = len(g_path) - 1
        g_kt = ";".join(f"{i / float(g_steps):.4f}" for i in range(len(g_path)))
        g_tr = ";".join(f"{cell_center(c, r)[0]:.1f},{cell_center(c, r)[1]:.1f}" for c, r in g_path)
        out.append(f'''  <g fill="{g_col}" filter="url(#neonGlow)">
    <animateTransform attributeName="transform" type="translate" dur="{g_dur}" repeatCount="indefinite"
      keyTimes="{g_kt}" values="{g_tr}" />
    <use href="#ghostBody" />
  </g>''')

    # Bottom Arcade Progress Bar & Status Footer
    out.append(f'''  <g font-family="'Fira Code', 'Consolas', 'Segoe UI', monospace" font-size="10" font-weight="600">
    <text x="20" y="206" fill="{text_muted}">ARCADE SYNC // <tspan fill="#22d3ee">AUTO-UPDATED DAILY VIA GITHUB ACTIONS</tspan></text>
    <rect x="440" y="197" width="436" height="8" rx="4" fill="{empty_cell}" stroke="{border_col}" stroke-width="0.8"/>
    <rect x="440" y="197" width="40" height="8" rx="4" fill="url(#barGrad)" filter="url(#neonGlow)">
      <animate attributeName="width" dur="{dur_sec}s" repeatCount="indefinite" values="24;436;24" />
    </rect>
  </g>''')

    out.append('</svg>')
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs("dist", exist_ok=True)
    dark_svg = build_svg(dark=True)
    light_svg = build_svg(dark=False)
    with open("dist/pacman-contribution-graph-dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    with open("dist/pacman-contribution-graph.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print("Generated custom Neon Cyberpunk Pac-Man SVGs in dist/")
