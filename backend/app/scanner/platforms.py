"""Complete Batocera platform registry with extensions, path patterns, and families."""
from dataclasses import dataclass
import re
from typing import Optional


@dataclass
class PlatformInfo:
    """Platform information container."""
    slug: str
    name: str
    family: Optional[str]
    extensions: list[str]
    path_pattern: str


PLATFORMS: dict[str, PlatformInfo] = {
    # Nintendo
    "nes": PlatformInfo("nes", "Nintendo Entertainment System", "nintendo", ["nes", "fds", "zip", "7z"], "nes"),
    "snes": PlatformInfo("snes", "Super Nintendo", "nintendo", ["sfc", "smc", "swc", "fig", "zip", "7z"], "snes"),
    "n64": PlatformInfo("n64", "Nintendo 64", "nintendo", ["z64", "n64", "v64", "rom", "zip", "7z"], "n64"),
    "n64dd": PlatformInfo("n64dd", "Nintendo 64DD", "nintendo", ["z64", "n64", "v64", "d64", "ndd", "zip", "7z"], "n64dd"),
    "gamecube": PlatformInfo("gamecube", "Nintendo GameCube", "nintendo", ["gcm", "iso", "ciso", "gcz", "rvz", "wad"], "gamecube"),
    "wii": PlatformInfo("wii", "Nintendo Wii", "nintendo", ["iso", "gcm", "wbfs", "ciso", "gcz", "rvz", "wad"], "wii"),
    "wiiu": PlatformInfo("wiiu", "Nintendo Wii U", "nintendo", ["wux", "iso", "wad", "wua", "rpx"], "wiiu"),
    "switch": PlatformInfo("switch", "Nintendo Switch", "nintendo", ["nsp", "xci", "nro", "nso", "nsz"], "switch"),
    "gameboy": PlatformInfo("gameboy", "Game Boy", "nintendo", ["gb", "dmg", "zip", "7z"], "gameboy"),
    "gameboyadvance": PlatformInfo("gameboyadvance", "Game Boy Advance", "nintendo", ["gba", "agb", "zip", "7z"], "gameboyadvance"),
    "gameboycolor": PlatformInfo("gameboycolor", "Game Boy Color", "nintendo", ["gbc", "cgb", "zip", "7z"], "gameboycolor"),
    "virtualboy": PlatformInfo("virtualboy", "Virtual Boy", "nintendo", ["vb", "vboy", "zip", "7z"], "virtualboy"),
    "nds": PlatformInfo("nds", "Nintendo DS", "nintendo", ["nds", "ids", "nitro", "zip", "7z"], "nds"),
    "3ds": PlatformInfo("3ds", "Nintendo 3DS", "nintendo", ["3ds", "cci", "ctr", "pdg", "cia"], "3ds"),
    "gameandwatch": PlatformInfo("gameandwatch", "Game & Watch", "nintendo", ["gw", "mgw", "zip", "7z"], "gameandwatch"),
    "pokemini": PlatformInfo("pokemini", "Pokemon Mini", "nintendo", ["min", "bin", "zip", "7z"], "pokemini"),

    # Sony
    "psx": PlatformInfo("psx", "PlayStation", "sony", ["cue", "bin", "iso", "pbp", "chd", "img", "mdf"], "psx"),
    "ps2": PlatformInfo("ps2", "PlayStation 2", "sony", ["iso", "bin", "ngr", "chd", "gz", "mdf"], "ps2"),
    "ps3": PlatformInfo("ps3", "PlayStation 3", "sony", ["iso", "bin", "pkg", "rap"], "ps3"),
    "ps4": PlatformInfo("ps4", "PlayStation 4", "sony", ["pkg", "rap", "trp"], "ps4"),
    "ps5": PlatformInfo("ps5", "PlayStation 5", "sony", ["pkg", "trp"], "ps5"),
    "psp": PlatformInfo("psp", "PlayStation Portable", "sony", ["iso", "cso", "pbp", "prx", "chd"], "psp"),
    "vita": PlatformInfo("vita", "PlayStation Vita", "sony", ["vpk", "iso", "cso", "pkg"], "vita"),

    # Sega
    "megadrive": PlatformInfo("megadrive", "Mega Drive / Genesis", "sega", ["md", "gen", "bin", "smd", "mdg", "zip", "7z"], "megadrive"),
    "mastersystem": PlatformInfo("mastersystem", "Master System", "sega", ["sms", "bin", "rom", "zip", "7z"], "mastersystem"),
    "gamegear": PlatformInfo("gamegear", "Game Gear", "sega", ["gg", "bin", "sms", "zip", "7z"], "gamegear"),
    "segacd": PlatformInfo("segacd", "Sega CD", "sega", ["iso", "bin", "cue", "chd"], "segacd"),
    "saturn": PlatformInfo("saturn", "Sega Saturn", "sega", ["iso", "bin", "cue", "chd", "mdf"], "saturn"),
    "dreamcast": PlatformInfo("dreamcast", "Dreamcast", "sega", ["gdi", "iso", "bin", "cue", "chd", "cdi"], "dreamcast"),
    "sg1000": PlatformInfo("sg1000", "SG-1000", "sega", ["sg", "bin", "rom", "zip", "7z"], "sg1000"),
    "sega32x": PlatformInfo("sega32x", "Sega 32X", "sega", ["32x", "smd", "bin", "md", "zip", "7z"], "sega32x"),

    # Arcade
    "mame": PlatformInfo("mame", "MAME", "arcade", ["zip", "7z", "chd"], "mame"),
    "arcade": PlatformInfo("arcade", "Arcade", "arcade", ["7z", "uae", "zip"], "arcade"),
    "neogeo": PlatformInfo("neogeo", "Neo Geo", "arcade", ["zip", "7z", "neo", "ngc"], "neogeo"),
    "neogeocd": PlatformInfo("neogeocd", "Neo Geo CD", "arcade", ["iso", "bin", "cue", "chd"], "neogeocd"),
    "fbneo": PlatformInfo("fbneo", "Final Burn Neo", "arcade", ["zip", "fbn", "neo"], "fbneo"),
    "fba": PlatformInfo("fba", "FBA (Final Burn Alpha)", "arcade", ["zip", "fba"], "fba"),

    # Atari
    "atari2600": PlatformInfo("atari2600", "Atari 2600", "atari", ["a26", "bin", "rom", "zip", "7z"], "atari2600"),
    "atari5200": PlatformInfo("atari5200", "Atari 5200", "atari", ["a52", "bin", "rom", "zip", "7z"], "atari5200"),
    "atari7800": PlatformInfo("atari7800", "Atari 7800", "atari", ["a78", "bin", "rom", "zip", "7z"], "atari7800"),
    "atarilynx": PlatformInfo("atarilynx", "Atari Lynx", "atari", ["lnx", "o", "zip", "7z"], "atarilynx"),
    "atarijaguar": PlatformInfo("atarijaguar", "Atari Jaguar", "atari", ["jag", "bin", "iso", "j64", "zip", "7z"], "atarijaguar"),
    "atarist": PlatformInfo("atarist", "Atari ST", "atari", ["st", "msa", "dim", "ipf", "zip", "7z"], "atarist"),

    # Microsoft
    "xbox": PlatformInfo("xbox", "Xbox", "microsoft", ["iso", "bin", "img", "xbe", "zip", "7z"], "xbox"),
    "xbox360": PlatformInfo("xbox360", "Xbox 360", "microsoft", ["iso", "xex", "stfs"], "xbox360"),

    # Others
    "pc": PlatformInfo("pc", "PC (x86)", "pc", ["exe", "com", "bat", "dosz", "zip", "7z"], "pc"),
    "msx": PlatformInfo("msx", "MSX", "msx", ["cas", "dsk", "msx", "mx1", "mx2", "rom", "zip", "7z"], "msx"),
    "pce": PlatformInfo("pce", "TurboGrafx-16/PC Engine", "nec", ["pce", "bin", "iso", "chd", "zip", "7z"], "pce"),
    "3do": PlatformInfo("3do", "3DO", "3do", ["iso", "bin", "cue", "chd"], "3do"),
    "ngp": PlatformInfo("ngp", "Neo Geo Pocket", "snk", ["ngp", "ngc", "zip", "7z"], "ngp"),
    "ngpc": PlatformInfo("ngpc", "Neo Geo Pocket Color", "snk", ["ngc", "ngp", "zip", "7z"], "ngpc"),
    "ws": PlatformInfo("ws", "WonderSwan", "waninkoko", ["ws", "wsc", "zip", "7z"], "ws"),
    "wsc": PlatformInfo("wsc", "WonderSwan Color", "waninkoko", ["wsc", "ws", "zip", "7z"], "wsc"),
}

