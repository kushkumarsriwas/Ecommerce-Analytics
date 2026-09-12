import pandas as pd
from pathlib import Path
def export_dataframe(df, filename, output_dir="exports"):
    """Export analytics results to CSV."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / filename
    df.to_csv(file_path, index=False)
    return file_path
def export_excel(dataframes, filename="analytics_report.xlsx", output_dir="exports"):
    """Export multiple analytics datasets into one Excel workbook."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / filename
    with pd.ExcelWriter(
        file_path,
        engine="xlsxwriter",
    ) as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(
                writer,
                sheet_name=str(sheet_name)[:31],
                index=False,
            )
    return file_path
