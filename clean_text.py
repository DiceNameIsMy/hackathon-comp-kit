import json
import re


def clean_news_text(text):
    if not text:
        return ""

    lines = text.split("\n")
    cleaned_lines = []

    # Exact phrases to remove (lowercase for comparison)
    noise_phrases = {
        "[]",
        "[][]",
        "-",
        "reklama",
        "zdieľať",
        "sdílet",
        "advertisement",
        "celý článok",
        "kvalita",
        "rychlost přehrávání",
        "normální",
        "automatická",
        "language",
        "titulky",
        "vypnuto",
        "odber noviniek",
        "nájdite nás na google news a kliknite sledovať",
        "facebook",
        "twitter",
        "instagram",
        "e-mail",
        "kopírovať link",
        "prehrať video",
        "načítava sa",
        "video player is loading.",
        "play video",
        "pause",
        "fullscreen",
        "audio track",
        "chapters",
        "descriptions",
        "subtitles",
        "settings",
        "unmute",
        "this is a modal window.",
        "logo plus jeden deň",
        "tasr",
        "vyhledat",
        "osobní menu",
        "hlavní menu",
        "zavřít menu",
        "moje sledované",
        "domácí",
        "kauzy",
        "byznys",
        "svět",
        "názory a analýzy",
        "kultura",
        "sport",
        "magazín",
        "tech",
        "česká elita",
        "galerie osobností",
        "rozhovory",
        "obrazem",
        "kampus",
        "volby",
        "video",
        "podcasty",
        "newslettery",
        "vydali jsme",
        "čteme vám sz",
        "redakce",
        "záhlaví",
        "přeskočit intro",
        "autoplay",
        "možnosti",
        "automatický přepis",
        "velikost",
        "malé",
        "střední",
        "velké",
        "styl",
        "vržený stín",
        "tmavé",
        "světlé",
        "kontrastní",
        "pouze zvuk",
        "vypnout další video",
        "přehrát nyní",
        "sdílejte na facebooku",
        "sdílejte na síti x",
        "hdnastavenia",
        "nastavenia",
        "rýchlosť",
        "líbí",
        "nelíbí",
        "našli jste v článku chybu?",
        "byl pro vás článek přínosný?",
        "zasílat nově přidané názory e-mailem",
        "autor aktuality",
        "témata:",
        "drobečková navigace",
        "hlavní obsah",
        "související obsah",
        "/",
        "finance.czfinance.cz",
    }

    last_was_empty = False

    for line in lines:
        stripped = line.strip()
        lower_line = stripped.lower()

        # Handle empty lines (paragraph breaks)
        if not stripped:
            if not last_was_empty:
                cleaned_lines.append("")
                last_was_empty = True
            continue

        # Check for exact noise phrases
        if lower_line in noise_phrases:
            continue

        # Check for noise prefixes
        if lower_line.startswith(
            (
                "-   ",
                "foto:",
                "zdroj:",
                "autor:",
                "aktualizované",
                "stream type",
                "current time",
                "remaining time",
                "loaded:",
                "duration",
                "doba čtení:",
                "vstoupit do diskuse",
            )
        ):
            # For some prefixes, we might want to be more aggressive regardless of length
            # But keeping the length check for safety on some, usually these headers are short.
            if len(stripped) < 100:
                continue

        # Check for noise substrings (be careful here)
        if "rewind" in lower_line and len(stripped) < 20:  # e.g. "10Rewind"
            continue

        # Regex checks
        # Remove lines that are just brackets/captions e.g. [Something]
        if re.match(r"^\[.*?\]$", stripped):
            continue

        # Remove lines that are just HTML tags
        if re.match(r"^<[^>]+>$", stripped):
            continue

        # Remove timestamp-only lines e.g. 0:48 or 12:00
        if re.match(r"^\d+:\d+$", stripped):
            continue

        # Remove date lines e.g. 28. 6. 2023 or 20. 10. 2022, 13:14
        if re.match(r"^\d{1,2}\.\s*\d{1,2}\.\s*\d{4}", stripped):
            continue

        # Remove "X nových názorů" or "X názorů"
        if re.search(r"\d+\s+(nových\s+)?názorů", lower_line) and len(stripped) < 30:
            continue

        # Navigation crumbs with »
        if "»" in lower_line and len(stripped) < 150:
            continue

        # If we reached here, it's likely content.
        cleaned_lines.append(stripped)
        last_was_empty = False

    return "\n".join(cleaned_lines)


def process_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_count = 0
    total_lines_removed = 0
    total_chars_orig = 0
    total_chars_clean = 0

    for item in data["data"]:
        original_text = item.get("news_text", "")
        if not original_text:
            continue

        total_chars_orig += len(original_text)
        cleaned_text = clean_news_text(original_text)
        total_chars_clean += len(cleaned_text)

        # Calculate stats (rough estimate based on newline count)
        orig_lines = original_text.count("\n") + 1
        new_lines = cleaned_text.count("\n") + 1
        diff = orig_lines - new_lines

        if diff > 0 or len(original_text) != len(cleaned_text):
            cleaned_count += 1
            total_lines_removed += diff

        item["news_text"] = cleaned_text

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Processed {len(data['data'])} items.")
    print(f"Modified {cleaned_count} texts.")
    print(f"Removed approximately {total_lines_removed} lines/blocks of noise.")

    char_diff = total_chars_orig - total_chars_clean
    char_percent = (char_diff / total_chars_orig * 100) if total_chars_orig > 0 else 0
    print(f"Removed {char_diff} characters ({char_percent:.2f}% decrease).")


if __name__ == "__main__":
    process_file("dev.json", "dev_cleaned.json")