PLATFORMS.update({
    # Amiga / Commodore
    "amiga500": PlatformInfo("amiga500", "Amiga 500", "amiga", ["adf", "adz", "lha", "hdf", "ipf", "zip", "7z"], "amiga500"),
    "amiga1200": PlatformInfo("amiga1200", "Amiga 1200", "amiga", ["adf", "adz", "lha", "hdf", "ipf", "zip", "7z"], "amiga1200"),
    "amigacd32": PlatformInfo("amigacd32", "Amiga CD32", "amiga", ["cue", "iso", "chd", "zip", "7z"], "amigacd32"),
    "amigacdtv": PlatformInfo("amigacdtv", "Amiga CDTV", "amiga", ["cue", "iso", "chd", "zip", "7z"], "amigacdtv"),
    "c64": PlatformInfo("c64", "Commodore 64", "commodore", ["d64", "t64", "tap", "crt", "prg", "zip", "7z"], "c64"),
    "c128": PlatformInfo("c128", "Commodore 128", "commodore", ["d64", "t64", "tap", "crt", "prg", "zip", "7z"], "c128"),
    "vic20": PlatformInfo("vic20", "Commodore VIC-20", "commodore", ["20", "40", "60", "a0", "b0", "crt", "prg", "zip"], "vic20"),
    "plus4": PlatformInfo("plus4", "Commodore Plus/4", "commodore", ["d64", "tap", "prg", "zip", "7z"], "plus4"),

    # Atari
    "atarifalcon": PlatformInfo("atarifalcon", "Atari Falcon", "atari", ["st", "msa", "dim", "ipf", "zip", "7z"], "atarifalcon"),
    "atari800": PlatformInfo("atari800", "Atari 800", "atari", ["atr", "xfd", "atx", "cas", "car", "rom", "zip"], "atari800"),
    "atarixe": PlatformInfo("atarixe", "Atari XE", "atari", ["atr", "xfd", "atx", "cas", "car", "rom", "zip"], "atarixe"),
    "ataritt": PlatformInfo("ataritt", "Atari TT", "atari", ["st", "msa", "dim", "ipf", "zip", "7z"], "ataritt"),

    # Computers / ports
    "scummvm": PlatformInfo("scummvm", "ScummVM", "ports", ["scummvm", "svm", "zip", "7z"], "scummvm"),
    "dos": PlatformInfo("dos", "DOS", "pc", ["dosz", "zip", "7z", "exe", "bat", "com"], "dos"),
    "windows": PlatformInfo("windows", "Windows", "pc", ["exe", "msi", "zip", "7z"], "windows"),
    "macintosh": PlatformInfo("macintosh", "Apple Macintosh", "apple", ["dsk", "img", "sit", "zip", "7z"], "macintosh"),
    "apple2": PlatformInfo("apple2", "Apple II", "apple", ["dsk", "do", "po", "nib", "woz", "zip"], "apple2"),
    "apple2gs": PlatformInfo("apple2gs", "Apple IIGS", "apple", ["2mg", "dsk", "po", "zip", "7z"], "apple2gs"),
    "x68000": PlatformInfo("x68000", "Sharp X68000", "sharp", ["dim", "xdf", "hdm", "2hd", "zip", "7z"], "x68000"),
    "fmtowns": PlatformInfo("fmtowns", "FM Towns", "fujitsu", ["cue", "iso", "chd", "zip", "7z"], "fmtowns"),
    "pc88": PlatformInfo("pc88", "NEC PC-8801", "nec", ["d88", "u88", "m3u", "zip", "7z"], "pc88"),
    "pc98": PlatformInfo("pc98", "NEC PC-9801", "nec", ["d88", "fdi", "hdi", "nhd", "zip", "7z"], "pc98"),
    "zx81": PlatformInfo("zx81", "ZX81", "sinclair", ["p", "tzx", "tap", "zip", "7z"], "zx81"),
    "zxspectrum": PlatformInfo("zxspectrum", "ZX Spectrum", "sinclair", ["tzx", "tap", "z80", "sna", "zip", "7z"], "zxspectrum"),
    "samcoupe": PlatformInfo("samcoupe", "SAM Coupe", "mgt", ["dsk", "mgt", "sbt", "zip"], "samcoupe"),
    "thomson": PlatformInfo("thomson", "Thomson MO/TO", "thomson", ["fd", "sap", "k7", "zip", "7z"], "thomson"),
    "oric": PlatformInfo("oric", "Oric", "tangerine", ["tap", "dsk", "zip", "7z"], "oric"),
    "bk": PlatformInfo("bk", "Elektronika BK", "electronika", ["bin", "zip", "7z"], "bk"),

    # Consoles / handhelds
    "colecovision": PlatformInfo("colecovision", "ColecoVision", "coleco", ["col", "rom", "bin", "zip", "7z"], "colecovision"),
    "intellivision": PlatformInfo("intellivision", "Intellivision", "mattel", ["int", "bin", "rom", "zip", "7z"], "intellivision"),
    "odyssey2": PlatformInfo("odyssey2", "Magnavox Odyssey 2", "magnavox", ["bin", "zip", "7z"], "odyssey2"),
    "vectrex": PlatformInfo("vectrex", "Vectrex", "gce", ["vec", "bin", "zip", "7z"], "vectrex"),
    "supervision": PlatformInfo("supervision", "Watara Supervision", "watara", ["sv", "bin", "zip", "7z"], "supervision"),
    "megaduck": PlatformInfo("megaduck", "Mega Duck", "creativision", ["bin", "zip", "7z"], "megaduck"),
    "uzebox": PlatformInfo("uzebox", "Uzebox", "uzebox", ["uze", "hex", "zip"], "uzebox"),
    "tic80": PlatformInfo("tic80", "TIC-80", "fantasy", ["tic", "zip"], "tic80"),
    "pico8": PlatformInfo("pico8", "PICO-8", "fantasy", ["p8", "zip"], "pico8"),
    "lowresnx": PlatformInfo("lowresnx", "LowRes NX", "fantasy", ["nx", "zip"], "lowresnx"),
    "channelf": PlatformInfo("channelf", "Fairchild Channel F", "fairchild", ["bin", "chf", "zip"], "channelf"),
    "arcadia": PlatformInfo("arcadia", "Arcadia 2001", "arcadia", ["bin", "zip", "7z"], "arcadia"),
    "creativision": PlatformInfo("creativision", "CreatiVision", "vtech", ["bin", "rom", "zip"], "creativision"),
    "pv1000": PlatformInfo("pv1000", "Casio PV-1000", "casio", ["bin", "zip"], "pv1000"),
    "socrates": PlatformInfo("socrates", "VTech Socrates", "vtech", ["bin", "zip"], "socrates"),

    # Arcade boards / engines
    "atomiswave": PlatformInfo("atomiswave", "Atomiswave", "arcade", ["zip", "7z", "lst"], "atomiswave"),
    "naomi": PlatformInfo("naomi", "Sega NAOMI", "arcade", ["zip", "7z", "lst", "bin"], "naomi"),
    "naomi2": PlatformInfo("naomi2", "Sega NAOMI 2", "arcade", ["zip", "7z", "lst", "bin"], "naomi2"),
    "model2": PlatformInfo("model2", "Sega Model 2", "arcade", ["zip", "7z"], "model2"),
    "model3": PlatformInfo("model3", "Sega Model 3", "arcade", ["zip", "7z"], "model3"),
    "daphne": PlatformInfo("daphne", "Daphne", "arcade", ["daphne", "zip"], "daphne"),
    "hypseus": PlatformInfo("hypseus", "Hypseus Singe", "arcade", ["singe", "zip"], "hypseus"),
})


