from pathlib import Path


def rename_pandas_columns(df, cols):
    out_df = df.rename(columns=cols)
    return out_df


def save_pandas_to_csv(df, csv_name, out_path="", drop_nan=False, aggreg={}):
    out_dir = Path(out_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    df_out = df.copy(deep=True)

    if drop_nan:
        df_out.dropna(how='all')
        df_out = resample_dataset(df_out, aggreg)
        df_out.to_csv(out_dir / csv_name)
    else:
        df_out.to_csv(out_dir / csv_name)


def save_pandas_to_json(df, json_name, out_path="", drop_nan=False, aggreg={}):
    out_dir = Path(out_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    df_out = df.copy(deep=True)

    if drop_nan:
        df_out.dropna(how='all', inplace=True)
    #
    df_out = resample_dataset(df_out, aggreg=aggreg)
    df_out.reset_index(inplace=True)
    df_out["timestamp"] = df_out["timestamp"].astype(str)
    df_out.to_json(out_dir / json_name, orient='records')


def resample_dataset(df, aggreg={}):
    if aggreg:
        return df.resample("1h").agg(aggreg).bfill()
    else:
        return df.resample("1h").mean().bfill()
