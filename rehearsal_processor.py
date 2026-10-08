"""
G2.5 Rehearsal Audio Processor (v3.5)
Autor: Architekt a programátor (quant systems)
Popis: Analytický a exportní skript pro zpracování nahrávek zkoušek s implementací stavového automatu.
"""

import argparse
import logging
import os
import subprocess
import pickle
import re
import numpy as np
import librosa
import pandas as pd

# --- KONFIGURACE LOGOVÁNÍ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("RehearsalProcessor")

class RehearsalProcessor:
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = input_file
        self.output_dir = output_dir
        self.sr = 11025 # Nižší vzorkovací frekvence pro extrémně rychlou analýzu hlasitosti
        self.hop_length = 512
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.audio_cache = os.path.join(self.output_dir, "audio_analysis_cache_v4.pkl")

    def analyze_audio(self) -> pd.DataFrame:
        """Krok 1: Extrémně rychlé generování RMS pro detekci kandidátních hranic."""
        if os.path.exists(self.audio_cache):
            logger.info("Načítám analyzovaná audio data z lokální cache...")
            with open(self.audio_cache, 'rb') as f:
                return pickle.load(f)

        logger.info(f"Načítám audio (rychlý režim): {self.input_file}")
        # Načteme s mnohem nižší vzorkovací frekvencí (11025 Hz), protože pro analýzu hlasitosti nepotřebujeme detaily
        y, _ = librosa.load(self.input_file, sr=self.sr, mono=True)
        
        logger.info("Počítám energii (RMS) napříč celou nahrávkou...")
        # Vynechali jsme HPSS, protože podle histogramu je hlasitost hudby oproti mluvení obrovská sama o sobě
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr, hop_length=self.hop_length)
        
        # Zjištění běžné "hlasité" úrovně hudby (95. percentil ignoruje ojedinělé rány/prasknutí)
        music_peak = np.percentile(rms, 95)
        
        # Skladba se hraje, pokud je hlasitost alespoň 15% z maximální hudební hlasitosti
        threshold = music_peak * 0.15
        
        df = pd.DataFrame({'time': times, 'rms': rms})
        df['is_active'] = df['rms'] > threshold
        
        with open(self.audio_cache, 'wb') as f:
            pickle.dump(df, f)
            
        logger.info("Audio analýza dokončena a uložena do cache.")
        return df

    def extract_music_segments(self, df: pd.DataFrame, merge_tolerance_sec: float, min_duration_sec: float) -> list:
        """Stavový automat s hysterezí pro spojování fragmentů audia."""
        times = df['time'].values
        is_active = df['is_active'].values
        
        raw_segments = []
        in_segment = False
        start_time = 0.0
        
        # 1. Extrakce hrubých bloků
        for i in range(len(is_active)):
            if is_active[i] and not in_segment:
                in_segment = True
                start_time = times[i]
            elif not is_active[i] and in_segment:
                in_segment = False
                raw_segments.append([start_time, times[i]])
                
        if in_segment:
            raw_segments.append([start_time, times[-1]])
            
        # 2. Slučování bloků (Hystereze)
        merged_segments = []
        for seg in raw_segments:
            if not merged_segments:
                merged_segments.append(seg)
            else:
                last_seg = merged_segments[-1]
                if (seg[0] - last_seg[1]) <= merge_tolerance_sec:
                    last_seg[1] = seg[1] # Prodloužení předchozího bloku
                else:
                    merged_segments.append(seg)
                    
        # 3. Filtrace hluku a ladění na základě minimální délky
        final_segments = []
        for s in merged_segments:
            duration = s[1] - s[0]
            if duration >= min_duration_sec:
                final_segments.append({'start': s[0], 'end': s[1], 'duration': duration})
                
        return final_segments

    def generate_label_track(self, df_audio: pd.DataFrame, output_txt: str):
        """Krok 3: Sloučení vyhodnoceného hudebního automatu do Audacity formátu."""
        logger.info("Aplikuji stavový automat pro extrakci skladeb...")
        
        # Parametry definující chování detektoru:
        # merge_tolerance_sec = 4.0s (překlene pauzy bubeníka)
        # padding_sec = 2.0s (přidá prostor před a za skladbou pro plynulejší začátky a konce)
        padding_sec = 2.0
        
        music_segments = self.extract_music_segments(
            df_audio, 
            merge_tolerance_sec=4.0, 
            min_duration_sec=45.0
        )
        
        labels = []
            
        for s in music_segments:
            # Rozšíříme bloky o padding, ale zajistíme, že nezačnou v mínusu
            start = max(0.0, s['start'] - padding_sec)
            end = s['end'] + padding_sec
            labels.append((start, end, "BLOK"))
            
        labels.sort(key=lambda x: x[0])
        
        with open(output_txt, 'w', encoding='utf-8') as f:
            for start, end, label in labels:
                f.write(f"{start:.6f}\t{end:.6f}\t{label}\n")
                
        logger.info(f"Label Track vygenerován: {output_txt} (Nalezeno skladeb: {len(music_segments)})")

    def execute_ffmpeg_export(self, labels_txt: str, artist_name: str = "Unknown Artist"):
        """Krok 4: Načtení Audacity štítků a dávkový export MP3 (re-encode) s ID3 tagy."""
        logger.info(f"Zahajuji FFmpeg dávkový export podle {labels_txt}...")
        
        if not os.path.exists(labels_txt):
            logger.error(f"Soubor {labels_txt} nebyl nalezen. Export přerušen.")
            return

        with open(labels_txt, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        track_counter = 1
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
                
            start_time = float(parts[0])
            end_time = float(parts[1])
            duration = end_time - start_time
            label_text = parts[2].strip()
            
            # Ignorujeme nevyplněné výchozí štítky
            if label_text == "BLOK":
                logger.info(f"Přeskakuji nepojmenovaný úsek v čase {start_time:.1f}s.")
                continue
                
            # Detekce čísla v názvu (např. "01 Heartbreaker" -> "01", "Heartbreaker")
            match = re.match(r'^(\d+)[\s\-\._]*(.+)$', label_text)
            if match:
                track_num = str(match.group(1)).zfill(2)
                title = match.group(2).strip()
            else:
                track_num = str(track_counter).zfill(2)
                title = label_text
                
            track_counter += 1
            
            output_filename = os.path.join(self.output_dir, f"{track_num} {title}.mp3")
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', self.input_file,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c:a', 'libmp3lame',
                '-q:a', '2',
                '-metadata', f'title={title}',
                '-metadata', f'track={track_num}',
                '-metadata', f'artist={artist_name}',
                output_filename
            ]
            
            logger.info(f"Exportuji: {output_filename}")
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        logger.info("Dávkový export kompletně dokončen.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="G2.5 Rehearsal Audio Processor v3.5")
    parser.add_argument("--input", required=True, help="Cesta k MP3 souboru ze zkoušky")
    parser.add_argument("--outdir", required=True, help="Výstupní adresář")
    parser.add_argument("--mode", choices=['analyze', 'export'], required=True, help="Režim: 'analyze' nebo 'export'")
    parser.add_argument("--labels", help="Cesta k upravenému labels.txt (povinné pro režim 'export')")
    parser.add_argument("--artist", default="Unknown Artist", help="Název kapely pro ID3 tagy (při exportu)")
    
    args = parser.parse_args()
    processor = RehearsalProcessor(input_file=args.input, output_dir=args.outdir)
    
    if args.mode == 'analyze':
        audio_data = processor.analyze_audio()
        label_file = os.path.join(args.outdir, "labels.txt")
        processor.generate_label_track(audio_data, label_file)
        logger.info("Analýza ukončena z lokální cache za zlomek vteřiny.")
        
    elif args.mode == 'export':
        if not args.labels:
            logger.error("Pro export je nutné specifikovat --labels.")
            exit(1)
        processor.execute_ffmpeg_export(args.labels, artist_name=args.artist)