# Band Rehearsal Audio Processor

Automatizovaná pipeline pro bleskovou analýzu, segmentaci a export nahrávek ze zkoušek kapely. Skript spolehlivě identifikuje písničky na základě analýzy dynamiky a hlasitosti (RMS), ignoruje mluvení/ladění a připraví štítky pro finální ořez.

> 🎸 **Od muzikantů pro muzikanty:** Tento nástroj jsme si původně vytvořili pro zpracování našich zkoušek v kapele **Druhej plán**. Rozhodli jsme se ho ale uvolnit jako open-source – věříme totiž, že ušetří spoustu otravného stříhání a klikání i dalším muzikantům, aby se mohli soustředit na to podstatné: na muziku.

## Workflow
1. vlož 2h záznam do `data/input/`.
2. spusť analýzu: `python rehearsal_processor.py --input data/input/zkouska.mp3 --outdir data/output --mode analyze`
   - *Poznámka: Analýza celého 2h souboru trvá jen několik vteřin. Data se ukládají do cache pro instantní opakované ladění.*
3. zkontroluj vygenerované štítky `data/output/labels.txt` v Audacity.
4. uprav si začátky a konce, přejmenuj štítky "SONG" na názvy skladeb a ulož upravené štítky (např. jako `final_labels.txt`).
   - *Poznámka: Neupravené štítky ponechané s názvem "SONG" se při exportu přeskočí, takže pokud chceš nějaký úsek ignorovat, prostě ho nepřejmenovávej.*
5. spusť export: `python rehearsal_processor.py --input data/input/zkouska.mp3 --outdir data/output --mode export --labels data/output/final_labels.txt --artist "Název Mojí Kapely"`

## Ladění detekce (v `rehearsal_processor.py`)
- `threshold = music_peak * 0.15`: Práh, od kterého se hraje (aktuálně 15 % vrcholné hudební hlasitosti). *(Po úpravě je nutné smazat soubor s cache `*.pkl`)*
- `merge_tolerance_sec=4.0`: Jak dlouhou pauzu/dýchačku bubeníka skript přejde, než stopu rozdělí.
- `min_duration_sec=45.0`: Skladby kratší než 45 vteřin se vyhodnotí jako ladění a zahodí.
- `padding_sec=2.0`: Každý blok skript roztáhne na začátku a na konci o 2 vteřiny, aby řez působil lidsky a neustřihl dozvuk činelů.