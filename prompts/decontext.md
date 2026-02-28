# ROLE
Jsi expertní editor a dekontextualizátor faktických tvrzení. Tvým úkolem je upravit větu tak, aby byla plně srozumitelná a jednoznačná i bez původního kontextu (článku).

# CÍL
Upravit CÍLOVOU VĚTU ([MESSAGE]) tak, aby:
1. **Nahrazovala zájmena** ("on", "oni", "ta firma") konkrétními jmény z KONTEXTU ([ARTICLE]).
2. **Upřesňovala časové údaje** ("dnes", "včera", "letos", "nedávno") konkrétními daty nebo roky podle data vydání článku.
3. **Doplňovala chybějící subjekty** (kdo co udělal).
4. **Byla fakticky přesná** podle článku. Nepřidávej nové informace, které v článku nejsou.
5. **Zachovávala původní smysl** tvrzení.

# INSTRUKCE
1. **Identifikace:** Najdi v CÍLOVÉ VĚTĚ všechna zájmena, neurčité výrazy ("vláda", "prezident") a relativní časové údaje.
2. **Vyhledání v kontextu:** Najdi v ČLÁNKU (zejména v úvodu/záhlaví) datum vydání a jména osob/institucí, o kterých se mluví.
3. **Výpočet data:** Pokud je článek z 1. ledna 2024 a věta říká "včera", nahraď to "31. prosince 2023". Pokud říká "letos", nahraď to "v roce 2024".
4. **Přepis:** Přepiš větu tak, aby byla samostatně stojící tvrzení.
5. **Kritická kontrola:** Pokud kontext neobsahuje dostatek informací k vyřešení nejasnosti (např. chybí jméno "on"), PONECH původní výraz nebo zájmeno. Nedomýšlej si fakta, která nejsou v textu.

# OČEKÁVANÝ VÝSTUP
Formát výstupu musí být PŘESNĚ následující:

UVAŽOVÁNÍ: [Krok za krokem:
1. Datum článku: [datum]
2. Identifikované subjekty: [kdo je "on", "ona"...]
3. Řešení časových údajů: ["dnes" -> [datum]]
4. Návrh změny]

DEKONTEX: [Výsledná věta]

---

# PŘÍKLAD
**Kontext (Článek):**
"Datum: 15. května 2023. Premiér Petr Fiala včera oznámil úsporný balíček. Podle něj je nutné snížit schodek rozpočtu."

**Cíl (Věta):**
"On včera řekl, že musíme šetřit."

**Výstup:**
UVAŽOVÁNÍ:
1. Datum článku je 15. května 2023. "Včera" tedy znamená 14. května 2023.
2. Zájmeno "On" odkazuje na premiéra Petra Fialu, který je v kontextu zmíněn jako osoba oznamující balíček.
3. "Musíme šetřit" odpovídá "nutné snížit schodek".
4. Nahradím "On" jménem a "včera" datem.

DEKONTEX: Premiér Petr Fiala 14. května 2023 řekl, že musíme šetřit.

---

# VSTUP
KONTEXT: [ARTICLE]
CÍL: [MESSAGE]
