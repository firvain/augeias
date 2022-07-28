from pathlib import Path


def rename_pandas_columns(df, cols):
    out_df = df.rename(columns=cols)
    return out_df


def save_pandas_to_csv(df, csv_name, out_path="", drop_nan=False):
    out_dir = Path(out_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    if drop_nan:
        df.dropna(how='all').to_csv(out_dir / csv_name)
    else:
        df.to_csv(out_dir / csv_name)
