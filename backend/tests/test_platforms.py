"""Tests for the platform registry."""
from app.scanner.platforms import (
    PLATFORMS,
    get_platform_by_extension,
    get_platform_by_slug,
    get_all_platforms,
    get_platforms_by_family,
    guess_platform_from_path,
    PlatformInfo,
)


class TestPlatformRegistry:
    """Tests for the PLATFORMS registry."""

    def test_platform_count(self):
        """Should have 100+ platforms."""
        assert len(PLATFORMS) >= 100

    def test_all_platforms_have_required_fields(self):
        """Every platform should have slug, name, family, extensions."""
        for slug, platform in PLATFORMS.items():
            assert isinstance(platform, PlatformInfo)
            assert platform.slug == slug
            assert platform.name
            assert platform.family
            assert platform.extensions
            assert isinstance(platform.extensions, list)
            assert len(platform.extensions) > 0

    def test_nintendo_platforms(self):
        """Nintendo family should include major Nintendo consoles."""
        nintendo_slugs = [
            "nes", "snes", "n64", "gamecube", "wii", "wiiu",
            "switch", "nds", "3ds", "gameboy", "gameboycolor",
            "gameboyadvance", "virtualboy",
        ]
        for slug in nintendo_slugs:
            assert slug in PLATFORMS, f"Missing Nintendo platform: {slug}"
            assert PLATFORMS[slug].family == "nintendo"

    def test_sony_platforms(self):
        """Sony family should include PlayStation consoles."""
        for slug in ["psx", "ps2", "ps3", "ps4", "psp", "vita"]:
            assert slug in PLATFORMS, f"Missing Sony platform: {slug}"
            assert PLATFORMS[slug].family == "sony"

    def test_sega_platforms(self):
        """Sega family should include major Sega consoles."""
        for slug in [
            "mastersystem", "megadrive", "segacd", "saturn",
            "dreamcast", "gamegear", "sg1000", "sega32x",
        ]:
            assert slug in PLATFORMS, f"Missing Sega platform: {slug}"
            assert PLATFORMS[slug].family == "sega"

    def test_arcade_platforms(self):
        """Arcade platforms should be present."""
        for slug in ["arcade", "neogeo", "neogeocd", "fbneo", "mame", "fba"]:
            assert slug in PLATFORMS, f"Missing arcade platform: {slug}"
            assert PLATFORMS[slug].family == "arcade"

    def test_atari_platforms(self):
        """Atari platforms should be present."""
        for slug in ["atari2600", "atari7800", "atarilynx", "atarist", "atarifalcon"]:
            assert slug in PLATFORMS, f"Missing Atari platform: {slug}"
            assert PLATFORMS[slug].family == "atari"

    def test_amiga_platforms(self):
        """Amiga platforms should be present."""
        for slug in ["amiga500", "amiga1200", "amigacd32"]:
            assert slug in PLATFORMS, f"Missing Amiga platform: {slug}"
            assert PLATFORMS[slug].family == "amiga"

    def test_scummvm(self):
        """ScummVM should be in platforms."""
        assert "scummvm" in PLATFORMS

    def test_no_duplicate_slugs(self):
        """No duplicate platform slugs."""
        slugs = list(PLATFORMS.keys())
        assert len(slugs) == len(set(slugs))


