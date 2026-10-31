from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_dataset

from config import DATASET_NAME, DATASET_CONFIG, MODEL_SUMMARY_PATH, RANDOM_SEED, REPORTS_DIR


def load_support_dataset(max_rows: int | None = None, config_name: str | None = None, seed: int = RANDOM_SEED):
    """Load the support-ticket dataset from Hugging Face with a configurable sample size."""
    dataset_name = DATASET_NAME if config_name is None else config_name
    dataset_config = DATASET_CONFIG if config_name is None else config_name
    try:
        split = "train"
        if max_rows is not None:
            split = f"train[:{max_rows}]"
        dataset = load_dataset(dataset_name, dataset_config, split=split)
        if max_rows is not None and len(dataset) > 0 and max_rows < len(load_dataset(dataset_name, dataset_config, split="train")):
            dataset = dataset.shuffle(seed=seed)
        return dataset
    except Exception as exc:  # pragma: no cover - network failures handled in higher layers
        raise RuntimeError(
            f"Could not load the dataset '{dataset_name}' config '{dataset_config}'. "
            "Check the Hugging Face dataset permissions, internet access, or cache status."
        ) from exc


def dataset_to_dataframe(dataset):
    return dataset.to_pandas()


def build_dataset_summary(df: pd.DataFrame, summary_path: str | Path = MODEL_SUMMARY_PATH):
    summary = {
        "shape": {"rows": int(len(df)), "columns": int(len(df.columns))},
        "columns": list(df.columns),
        "missing_values": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated(subset=list(df.columns)).sum()),
        "target_summary": {},
        "text_summary": {},
    }

    for target in ["priority", "escalated_to_human"]:
        if target in df.columns:
            counts = df[target].fillna("missing").astype(str).value_counts(dropna=False).to_dict()
            summary["target_summary"][target] = counts

    text_columns = [c for c in ["issue_description", "subject", "description"] if c in df.columns]
    for column in text_columns:
        values = df[column].fillna("")
        summary["text_summary"][column] = {
            "empty_count": int((values == "").sum()),
            "avg_length": float(values.str.len().mean()) if not values.empty else 0.0,
            "max_length": int(values.str.len().max()) if not values.empty else 0,
        }

    summary_path = Path(summary_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


def inspect_dataset_summary(max_rows: int | None = None):
    dataset = load_support_dataset(max_rows=max_rows)
    df = dataset_to_dataframe(dataset)
    summary = build_dataset_summary(df)
    return df, summary
