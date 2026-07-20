"""Physics-accurate reachability for Skyrift maps.

Mirrors update_player() in src/main.c frame for frame, so a jump is only
counted as possible if the real game can actually perform it. The old
heuristic (rise/run lookup table) had no notion of terrain *between* two
platforms, which shipped an impassable isle 3: a 17-tile tree trunk sat
between the branches it claimed were one hop apart.

Only '#' blocks movement; '=' is one-way (you pass up/through it and can
only land on it from above), matching hard_box()/landing_box().
"""

TILE = 16
PHIT_W, PHIT_H = 12, 18
GRAVITY = 0.35
MOVE_SPEED = 2.0
JUMP_VEL = -6.3
AIRJUMP_VEL = -5.4
GLIDE_SPEED = MOVE_SPEED + 0.5
GLIDE_CAP = 0.65
MAX_FALL = 6.0


class Map:
    def __init__(self, rows):
        self.rows = rows
        self.h = len(rows)
        self.w = max(len(r) for r in rows)

    def at(self, tx, ty):
        if tx < 0 or ty < 0 or ty >= self.h:
            return ' '
        row = self.rows[ty]
        return row[tx] if tx < len(row) else ' '

    def hard(self, px, py):
        return self.at(int(px // TILE), int(py // TILE)) == '#'

    def hard_box(self, x, y):
        w, h = PHIT_W, PHIT_H
        return (self.hard(x, y) or self.hard(x + w - 1, y) or
                self.hard(x, y + h - 1) or self.hard(x + w - 1, y + h - 1) or
                self.hard(x + w / 2, y) or self.hard(x + w / 2, y + h - 1))

    def landing(self, x, y, old_feet):
        ty = int((y + PHIT_H - 1) // TILE)
        for px in (x, x + PHIT_W / 2, x + PHIT_W - 1):
            c = self.at(int(px // TILE), ty)
            if c == '#':
                return True
            if c == '=' and old_feet <= ty * TILE:
                return True
        return False


def simulate(m, x, y, hdir, airjump_frame, glide, max_frames=260):
    """One jump attempt. Returns the resting (x, y) or None if it falls out."""
    vy = JUMP_VEL
    air_jumps = 1
    on_ground = False
    for f in range(max_frames):
        gliding = (not on_ground and glide and vy > 0.4)
        vx = hdir * (GLIDE_SPEED if gliding else MOVE_SPEED)

        vy += GRAVITY
        if vy > MAX_FALL:
            vy = MAX_FALL
        if gliding and vy > GLIDE_CAP:
            vy = GLIDE_CAP

        if airjump_frame is not None and f == airjump_frame and air_jumps > 0:
            air_jumps -= 1
            vy = AIRJUMP_VEL

        nx = x + vx
        if not m.hard_box(nx, y):
            x = nx

        on_ground = False
        if vy >= 0:
            old_feet = y + PHIT_H - 1
            ny = y + vy
            if m.landing(x, ny, old_feet):
                y = float(int((ny + PHIT_H - 1) // TILE) * TILE - PHIT_H)
                on_ground = True
                vy = 0
                return (x, y)
            y = ny
        else:
            ny = y + vy
            if not m.hard_box(x, ny):
                y = ny
            else:
                vy = 0

        if y > m.h * TILE + 60:
            return None
    return None


# jump strategies a player can actually execute
def strategies():
    out = []
    for hdir in (-1, 0, 1):
        for aj in (None, 4, 8, 12, 16, 20, 24, 30):
            for glide in (False, True):
                out.append((hdir, aj, glide))
    return out


STRATS = strategies()


def standable_cells(m):
    """Cells where the player can rest: solid/platform below, body fits."""
    cells = set()
    for ty in range(m.h - 1):
        for tx in range(m.w):
            below = m.at(tx, ty + 1)
            if below not in '#=':
                continue
            x = tx * TILE + (TILE - PHIT_W) / 2
            y = (ty + 1) * TILE - PHIT_H
            if m.hard_box(x, y):
                continue
            cells.add((tx, ty))
    return cells


def cell_of(x, y):
    return (int((x + PHIT_W / 2) // TILE), int((y + PHIT_H - 1) // TILE))


def reachable_from(m, start_cells):
    """BFS over standable cells using real simulated jumps (and walking)."""
    from collections import deque
    seen = set(start_cells)
    q = deque(start_cells)
    while q:
        tx, ty = q.popleft()
        x = tx * TILE + (TILE - PHIT_W) / 2
        y = (ty + 1) * TILE - PHIT_H
        for hdir, aj, glide in STRATS:
            land = simulate(m, x, y, hdir, aj, glide)
            if land is None:
                continue
            c = cell_of(*land)
            if c not in seen:
                seen.add(c)
                q.append(c)
        # walking / stepping off ledges (no jump): short slide either way
        for hdir in (-1, 1):
            wx, wy, vy = x, y, 0.0
            for _ in range(90):
                vy = min(vy + GRAVITY, MAX_FALL)
                nx = wx + hdir * MOVE_SPEED
                if not m.hard_box(nx, wy):
                    wx = nx
                old_feet = wy + PHIT_H - 1
                ny = wy + vy
                if m.landing(wx, ny, old_feet):
                    wy = float(int((ny + PHIT_H - 1) // TILE) * TILE - PHIT_H)
                    vy = 0
                else:
                    wy = ny
                if wy > m.h * TILE + 60:
                    break
                c = cell_of(wx, wy)
                if vy == 0 and c not in seen:
                    seen.add(c)
                    q.append(c)
    return seen


def drop_to_stand(m, r, c, stand):
    while r < m.h - 1:
        if (c, r) in stand:
            return (c, r)
        r += 1
    return None


def find(rows, ch):
    for r, row in enumerate(rows):
        c = row.find(ch)
        if c >= 0:
            return (r, c)
    return None


def audit(rows, name, req_gems):
    """Returns a list of problem strings (empty = level is sound)."""
    m = Map(rows)
    stand = standable_cells(m)
    problems = []

    pr, pc = find(rows, 'P')
    start = drop_to_stand(m, pr, pc, stand)
    if not start:
        return [f"{name}: spawn has no footing"]
    seen = reachable_from(m, [start])

    dr, dc = find(rows, 'D')
    door = drop_to_stand(m, dr, dc, stand)
    if door not in seen:
        problems.append(f"{name}: DOOR unreachable from spawn")

    # a pickup counts as reachable if some reachable cell can touch it
    def pickup_ok(r, c):
        for (sx, sy) in seen:
            if abs(sx - c) <= 4 and -6 <= sy - r <= 5:
                return True
        return False

    gems = [(r, c) for r, row in enumerate(rows)
            for c, ch in enumerate(row) if ch == '*']
    bad_gems = [(r, c) for r, c in gems if not pickup_ok(r, c)]
    ok_gems = len(gems) - len(bad_gems)
    if bad_gems:
        problems.append(f"{name}: {len(bad_gems)} unreachable gems {bad_gems[:6]}")
    if ok_gems < req_gems:
        problems.append(
            f"{name}: only {ok_gems} reachable gems but door needs {req_gems}")

    for ch, label in (('C', 'checkpoint'), ('H', 'cherry')):
        for r, row in enumerate(rows):
            for c, x in enumerate(row):
                if x == ch and not pickup_ok(r, c):
                    problems.append(f"{name}: {label} at ({r},{c}) unreachable")
    return problems
