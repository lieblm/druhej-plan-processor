# Band Rehearsal Audio Processor

Automatizovaná pipeline pro bleskovou analýzu, segmentaci a export nahrávek ze zkoušek kapely. Skript spolehlivě identifikuje písničky na základě analýzy dynamiky a hlasitosti (RMS), ignoruje mluvení/ladění a připraví štítky pro finální ořez.

> 🎸 **Od muzikantů pro muzikanty:** Tento nástroj jsme si původně vytvořili pro zpracování našich zkoušek v kapele **Druhej plán**. Rozhodli jsme se ho ale uvolnit jako open-source – věříme totiž, že ušetří spoustu otravného stříhání a klikání i dalším muzikantům, aby se mohli soustředit na to podstatné: na muziku.

## Workflow
1. vlož záznam ze zkoušky do `data/input/`.
2. spusť analýzu: `python rehearsal_processor.py --input data/input/zkouska.mp3 --outdir data/output --mode analyze`
   - *Poznámka: Analýza celého souboru trvá jen několik vteřin. Data se ukládají do cache pro instantní opakované ladění.*
3. zkontroluj vygenerované štítky `data/output/labels.txt` v Audacity.
4. v Audacity si vizuálně posuň a uprav hrany bloků. U skladeb, které chceš exportovat, přepiš výchozí štítek "BLOK" alespoň na rychlý pracovní název (např. "a", "x" nebo hrubý název). Ty úseky, které chceš zahodit (ladění, pauzy), ponech s původním textem "BLOK" nebo je smaž. Následně štítky vyexportuj (`Soubor -> Export Other -> Export Labels...`) např. jako `final_labels.txt`.
5. otevři `final_labels.txt` v běžném textovém editoru (např. VS Code, Poznámkový blok) a v klidu dočisti pracovní názvy do finální podoby (např. "01 Heartbreaker").
   - *Tip z praxe: Psát detailní text štítků přímo v Audacity je frustrující, protože program odchytává některé klávesy (např. čísla) jako své zkratky. Proto je v Audacity lepší dát jen rychlý pracovní název a čisté pojmenování (i s číslováním) udělat až v textovém editoru.*
   - *Poznámka: Štítky ponechané s výchozím názvem "BLOK" se při exportu automaticky přeskočí a zahodí.*
6. spusť export: `python rehearsal_processor.py --input data/input/zkouska.mp3 --outdir data/output --mode export --labels data/output/final_labels.txt --artist "Název Mojí Kapely"`

## Ladění detekce (v `rehearsal_processor.py`)
- `threshold = music_peak * 0.15`: Práh, od kterého se hraje (aktuálně 15 % vrcholné hudební hlasitosti). *(Po úpravě je nutné smazat soubor s cache `*.pkl`)*
- `merge_tolerance_sec=4.0`: Jak dlouhou pauzu skript přejde, než stopu rozdělí.
- `min_duration_sec=45.0`: Skladby kratší než 45 vteřin se vyhodnotí jako ladění a zahodí.
- `padding_sec=4.0`: Každý blok skript roztáhne na začátku a na konci o 4 vteřiny, aby řez působil lidsky a neustřihl dozvuk činelů.