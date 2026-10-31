from __future__ import annotations

import re
from typing import Iterable, Sequence

import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

from config import POST_OUTCOME_FIELDS, SAFE_STRUCTURED_FIELDS, TEXT_FIELDS


def normalize_whitespace(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def combine_ticket_text(subject, description):
    parts = [normalize_whitespace(subject), normalize_whitespace(description)]
    joined = " ".join(part for part in parts if part)
    return joined.strip()


def prepare_ticket_text(df: pd.DataFrame):
    df = df.copy()
    for column in TEXT_FIELDS:
        if column in df.columns:
            df[column] = df[column].map(normalize_whitespace)
    if "subject" in df.columns and "issue_description" in df.columns:
        df["ticket_text"] = df.apply(lambda row: combine_ticket_text(row.get("subject", ""), row.get("issue_description", "")), axis=1)
    elif "issue_description" in df.columns:
        df["ticket_text"] = df["issue_description"].map(normalize_whitespace)
    elif "subject" in df.columns:
        df["ticket_text"] = df["subject"].map(normalize_whitespace)
    else:
        df["ticket_text"] = ""
    df["ticket_text"] = df["ticket_text"].fillna("")
    return df


def ticket_description_groups(df: pd.DataFrame):
    if "issue_description" in df.columns:
        descriptions = df["issue_description"]
    elif "ticket_text" in df.columns:
        descriptions = df["ticket_text"]
    else:
        descriptions = pd.Series("", index=df.index)
    groups = descriptions.map(lambda value: normalize_whitespace(value).casefold())
    empty = groups.eq("")
    groups.loc[empty] = [f"empty-description-{index}" for index in groups.index[empty]]
    return groups


def safe_feature_columns(df: pd.DataFrame, target_name: str):
    exclusions = {
        target_name,
        "priority",
        "escalated_to_human",
        "ticket_id",
        "customer_name",
        "customer_email",
        "created_at",
    }
    exclusions |= POST_OUTCOME_FIELDS
    return [column for column in SAFE_STRUCTURED_FIELDS if column in df.columns and column not in exclusions]


def make_model_preprocessor(
    df: pd.DataFrame,
    target_name: str,
    text_column: str = "ticket_text",
    word_tfidf_config: dict | None = None,
    char_tfidf_config: dict | None = None,
):
    df = prepare_ticket_text(df)
    feature_columns = safe_feature_columns(df, target_name)
    categorical_columns = [
        col for col in feature_columns
        if (
            pd.api.types.is_object_dtype(df[col].dtype)
            or pd.api.types.is_string_dtype(df[col].dtype)
            or isinstance(df[col].dtype, pd.CategoricalDtype)
        ) and col != text_column
    ]
    numeric_columns = [
        col for col in feature_columns
        if (pd.api.types.is_numeric_dtype(df[col]) and col not in {text_column})
    ]

    transformers = []
    word_options = {
        "lowercase": True,
        "strip_accents": "unicode",
        "ngram_range": (1, 2),
        "min_df": 2,
        "max_df": 0.98,
        "sublinear_tf": True,
    }
    word_options.update(word_tfidf_config or {})
    transformers.append(("text", TfidfVectorizer(**word_options), text_column))

    if char_tfidf_config is not None:
        char_options = {
            "analyzer": "char_wb",
            "ngram_range": (3, 5),
            "min_df": 3,
            "max_features": 100_000,
            "sublinear_tf": True,
            "dtype": np.float32,
        }
        char_options.update(char_tfidf_config)
        transformers.append(("char_text", TfidfVectorizer(**char_options), text_column))

    if categorical_columns:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_columns,
            )
        )

    if numeric_columns:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_columns,
            )
        )

    return ColumnTransformer(transformers=transformers, remainder="drop", sparse_threshold=0.3)


def prepare_model_data(df: pd.DataFrame, target_name: str):
    df = prepare_ticket_text(df)
    feature_columns = safe_feature_columns(df, target_name)
    X = df[feature_columns + ["ticket_text"]]
    y = df[target_name].astype(str)
    return X, y
