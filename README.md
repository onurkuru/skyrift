# Skyrift

An original sky-gliding pixel-art adventure for PS Vita homebrew and desktop.

- **Code**: original, single-file C99 + SDL2 ([src/main.c](src/main.c))
- **Art**: ["Sunny Land"](https://opengameart.org/content/sunny-land-2d-pixel-art-pack) by Ansimuz, **CC0** (`assets/`)
- **Audio**: no sound files — soft chiptune SFX and an ambient music loop are synthesized at boot
- **PNG loader**: [stb_image](https://github.com/nothings/stb) — public domain

![screenshot](screenshot.png)

## Play it on your Vita (no building required)

1. Your Vita must be homebrew-enabled (HENkaku / h-encore² — follow
   [vita.hacks.guide](https://vita.hacks.guide), it takes ~15 minutes).
2. Download **`skyrift.vpk`** from the
   [latest release](https://github.com/onurkuru/skyrift/releases/latest).
3. Copy it to the Vita: in **VitaShell** press **SELECT** to start the FTP
   server, connect from your computer (`ftp://<vita-ip>:1337`) and upload
   the file to `ux0:/` — or use a USB cable (SELECT toggles USB mode too).
4. On the Vita, navigate to the file in VitaShell, press **X** → **Install**
   (accept the extended permissions prompt).
5. Exit VitaShell — **Skyrift** now has a bubble on your LiveArea. Enjoy!

## Story

The Sunreef Isles float on the Old Wind. The Sky Tyrant shattered the Great
Beacon, and its nine shards fell across the isles. The wind is dying; the
isles are sinking. You are **Kip** — the last Glider Courier, a fox who
catches the wind with his tail. Cross the ten isles, free every shard,
relight the Beacon.

## The Ten Isles

| # | Isle | Style | Boss |
|---|------|-------|------|
| 1 | Verdant Woods | open forest, tutorial | — |
| 2 | Twilight Hollow | cave galleries | — |
| 3 | Canopy Heights | giant trees, vertical | **MIRE KING** (giant frog) |
| 4 | Sunken Grotto | winding tunnels | — |
| 5 | Windy Cliffs | rising terraces | **RUST FANG** (giant opossum) |
| 6 | Ruined Hamlet | broken ground, rooftops | — |
| 7 | The Underroot | underground maze | **GALE WRAITH** (purple eagle) |
| 8 | Skybridge | bridges over the void | — |
| 9 | Storm Ascent | vertical zigzag climb | — |
| 10 | Tyrant's Throne | sky arena | **SKY TYRANT** (final) |

Each isle's exit door opens once you bank enough gems (and defeat the boss,
if one guards the isle). Passing a door frees a Beacon shard. Topple the
Tyrant on isle 10 and relight the Beacon.

## Controls

| Action | Desktop             | PS Vita          |
|--------|---------------------|------------------|
| Move   | Arrows / WASD       | Left stick / dpad|
| Jump / double jump | Z / Space | Cross         |
| Glide (hold in air) | Z      | Cross            |
| Shoot  | X / Shift           | Square           |
| Dash (LV2+) | C / V          | Circle           |
| Pause  | P                   | Start            |
| Quit   | ESC                 | Select           |

## Mechanics

- Press jump again in the air → **double jump** (tucks into a spinning ball);
  **hold jump in the air → tail glide** (slow fall, strong air control)
- **Stomp**: land on a foe to squash it — hold jump for a high bounce, and
  the stomp refreshes your air jump for big chain routes
- Kills reset the dash cooldown; brick platforms are one-way
  (down+jump drops through)
- **Score & combo**: gem +100, enemy +40/50, boss +1000; chained kills multiply
- **Skill levels**: LV2 dash · LV3 double shot · LV4 rapid fire · LV5 +1 max HP · LV6 triple shot
- **Enemies**: eagle (chases, speed-capped), frog (crouch-telegraphs its hop),
  opossum (patrols) + 4 bosses with minion waves and telegraphed attacks
- Cherries heal; checkpoint signs move your respawn point **and heal you full**
- Best score persists on device; completion time shown at the end
- Coyote time, variable jump height, squash & stretch, gem magnet, hit-stop,
  ground shadows, dash afterimages, isle intro cards
- Every isle is machine-validated: each gem and door is reachable from both
  the spawn and the door — no dead ends, no soft-locks

## Desktop build

```sh
brew install sdl2 cmake   # once (macOS; use your package manager elsewhere)
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make
./skyrift
```

## PS Vita build (.vpk) — from source

### 1. Install VitaSDK (once)

```sh
git clone https://github.com/vitasdk/vdpm
cd vdpm
./bootstrap-vitasdk.sh
export VITASDK=/usr/local/vitasdk        # add to your shell profile too
export PATH=$VITASDK/bin:$PATH
./install-all.sh                          # installs all ports incl. SDL2
```

### 2. Build the VPK

```sh
mkdir -p build-vita && cd build-vita
cmake .. -DBUILD_VITA=ON -DCMAKE_BUILD_TYPE=Release
make skyrift.vpk-vpk        # produces build-vita/skyrift.vpk
```

> On macOS the VitaSDK bootstrap's toolchain URL resolver can fail SSL
> verification (`CERTIFICATE_VERIFY_FAILED`). If it does, install `wget`
> first (`brew install wget`) and point `VITASDK` at a writable path
> (e.g. `$HOME/vitasdk`) before running `./bootstrap-vitasdk.sh`.

### 3. Install on the Vita

Requires a homebrew-enabled Vita (h-encore² + HENkaku, see
[vita.hacks.guide](https://vita.hacks.guide)). Transfer `skyrift.vpk` with
VitaShell FTP, press X → Install, launch from LiveArea.

## Developer notes

- Maps are generated by [tools/genlevels.py](tools/genlevels.py) → `src/levels.h`
  (placement-validated: nothing can spawn inside terrain or floating in the void)
- `SKYRIFT_TEST=1 ./skyrift` — physics & skill smoke tests
- `SKYRIFT_SHOT=/path.bmp ./skyrift` — capture one frame and exit
- `SKYRIFT_LEVEL=n ./skyrift` — start on isle n (0-9)
- `SKYRIFT_TITLE=1` — capture the title screen in shot mode

## License

Code is MIT. Art assets are from Ansimuz's CC0 "Sunny Land" packs.
stb_image is public domain.
