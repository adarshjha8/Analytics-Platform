from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

NB_FILE = DATA_DIR / "NB_MASTER_FULL.parquet"
SB_FILE = DATA_DIR / "SB_MASTER_FULL.parquet"
NMI_FILE = DATA_DIR / "NMI_MASTER_FULL.parquet"

PARQUET_FILES = {
    "NB": NB_FILE,
    "SB": SB_FILE,
    "NMI": NMI_FILE,
}