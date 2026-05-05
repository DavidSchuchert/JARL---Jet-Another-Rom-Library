# Platforms

JARL auto-detects gaming platforms from directory structure and filenames.

---

## Directory Convention

JARL expects ROMs to be organized by platform:

```
/roms/
├── nintendo/nes/
│   ├── Legend of Zelda (USA).nes
│   └── Super Mario Bros. 3 (Europe).nes
├── sony/playstation-2/
│   ├── Final Fantasy X (Europe).iso
│   └── Shadow of the Colossus (USA).iso
└── sega/dreamcast/
    └── Sonic Adventure 2 (Japan).gdi
```

The first path segment (e.g., `nintendo`, `sony`, `sega`) maps to the **platform family**. The second segment (e.g., `nes`, `playstation-2`, `dreamcast`) maps to the **platform slug**.

---

## Supported Platforms

| Slug | Display Name | Family | Extensions |
|------|-------------|--------|------------|
| `nes` | Nintendo Entertainment System | Nintendo | `.nes` |
| `snes` | Super Nintendo | Nintendo | `.sfc`, `.smc` |
| `n64` | Nintendo 64 | Nintendo | `.n64`, `.z64`, `.v64` |
| `gamecube` | Nintendo GameCube | Nintendo | `.iso`, `.gcm` |
| `wii` | Nintendo Wii | Nintendo | `.iso`, `.wbfs` |
| `wii-u` | Nintendo Wii U | Nintendo | `.iso`, `.wux` |
| `switch` | Nintendo Switch | Nintendo | `.nsp`, `.xci` |
| `3ds` | Nintendo 3DS | Nintendo | `.3ds`, `.cia` |
| `ps1` | PlayStation | Sony | `.bin`, `.cue`, `.iso` |
| `ps2` | PlayStation 2 | Sony | `.iso`, `.bin` |
| `ps3` | PlayStation 3 | Sony | `.iso`, `.bin`, `.pkg` |
| `psp` | PlayStation Portable | Sony | `.iso`, `.cso` |
| `genesis` | Sega Genesis/Mega Drive | Sega | `.bin`, `.md`, `.gen` |
| `saturn` | Sega Saturn | Sega | `.bin`, `.iso` |
| `dreamcast` | Sega Dreamcast | Sega | `.gdi`, `.chd`, `.iso` |
| `gamegear` | Sega Game Gear | Sega | `.bin`, `.gg` |
| `master-system` | Sega Master System | Sega | `.bin`, `.sms` |
| `turbografx-16` | TurboGrafx-16 | NEC | `.pce`, `.bin` |
| `atari-2600` | Atari 2600 | Atari | `.a26`, `.bin` |
| `atari-7800` | Atari 7800 | Atari | `.a78`, `.bin` |
| `jaguar` | Atari Jaguar | Atari | `.jag`, `.bin` |
| `nds` | Nintendo DS | Nintendo | `.nds`, `.ids` |
| `gb` | Game Boy | Nintendo | `.gb` |
| `gbc` | Game Boy Color | Nintendo | `.gbc` |
| `gba` | Game Boy Advance | Nintendo | `.gba` |
| `xbox` | Xbox | Microsoft | `.iso`, `.bin` |
| `xbox-360` | Xbox 360 | Microsoft | `.iso`, `.xex` |
| `pc-engine` | PC Engine | NEC | (alias of `turbografx-16`) |
| `c64` | Commodore 64 | Commodore | `.d64`, `.t64` |
| `amiga` | Commodore Amiga | Commodore | `.adf`, `.ipf`, `.lha` |
| `msx` | MSX | Microsoft | `.rom`, `.msx` |
| `neogeo` | Neo Geo | SNK | `.neo`, `.zip` |
| `arcade` | MAME Arcade | Various | `.zip`, `.chd` |

---

## Adding Custom Platforms

JARL's platform registry is in `backend/app/scanner/platforms.py`. To add a new platform:

```python
PLATFORMS: dict[str, Platform] = {
    "my-platform": Platform(
        slug="my-platform",
        name="My Platform",
        family="My Company",
        extensions=[".my", ".rom"],
        patterns=[
            # Optional: additional filename patterns
            r"^(?P<title>.+?) \((?P<region>[\w\s]+)\)$",
        ],
    ),
}
```

Then add the corresponding directory structure under `/roms/my-company/my-platform/`.

---

## Platform Family Grouping

Platforms are grouped by family in the UI (Nintendo, Sony, Sega, etc.). The `family` field is used for sidebar grouping and filtering.
