import pandas as pd


def rename_pandas_columns(df, cols):
    out_df = df.rename(columns=cols)
    return out_df
