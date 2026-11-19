from pathlib import Path


NB_FILE = Path(
    r"C:\Users\Adarsh setu\OneDrive\Desktop\Project\Analytics_Platform\data\NB_MASTER_PARQUET\NB_MASTER_FULL.parquet"
)

SB_FILE = Path(
    r"C:\Users\Adarsh setu\OneDrive\Desktop\Project\Analytics_Platform\data\SB_MASTER_PARQUET\SB_MASTER_FULL.parquet"
)

NMI_FILE = Path(
    r"C:\Users\Adarsh setu\OneDrive\Desktop\Project\Analytics_Platform\data\NMI_MASTER_PARQUET\NMI_MASTER_FULL.parquet"
)

PARQUET_FILES = {
    "NB": NB_FILE,
    "SB": SB_FILE,
    "NMI": NMI_FILE
}