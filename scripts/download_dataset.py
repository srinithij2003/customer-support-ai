from __future__ import annotations

from src.data_loader import inspect_dataset_summary


def main():
    df, summary = inspect_dataset_summary(max_rows=10000)
    print(f"Loaded {len(df)} rows for schema inspection.")
    print(summary["target_summary"])


if __name__ == "__main__":
    main()