def get_platform_by_extension(extension: str) -> Optional[PlatformInfo]:
    """Get platform info by file extension."""
    extension = extension.lower().lstrip(".")
    for platform in PLATFORMS.values():
        if extension in platform.extensions:
            return platform
    return None


def get_platform_by_slug(slug: str) -> Optional[PlatformInfo]:
    """Get platform info by slug."""
    return PLATFORMS.get(slug.lower())


def get_all_platforms() -> list[PlatformInfo]:
    """Get all registered platforms."""
    return list(PLATFORMS.values())


def get_platforms_by_family(family: str) -> list[PlatformInfo]:
    """Get all platforms in a family."""
    return [p for p in PLATFORMS.values() if p.family == family.lower()]


def guess_platform_from_path(path: str) -> Optional[PlatformInfo]:
    """Guess platform from file path."""
    path_lower = path.lower()
    path_parts = [part for part in re.split(r"[^a-z0-9]+", path_lower) if part]

    for platform in sorted(PLATFORMS.values(), key=lambda p: len(p.slug), reverse=True):
        if platform.slug in path_parts or platform.path_pattern in path_parts:
            return platform

    for platform in sorted(PLATFORMS.values(), key=lambda p: len(p.slug), reverse=True):
        pattern = rf"(?<![a-z0-9]){re.escape(platform.slug)}(?![a-z0-9])"
        if re.search(pattern, path_lower):
            return platform
    return None
