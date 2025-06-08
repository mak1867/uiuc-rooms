import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # ---- normalise whitespace ------------------------------------------------
    for col in ["Location", "Day", "Time"]:
        df[col] = df[col].astype(str).str.strip()

    # ---- remove online sections ---------------------------------------------
    mask_online = df["Location"].str.contains(r"\bonline\b", case=False, na=False)
    df = df.loc[~mask_online]

    # ---- flag “n.a.” variations as NaN --------------------------------------
    na_regex = re.compile(r"^\s*(?:n\.?/?a\.?|na)\s*$", re.I)  # see doc-string
    df.replace(na_regex, np.nan, inplace=True)

    # ---- drop rows missing any of the three key columns ----------------------
    df.dropna(subset=["Location", "Day", "Time"], inplace=True)

    return df


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clean the raw course CSV produced by the scraper."
    )
    parser.add_argument(
        "--in",
        dest="infile",
        default="SP25_UIUC_courses.csv",
        help="Path to input CSV (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        dest="outfile",
        default="SP25_UIUC_courses_clean.csv",
        help="Path for cleaned CSV (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    in_path = Path(args.infile)
    if not in_path.is_file():
        sys.exit(f"Input file not found: {in_path}")

    print(f"Reading  : {in_path}")
    df_raw = pd.read_csv(in_path)

    print("Cleaning …")
    df_clean = clean_dataframe(df_raw.copy())

    out_path = Path(args.outfile)
    df_clean.to_csv(out_path, index=False)
    print(f"Wrote     : {out_path}")
    print(f"Rows kept : {len(df_clean):,} of {len(df_raw):,}")


if __name__ == "__main__":
    main()
