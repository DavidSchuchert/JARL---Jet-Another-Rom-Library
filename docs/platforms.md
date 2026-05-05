# Platforms

JARL detects platforms from **path segments** — the scanner splits each file's path by `/` and matches parts against known platform slugs. No enforced folder structure is required.

---

## How Platform Detection Works

JARL walks all subdirectories under `SCANNER__ROMS_PATH`. For each file it finds, it extracts path segments and checks for matches against registered platform slugs (longest slug wins).

Example:

```
/roms/nintendo/nes/Legend of Zelda (USA).nes
                         ^^^^^  ^^
                         family slug
                         nes    ← detected as `nes` platform
```

```
/roms/sony/psx/Metal Gear Solid (USA).bin
                         ^^^  ^^^
                         family  slug
                         psx     ← detected as `psx` platform
```

Platform detection also considers parent directory names as fallback — if `nes` isn't found in the path, it checks the `nintendo` folder to infer the platform.

---

## Supported Platforms (80+)

| Slug               | Display Name                  | Family     |
| ------------------ | ---------------------------- | ---------- |
| `nes`              | Nintendo Entertainment System | Nintendo   |
| `snes`             | Super Nintendo               | Nintendo   |
| `n64`              | Nintendo 64                  | Nintendo   |
| `n64dd`            | Nintendo 64DD               | Nintendo   |
| `gamecube`         | Nintendo GameCube           | Nintendo   |
| `wii`              | Nintendo Wii                 | Nintendo   |
| `wiiu`             | Nintendo Wii U               | Nintendo   |
| `switch`           | Nintendo Switch              | Nintendo   |
| `gameboy`          | Game Boy                     | Nintendo   |
| `gameboycolor`     | Game Boy Color              | Nintendo   |
| `gameboyadvance`   | Game Boy Advance            | Nintendo   |
| `virtualboy`       | Virtual Boy                 | Nintendo   |
| `nds`              | Nintendo DS                  | Nintendo   |
| `3ds`              | Nintendo 3DS                 | Nintendo   |
| `gameandwatch`     | Game & Watch                | Nintendo   |
| `pokemini`         | Pokemon Mini                | Nintendo   |
| `psx`              | PlayStation                 | Sony       |
| `ps2`              | PlayStation 2               | Sony       |
| `ps3`              | PlayStation 3               | Sony       |
| `ps4`              | PlayStation 4               | Sony       |
| `ps5`              | PlayStation 5               | Sony       |
| `psp`              | PlayStation Portable         | Sony       |
| `vita`             | PlayStation Vita            | Sony       |
| `megadrive`        | Mega Drive / Genesis        | Sega       |
| `mastersystem`      | Master System              | Sega       |
| `gamegear`         | Game Gear                  | Sega       |
| `segacd`           | Sega CD                    | Sega       |
| `saturn`           | Sega Saturn                 | Sega       |
| `dreamcast`        | Sega Dreamcast             | Sega       |
| `sg1000`           | SG-1000                    | Sega       |
| `sega32x`          | Sega 32X                   | Sega       |
| `atari2600`        | Atari 2600                 | Atari      |
| `atari5200`        | Atari 5200                 | Atari      |
| `atari7800`        | Atari 7800                 | Atari      |
| `atarilynx`        | Atari Lynx                 | Atari      |
| `atarijaguar`      | Atari Jaguar               | Atari      |
| `atarist`          | Atari ST                   | Atari      |
| `atari800`         | Atari 800                  | Atari      |
| `atarixe`          | Atari XE                   | Atari      |
| `atarifalcon`      | Atari Falcon               | Atari      |
| `ataritt`          | Atari TT                   | Atari      |
| `xbox`             | Xbox                        | Microsoft  |
| `xbox360`          | Xbox 360                    | Microsoft  |
| `pc`               | PC (x86)                   | PC         |
| `dos`              | DOS                        | PC         |
| `windows`          | Windows                    | PC         |
| `scummvm`          | ScummVM                    | Ports      |
| `msx`              | MSX                        | MSX        |
| `pce`              | TurboGrafx-16/PC Engine    | NEC        |
| `3do`              | 3DO                       | 3DO        |
| `ngp`              | Neo Geo Pocket             | SNK        |
| `ngpc`             | Neo Geo Pocket Color       | SNK        |
| `ws`               | WonderSwan                | Waninkoko  |
| `wsc`              | WonderSwan Color           | Waninkoko  |
| `colecovision`      | ColecoVision               | Coleco     |
| `intellivision`     | Intellivision              | Mattel     |
| `odyssey2`          | Magnavox Odyssey 2         | Magnavox   |
| `vectrex`           | Vectrex                    | GCE        |
| `channelf`          | Fairchild Channel F        | Fairchild  |
| `uzebox`            | Uzebox                     | Uzebox     |
| `tic80`             | TIC-80                    | Fantasy    |
| `pico8`             | PICO-8                    | Fantasy    |
| `lowresnx`          | LowRes NX                 | Fantasy    |
| `mame`              | MAME                      | Arcade     |
| `arcade`            | Arcade                    | Arcade     |
| `neogeo`            | Neo Geo                   | Arcade     |
| `neogeocd`          | Neo Geo CD                | Arcade     |
| `fbneo`             | Final Burn Neo            | Arcade     |
| `fba`               | Final Burn Alpha          | Arcade     |
| `atomiswave`        | Atomiswave                | Arcade     |
| `naomi`              | Sega NAOMI               | Arcade     |
| `naomi2`            | Sega NAOMI 2              | Arcade     |
| `model2`            | Sega Model 2              | Arcade     |
| `model3`            | Sega Model 3              | Arcade     |
| `daphne`            | Daphne                    | Arcade     |
| `amiga500`          | Amiga 500                 | Amiga      |
| `amiga1200`         | Amiga 1200                | Amiga      |
| `amigacd32`         | Amiga CD32                | Amiga      |
| `amigacdtv`         | Amiga CDTV                | Amiga      |
| `c64`               | Commodore 64              | Commodore   |
| `c128`              | Commodore 128              | Commodore   |
| `vic20`             | Commodore VIC-20           | Commodore   |
| `plus4`             | Commodore Plus/4           | Commodore   |
| `apple2`            | Apple II                  | Apple      |
| `apple2gs`          | Apple IIGS                | Apple      |
| `macintosh`         | Apple Macintosh            | Apple      |
| `x68000`            | Sharp X68000              | Sharp      |
| `pc88`              | NEC PC-8801               | NEC        |
| `pc98`              | NEC PC-9801               | NEC        |
| `zx81`              | ZX81                      | Sinclair   |
| `zxspectrum`       | ZX Spectrum               | Sinclair   |
| `samcoupe`          | SAM Coupe                 | MGT        |
| `fmtowns`           | FM Towns                  | Fujitsu    |

---

## Adding Custom Platforms

JARL's platform registry lives in `backend/app/scanner/platforms.py`. To add a new platform:

```python
"my-platform": PlatformInfo(
    slug="my-platform",
    name="My Platform",
    family="My Company",
    extensions=[".my", ".rom"],
    path_pattern="my-platform",
),
```

Place ROMs in a directory whose path contains `my-platform` — e.g., `/roms/my-company/my-platform/game.rom`.
