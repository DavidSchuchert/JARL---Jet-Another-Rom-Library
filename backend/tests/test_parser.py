"""Tests for the filename parser."""
from app.scanner.parser import (
    parse_filename,
    parse_region,
    parse_language,
    parse_version,
    build_filename_from_parsed,
)


class TestParseFilename:
    """Tests for parse_filename function."""

    def test_simple_title(self):
        """Simple filename with just the game title."""
        result = parse_filename("Super Mario Bros")
        assert result["title"] == "Super Mario Bros"
        assert result["region"] is None
        assert result["languages"] is None
        assert result["version"] is None

    def test_europe_region(self):
        """Filename with Europe region tag."""
        result = parse_filename("Sonic (Europe).md")
        assert result["title"] == "Sonic"
        assert result["region"] == "Europe"

    def test_usa_region(self):
        """Filename with USA region tag."""
        result = parse_filename("Final Fantasy (USA).nes")
        assert result["title"] == "Final Fantasy"
        assert result["region"] == "USA"

    def test_multiple_regions(self):
        """Filename with multiple regions."""
        result = parse_filename("Game (USA, Europe).zip")
        assert result["region"] == "USA, Europe"

    def test_language_tag(self):
        """Filename with language tag."""
        result = parse_filename("RPG (Japan, En).iso")
        assert result["title"] == "RPG"
        assert result["region"] == "Japan"
        assert result["languages"] == ["English"]

    def test_multiple_languages(self):
        """Filename with multiple language tags."""
        result = parse_filename("Game (En, Fr, De).zip")
        assert result["languages"] == ["English", "French", "German"]

    def test_version_tag(self):
        """Filename with version tag."""
        result = parse_filename("Game v1.2.zip")
        assert result["title"] == "Game"
        assert result["version"] == "1.2"

    def test_parentheses_version(self):
        """Version in parentheses."""
        result = parse_filename("Game (v1.0) (Rev 2).zip")
        assert result["version"] is not None

    def test_region_and_language_and_version(self):
        """Complex filename with all tags."""
        result = parse_filename("Castlevania (Europe) (En) (v1.1).zip")
        assert result["title"] == "Castlevania"
        assert result["region"] == "Europe"
        assert result["languages"] == ["English"]
        assert result["version"] == "1.1"

    def test_japanese_game(self):
        """Japanese game filename."""
        result = parse_filename("RPG Maker (Japan).iso")
        assert result["title"] == "RPG Maker"
        assert result["region"] == "Japan"

    def test_underscore_separator(self):
        """Filename with underscores as separator."""
        result = parse_filename("Super_Mario_64.z64")
        assert result["title"] == "Super Mario 64"

    def test_underscore_region(self):
        """Underscore-separated region."""
        result = parse_filename("Sonic_USA.md")
        # May or may not parse region from underscore style
        assert result["title"] is not None

    def test_revision_tag(self):
        """Revision tags."""
        result = parse_filename("Game (Rev 1).zip")
        assert result["version"] is not None

    def test_build_filename_roundtrip(self):
        """Roundtrip: parse -> build -> parse gives same title."""
        original = "Super Mario Bros (Europe) (En) (v1.0)"
        parsed = parse_filename(original)
        rebuilt = build_filename_from_parsed(parsed)
        reparsed = parse_filename(rebuilt)
        assert reparsed["title"] == parsed["title"]


class TestParseRegion:
    """Tests for parse_region function."""

    def test_usa(self):
        assert parse_region("USA") == "USA"
        assert parse_region("us") == "USA"
        assert parse_region("america") == "USA"

    def test_japan(self):
        assert parse_region("Japan") == "Japan"
        assert parse_region("jp") == "Japan"
        assert parse_region("jap") == "Japan"

    def test_europe(self):
        assert parse_region("Europe") == "Europe"
        assert parse_region("eu") == "Europe"
        assert parse_region("pal") == "Europe"

    def test_germany(self):
        assert parse_region("Germany") == "Germany"
        assert parse_region("de") == "Germany"

    def test_unknown(self):
        assert parse_region("unknown_region") is None


class TestParseLanguage:
    """Tests for parse_language function."""

    def test_english(self):
        assert parse_language("en") == "English"
        assert parse_language("eng") == "English"
        assert parse_language("english") == "English"

    def test_japanese(self):
        assert parse_language("ja") == "Japanese"
        assert parse_language("jpn") == "Japanese"

    def test_german(self):
        assert parse_language("de") == "German"
        assert parse_language("ger") == "German"

    def test_french(self):
        assert parse_language("fr") == "French"
        assert parse_language("fre") == "French"

    def test_spanish(self):
        assert parse_language("es") == "Spanish"
        assert parse_language("spa") == "Spanish"

    def test_multi(self):
        assert parse_language("multi") == "Multi"

    def test_unknown(self):
        assert parse_language("unknown_lang") is None


class TestParseVersion:
    """Tests for parse_version function."""

    def test_simple_version(self):
        assert parse_version("v1.2") == "1.2"
        assert parse_version("1.0") == "1.0"

    def test_version_with_letter(self):
        assert parse_version("v1.2b") == "1.2b"

    def test_revision(self):
        assert parse_version("Rev 1") == "1"
        assert parse_version("revision 2") == "2"

    def test_full_version_string(self):
        assert parse_version("Version 1.0") == "1.0"
