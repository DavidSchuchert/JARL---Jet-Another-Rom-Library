"""ROM filename parser for extracting metadata from filenames."""
import re
from pathlib import PurePath
from typing import Optional


REGION_TAGS: dict[str, str] = {
    "usa": "USA",
    "us": "USA",
    "america": "USA",
    "ntsc": "USA",
    "ntsc-u": "USA",
    "ntsc-j": "Japan",
    "japan": "Japan",
    "jp": "Japan",
    "jap": "Japan",
    "pal": "Europe",
    "europe": "Europe",
    "eu": "Europe",
    "france": "France",
    "fr": "France",
    "germany": "Germany",
    "de": "Germany",
    "uk": "UK",
    "united kingdom": "UK",
    "england": "UK",
    "spain": "Spain",
    "es": "Spain",
    "italy": "Italy",
    "it": "Italy",
    "netherlands": "Netherlands",
    "nl": "Netherlands",
    "russia": "Russia",
    "ru": "Russia",
    "asia": "Asia",
    "china": "China",
    "korea": "Korea",
    "kr": "Korea",
    "hong kong": "Hong Kong",
    "hk": "Hong Kong",
    "taiwan": "Taiwan",
    "tw": "Taiwan",
    "world": "World",
    "worldwide": "World",
    "brazil": "Brazil",
    "br": "Brazil",
    "argentina": "Argentina",
    "latam": "Latin America",
    "australia": "Australia",
    "au": "Australia",
    "canada": "Canada",
    "ca": "Canada",
    "sweden": "Sweden",
    "se": "Sweden",
    "poland": "Poland",
    "pl": "Poland",
    "czech": "Czech",
    "cz": "Czech",
    "hungary": "Hungary",
    "hu": "Hungary",
    "greece": "Greece",
    "gr": "Greece",
    "turkey": "Turkey",
    "tr": "Turkey",
    "dubai": "Dubai",
    "uae": "UAE",
    "singapore": "Singapore",
    "sg": "Singapore",
    "thailand": "Thailand",
    "th": "Thailand",
    "indonesia": "Indonesia",
    "id": "Indonesia",
    "malaysia": "Malaysia",
    "my": "Malaysia",
    "philippines": "Philippines",
    "ph": "Philippines",
}

LANGUAGE_TAGS: dict[str, str] = {
    "en": "English",
    "eng": "English",
    "english": "English",
    "ja": "Japanese",
    "jpn": "Japanese",
    "japanese": "Japanese",
    "fr": "French",
    "fre": "French",
    "french": "French",
    "de": "German",
    "ger": "German",
    "german": "German",
    "es": "Spanish",
    "spa": "Spanish",
    "spanish": "Spanish",
    "it": "Italian",
    "ita": "Italian",
    "italian": "Italian",
    "pt": "Portuguese",
    "por": "Portuguese",
    "portuguese": "Portuguese",
    "br": "Portuguese (Brazil)",
    "pt-br": "Portuguese (Brazil)",
    "ru": "Russian",
    "rus": "Russian",
    "russian": "Russian",
    "ko": "Korean",
    "kor": "Korean",
    "korean": "Korean",
    "zh": "Chinese",
    "chi": "Chinese",
    "chinese": "Chinese",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "zh_cn": "Chinese (Simplified)",
    "zh_tw": "Chinese (Traditional)",
    "nl": "Dutch",
    "dut": "Dutch",
    "dutch": "Dutch",
    "sv": "Swedish",
    "swe": "Swedish",
    "swedish": "Swedish",
    "no": "Norwegian",
    "nor": "Norwegian",
    "norwegian": "Norwegian",
    "da": "Danish",
    "dan": "Danish",
    "danish": "Danish",
    "fi": "Finnish",
    "fin": "Finnish",
    "finnish": "Finnish",
    "pl": "Polish",
    "pol": "Polish",
    "polish": "Polish",
    "cs": "Czech",
    "cze": "Czech",
    "czech": "Czech",
    "hu": "Hungarian",
    "hun": "Hungarian",
    "hungarian": "Hungarian",
    "tr": "Turkish",
    "tur": "Turkish",
    "turkish": "Turkish",
    "el": "Greek",
    "gre": "Greek",
    "greek": "Greek",
    "ar": "Arabic",
    "ara": "Arabic",
    "arabic": "Arabic",
    "he": "Hebrew",
    "heb": "Hebrew",
    "hebrew": "Hebrew",
    "th": "Thai",
    "tha": "Thai",
    "thai": "Thai",
    "vi": "Vietnamese",
    "vie": "Vietnamese",
    "vietnamese": "Vietnamese",
    "id": "Indonesian",
    "ind": "Indonesian",
    "indonesian": "Indonesian",
    "ms": "Malay",
    "may": "Malay",
    "malay": "Malay",
    "multi": "Multi",
    "m": "Multi",
}


def parse_region(region_str: str) -> Optional[str]:
    """Parse region string to normalized region name."""
    region_lower = region_str.lower().strip()
    return REGION_TAGS.get(region_lower)


