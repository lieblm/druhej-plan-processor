# Návrh na migraci: Google Colab (Cloudové řešení)

Tento dokument slouží jako záznam myšlenky a návrhu na přesun lokálního skriptu do prostředí Google Colab. Cílem je umožnit všem členům kapely analyzovat a exportovat nahrávky ze zkoušek bez nutnosti instalovat Python, FFmpeg a další knihovny lokálně.

## Architektura řešení
1. **Google Drive jako úložiště:** 
   - V Colab notebooku se na začátku připojí sdílený Google Drive kapely (`google.colab.drive.mount('/content/drive')`).
   - Členové nahrávají syrové MP3 soubory přímo do sdílené složky.
2. **Buňka 1: Analýza (Generování štítků):**
   - Skript si přečte MP3 z disku a provede rychlou RMS analýzu (jako současný `rehearsal_processor.py --mode analyze`).
   - Vygeneruje soubor `labels.txt` a uloží ho vedle MP3 na Google Drive.
3. **Zásah uživatele (Human-in-the-loop):**
   - Člen kapely si stáhne `labels.txt` a MP3 do počítače.
   - Otevře je v Audacity, upraví délky, přejmenuje zajímavé kusy ze `SONG` na názvy skladeb (např. `01 Heartbreaker`).
   - Upravený soubor nahraje zpět na Google Drive (např. jako `final.txt`).
4. **Buňka 2: Finální export:**
   - Notebook spustí exportní mód (`--mode export --labels final.txt`).
   - Pomocí FFmpeg (předinstalovaného v Colabu) rozstříhá velký MP3 soubor.
   - Výsledné jednotlivé skladby se uloží do složky na Google Drive, odkud si je všichni mohou ihned pustit.

## Výhody
- Není třeba nic instalovat (FFmpeg, Python, pip).
- Odpadá problém s kompatibilitou (Mac, Windows, Linux).
- Extrémně rychlý výpočet na serverech Googlu.
- Skript a kód běží v prohlížeči, sdílí se jednoduchým odkazem.

## Možná vylepšení (Pokročilý Colab)
S využitím `ipywidgets` a `IPython.display.Audio` by šlo z Colabu vytvořit jednoduché grafické rozhraní, které rovnou nabídne přehrání jednotlivých "SONG" kandidátů a textové pole pro zadání názvu skladby. Tím by se kompletně eliminovala nutnost stahovat a používat Audacity.
