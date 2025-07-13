# data_loader.py

import pandas as pd
from pathlib import Path

def load_all_csvs(data_dir: Path) -> dict:
    csv_data = {}
    for csv_file in data_dir.glob("*.csv"):
        var_name = csv_file.stem.lower().replace("-", "_") + "_data"
        df = pd.read_csv(csv_file)
        csv_data[var_name] = df
    return csv_data
