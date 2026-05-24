from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / 'sample'
for p in SAMPLE_DIR.glob('*.csv'):
    print(p.name, p.stat().st_size)