class TestGetPlatformByExtension:
    """Tests for get_platform_by_extension function."""

    def test_nes_extension(self):
        """get_platform_by_extension('.nes') should return nes platform."""
        result = get_platform_by_extension(".nes")
        assert result is not None
        assert result.slug == "nes"

    def test_sfc_extension(self):
        """.sfc should map to snes."""
        result = get_platform_by_extension(".sfc")
        assert result is not None
        assert result.slug == "snes"

    def test_smc_extension(self):
        """.smc should map to snes."""
        result = get_platform_by_extension(".smc")
        assert result is not None
        assert result.slug == "snes"

    def test_z64_extension(self):
        """.z64 should map to n64."""
        result = get_platform_by_extension(".z64")
        assert result is not None
        assert result.slug == "n64"

    def test_gba_extension(self):
        """.gba should map to gameboyadvance."""
        result = get_platform_by_extension(".gba")
        assert result is not None
        assert result.slug == "gameboyadvance"

    def test_md_extension(self):
        """.md should map to megadrive."""
        result = get_platform_by_extension(".md")
        assert result is not None
        assert result.slug == "megadrive"

    def test_gen_extension(self):
        """.gen should map to megadrive."""
        result = get_platform_by_extension(".gen")
        assert result is not None
        assert result.slug == "megadrive"

    def test_case_insensitive(self):
        """Extension lookup should be case insensitive."""
        assert get_platform_by_extension(".NES") is not None
        assert get_platform_by_extension(".GBA") is not None

    def test_without_dot(self):
        """Should work without leading dot."""
        result = get_platform_by_extension("nes")
        assert result is not None
        assert result.slug == "nes"

    def test_unknown_extension(self):
        """Unknown extension should return None."""
        result = get_platform_by_extension(".xyzabc")
        assert result is None


class TestGuessPlatformFromPath:
    """Tests for guess_platform_from_path function."""

    def test_path_with_snes(self):
        """/roms/nintendo/snes/ should return snes platform."""
        result = guess_platform_from_path("/roms/nintendo/snes/")
        assert result is not None
        assert result.slug == "snes"

    def test_path_with_psx(self):
        """/roms/sony/psx/ should return psx platform."""
        result = guess_platform_from_path("/roms/sony/psx/")
        assert result is not None
        assert result.slug == "psx"

    def test_path_case_insensitive(self):
        """Path detection should be case insensitive."""
        result = guess_platform_from_path("/roms/NINTENDO/SNES/")
        assert result is not None
        assert result.slug == "snes"

    def test_path_with_switch(self):
        """/roms/nintendo/switch/ should return switch platform."""
        result = guess_platform_from_path("/roms/nintendo/switch/")
        assert result is not None
        assert result.slug == "switch"

    def test_path_with_psp(self):
        """psp in path should return psp platform."""
        result = guess_platform_from_path("/data/roms/psp/")
        assert result is not None
        assert result.slug == "psp"

    def test_unknown_path(self):
        """Unknown path should return None."""
        result = guess_platform_from_path("/some/random/path/that/means/nothing/")
        assert result is None


class TestGetPlatformsByFamily:
    """Tests for get_platforms_by_family function."""

    def test_nintendo_family(self):
        """Should return all Nintendo platforms."""
        nintendo = get_platforms_by_family("nintendo")
        assert len(nintendo) >= 10
        assert all(p.family == "nintendo" for p in nintendo)

    def test_sony_family(self):
        """Should return all Sony platforms."""
        sony = get_platforms_by_family("sony")
        assert len(sony) >= 5
        assert all(p.family == "sony" for p in sony)

    def test_sega_family(self):
        """Should return all Sega platforms."""
        sega = get_platforms_by_family("sega")
        assert len(sega) >= 5
        assert all(p.family == "sega" for p in sega)

    def test_unknown_family(self):
        """Unknown family should return empty list."""
        result = get_platforms_by_family("nonexistent_family_xyz")
        assert result == []


class TestGetAllPlatforms:
    """Tests for get_all_platforms function."""

    def test_returns_list(self):
        """Should return a list."""
        result = get_all_platforms()
        assert isinstance(result, list)

    def test_count_matches(self):
        """Count should match PLATFORMS dict."""
        assert len(get_all_platforms()) == len(PLATFORMS)


class TestGetPlatformBySlug:
    """Tests for get_platform_by_slug function."""

    def test_valid_slug(self):
        """Valid slug should return platform."""
        result = get_platform_by_slug("snes")
        assert result is not None
        assert result.slug == "snes"

    def test_invalid_slug(self):
        """Invalid slug should return None."""
        result = get_platform_by_slug("nonexistent_slug_xyz")
        assert result is None

    def test_case_insensitive(self):
        """Slug lookup should be case insensitive."""
        result = get_platform_by_slug("SNES")
        assert result is not None
        assert result.slug == "snes"
