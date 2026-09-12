import pandas as pd
import numpy as np
def profile_dataframe(df):
    """Generate a data-quality profile for any dataframe."""
    profile = pd.DataFrame({
        "column": df.columns,
        "dtype": [
            str(dtype)
            for dtype in df.dtypes
        ],
        "rows": [
            len(df)
            for _ in df.columns
        ],
        "missing": [
            df[col].isna().sum()
            for col in df.columns
        ],
        "missing_%": [
            round(df[col].isna().mean() * 100, 2)
            for col in df.columns
        ],
        "unique_values": [
            df[col].nunique(dropna=True)
            for col in df.columns
        ],
        "duplicates": [
            df[col].duplicated().sum()
            for col in df.columns
        ],
    })
    profile["quality_status"] = np.where(
        profile["missing_%"] > 20,
        "Needs Attention",
        np.where(
            profile["missing_%"] > 5,
            "Review",
            "Good",
        ),
    )
    return profile
def dataset_summary(df):
    """Return high-level dataset quality metrics."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "missing_percentage": round(
            df.isna().mean().mean() * 100,
            2,
        ),
        "memory_mb": round(
            df.memory_usage(deep=True).sum() / 1024**2,
            2,
        ),
    }
