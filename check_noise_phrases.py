import json

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

with open("dev.json", "r", encoding="utf-8") as f:
    data = json.load(f)

counts = {phrase: 0 for phrase in noise_phrases}

for item in data["data"]:
    text = item.get("news_text", "")
    if not text:
        continue
    lines = text.split("\n")
    for line in lines:
        stripped = line.strip().lower()
        if stripped in noise_phrases:
            counts[stripped] += 1

print("Occurrences of exact matches in dev.json:")
for phrase, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"{phrase}: {count}")
