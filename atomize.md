Jste technický analytik. Rozdělte komentář na atomární tvrzení. Často je text ve slovenštině nebo češtině.


Zachovejte záměr a formulace autora v maximální možné míře: nepřidávejte nová fakta ani nevyvozujte nevyřčená tvrzení. Vaším úkolem je POUZE oddělit a minimálně normalizovat jednotky tvrzení.


### PŘÍKLADY

Vstup: "Všichni nadávají na Rusko ale všichni od něj berou levný plyn"
Výstup (Tvrzení): "Mnoho zemí nakupuje od Ruska levný plyn"

Vstup: "Bratia Cesi, ktore noviny su to u vas?\nU nas je to DennikN, ktore vlastni ESSET a ten je pod kontrolou CIA. Potom noviny SME, kde je vlastnikom Soros."
Výstup (Tvrzení): 
- "CIA má pod kontrolov ESET."
- "Noviny SME vlastni  Soros."
- "DennikN vlastnil v roku 2023 ESET."


### VSTUPY
Komentář (Comment):
[COMMENT]


OčekávanýPočetTvrzení (ExpectedClaims - celé číslo):
[N]


### DEFINICE
Atomární tvrzení (Atomic claim) = jedna propozice, kterou lze vyhodnotit jako pravdivou/nepravdivou (včetně názorů vyjádřených jako propozice).
Ne-tvrzení (Non-claim) = čisté otázky, pozdravy nebo metatext („viz výše“ atd.).


### KROKY


Krok 1 – Extrakce kandidátních tvrzení (zatím ignorujte OčekávanýPočetTvrzení)
- Seznamte všechny propozice v Komentáři.
- Rozdělte souvětí na více tvrzení, pokud zjevně obsahují více propozic (A a B; příčina–následek; srovnání + závěr).
- Udržujte formulace blízké originálu; provádějte pouze minimální úpravy, aby každé tvrzení bylo gramaticky správné.
- NEROZPOUŠTĚJTE zájmena ani nepřidávejte chybějící kontext; ponechte „to/tento/oni“ atd. v původní podobě.
- Také samostatně sesbírejte položky typu Ne-tvrzení.


Krok 2 – Přizpůsobení OčekávanémuPočtuTvrzení s minimálními změnami
Pokud počet_kandidátních_tvrzení > OčekávanýPočetTvrzení:
- Slučujte pouze úzce související sousední tvrzení (stejný subjekt/událost/čas) jednoduchým spojením (čárka/„a“), bez přidávání obsahu.
- Neslučujte tvrzení o různých entitách, časech nebo důkazech.


Pokud počet_kandidátních_tvrzení < OčekávanýPočetTvrzení:
- Rozdělujte pouze tehdy, pokud tvrzení zjevně obsahuje více propozic (spojky, srovnání, více entit nebo metrik).
- Nevymýšlejte nová tvrzení ani nepřirozené fragmenty.


Pokud nemůžete dosáhnout přesně OčekávanéhoPočtuTvrzení bez vymýšlení obsahu nebo vytváření špatných fragmentů:
- Zůstaňte co nejblíže OčekávanémuPočtuTvrzení a explicitně uveďte, proč je přesná shoda nemožná.


Krok 3 – Označení každého finálního tvrzení pro následnou dekontextualizaci
U každého finálního tvrzení uveďte:
- Typ (Type): jeden z {Fact, Interpretation, Opinion, Recommendation, Prediction}.
- Příznaky (Flags): libovolné z
  - PronounWithoutAntecedent (Zájmeno bez antecedentu)
  - ImplicitEntity (Implicitní entita – např. „model“, „článek“)
  - TimeDependent (Časově závislé – např. „nedávno“, „nyní“)
  - Referential (Referenční – např. „výše“, „tato sekce“)
  - MetricOrThresholdMissing (Chybějící metrika nebo práh – např. „významný“, „lepší“ bez komparátoru)
- TermínyPravděpodobněVyžadujícíPozdějšíNahrazení (TermsLikelyNeedingReplacementLater): krátké úseky zkopírované z tvrzení, které budou pravděpodobně vyžadovat pozdější explicitní pojmenování (nepřepisujte je).


Krok 4 – Kontrola pokrytí
- Zajistěte, aby každá smysluplná propozice v Komentáři byla zastoupena právě v jednom tvrzení nebo položce Ne-tvrzení.
- Pokud neexistují žádná tvrzení, uveďte to a vraťte prázdný seznam tvrzení.


### FORMÁT VÝSTUPU
ExpectedClaims: <N>
FinalClaimCount: <K>


CandidateClaims:
1) "<text>"
2) ...


NonClaimItems:
1) "<text>"
2) ...


ReconciliationNotes:
- "<stručný popis sloučení/rozdělení a případně důvod, proč bylo přesné N nemožné>"


FinalClaims:
1) Text: "<tvrzení>"
   Type: <...>
   Flags: [ ... ]
   TermsLikelyNeedingReplacementLater: ["...", ...]
2) Text: "<tvrzení>"
   Type: <...>
   Flags: [ ... ]
   TermsLikelyNeedingReplacementLater: ["...", ...]
...


Pokud nebylo možné dosáhnout přesného OčekávanéhoPočtuTvrzení:
ExactMatchPossible: false
Reason: "<krátké vysvětlení, proč by dosažení přesně N vyžadovalo vymýšlení obsahu nebo vytvoření nepřirozených fragmentů>"
ClosestFeasibleClaimCount: <K>