def parse_language(lang_str: str) -> Optional[str]:
    """Parse language string to normalized language name."""
    lang_lower = lang_str.lower().strip()
    return LANGUAGE_TAGS.get(lang_lower)


def parse_version(version_str: str) -> Optional[str]:
    """Parse version string."""
    version_str = version_str.strip()
    version_patterns = [
        r"v(?:ersion)?\.?\s*(\d+(?:\.\d+)*(?:[a-z])?)",
        r"rev(?:ision)?\.?\s*(\d+)",
        r"version\s*(\d+(?:\.\d+)*(?:[a-z])?)",
        r"^(\d+(?:\.\d+)*(?:[a-z])?)$",
    ]
    for pattern in version_patterns:
        match = re.search(pattern, version_str, re.IGNORECASE)
        if match:
            return match.group(1)
    return version_str if version_str else None


def parse_filename(filename: str) -> dict[str, Optional[str | list[str]]]:
    """
    Parse a ROM filename to extract metadata.

    Examples:
        "Game (Europe) (En) (v1.2).zip" -> {title: "Game", region: "Europe", languages: ["English"], version: "1.2"}
        "Sonic The Hedgehog (USA, Europe) (Rev 1).zip" -> {title: "Sonic The Hedgehog", region: "USA, Europe"}
        "RPG Maker (Japan).iso" -> {title: "RPG Maker", region: "Japan"}

    Args:
        filename: The filename to parse (without extension).

    Returns:
        Dictionary with parsed metadata: title, region, languages, version.
    """
    result: dict[str, Optional[str | list[str]]] = {
        "title": None,
        "region": None,
        "languages": None,
        "version": None,
        "extra": None,
    }

    original = filename
    filename = PurePath(filename).name
    filename = re.sub(r"\.[A-Za-z0-9]{1,8}$", "", filename)

    def consume_metadata_group(match: re.Match[str]) -> str:
        region_content = match.group(1)
        regions: list[str] = []
        languages: list[str] = []
        rest_parts: list[str] = []
        parts = [part.strip() for part in region_content.split(",") if part.strip()]
        treat_as_languages = bool(parts) and all(parse_language(part) for part in parts) and not all(
            parse_region(part) for part in parts
        )

        for part in parts:
            part_lower = part.lower()

            if re.match(r"^(?:v(?:ersion)?\.?|version|rev(?:ision)?\.?)\s*\d", part_lower):
                if not result["version"]:
                    result["version"] = parse_version(part)
                continue

            if treat_as_languages:
                parsed_lang = parse_language(part)
                if parsed_lang:
                    languages.append(parsed_lang)
                    continue

            parsed_region = parse_region(part)
            if parsed_region:
                regions.append(parsed_region)
                continue

            parsed_lang = parse_language(part)
            if parsed_lang:
                languages.append(parsed_lang)
                continue

            rest_parts.append(part)

        if regions:
            result["region"] = ", ".join(regions)
        if languages:
            result["languages"] = languages
        if rest_parts:
            result["extra"] = ", ".join(rest_parts)
        return "" if parts and not rest_parts else match.group(0)

    filename = re.sub(r"\s*[\(\[]([^\)\]]+)[\)\]]", consume_metadata_group, filename)

    version_match = re.search(
        r"[\s_-]+(?:v(?:ersion)?\.?\s*)(\d+(?:\.\d+)*(?:[a-z])?)$",
        filename,
        re.IGNORECASE,
    )
    if version_match:
        result["version"] = parse_version(version_match.group(0))
        filename = filename[: version_match.start()].strip()

    # Clean up title
    if result["title"] is None:
        title = filename.replace("_", " ").strip()
        # Remove trailing parentheses and brackets with content
        title = re.sub(r"[\s\-_]+\(\s*\)", "", title)
        title = re.sub(r"[\s\-_]+\[\s*\]", "", title)
        title = re.sub(r"\s+", " ", title)
        title = title.strip(" -_")
        result["title"] = title or original

    return result


def build_filename_from_parsed(parsed: dict[str, Optional[str | list[str]]]) -> str:
    """Build a filename from parsed metadata (inverse of parse_filename)."""
    parts: list[str] = []

    if parsed.get("title"):
        parts.append(parsed["title"])

    metadata_parts: list[str] = []

    if parsed.get("region"):
        metadata_parts.append(parsed["region"])

    if parsed.get("languages"):
        langs = parsed["languages"]
        if isinstance(langs, list):
            metadata_parts.append(", ".join(langs))
        else:
            metadata_parts.append(str(langs))

    if parsed.get("extra"):
        metadata_parts.append(parsed["extra"])

    if parsed.get("version"):
        v = parsed["version"]
        metadata_parts.append(f"v{v}" if not str(v).startswith("v") else str(v))

    if metadata_parts:
        parts.append("(" + ", ".join(metadata_parts) + ")")

    return " ".join(parts)
