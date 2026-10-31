from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
DOCS_DIR = PROJECT_ROOT / "docs"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"
REPORTS_DIR = PROJECT_ROOT / "reports"
TESTS_DIR = PROJECT_ROOT / "tests"

DATASET_NAME = os.getenv("DATASET_NAME", "s2pidape/support-ticket-dataset")
DATASET_CONFIG = os.getenv("DATASET_CONFIG", "with_ai")
MAX_TRAIN_ROWS = int(os.getenv("MAX_TRAIN_ROWS", "100000"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.25"))
FAISS_TOP_K = int(os.getenv("FAISS_TOP_K", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

PRIORITY_MODEL_CONFIG = {
    "class_weight": os.getenv("PRIORITY_CLASS_WEIGHT", "balanced"),
    "C": float(os.getenv("PRIORITY_C", "1.0")),
}
ESCALATION_MODEL_CONFIG = {
    "class_weight": os.getenv("ESCALATION_CLASS_WEIGHT", "balanced"),
    "C": float(os.getenv("ESCALATION_C", "1.0")),
}
ESCALATION_DECISION_THRESHOLD = float(os.getenv("ESCALATION_DECISION_THRESHOLD", "0.5"))

PRIORITY_TARGET = "priority"
ESCALATION_TARGET = "escalated_to_human"
TEXT_FIELDS = ["issue_description", "subject"]
SAFE_STRUCTURED_FIELDS = [
    "category",
    "issue_type_id",
    "product",
    "channel",
    "region",
    "language",
    "customer_age",
    "customer_gender",
    "subscription_type",
    "customer_tenure_months",
    "previous_tickets",
    "customer_segment",
    "issue_complexity_score",
]

POST_OUTCOME_FIELDS = {
    "status",
    "auto_resolved",
    "escalation_reason",
    "reopen_count",
    "first_response_time_hours",
    "resolution_time_hours",
    "paused_hours",
    "resolution_wallclock_hours",
    "first_resolved_at",
    "resolved_at",
    "closed_at",
    "resolved_by",
    "resolution_notes",
    "sla_target_hours",
    "sla_breached",
    "sla_breach_margin",
    "customer_satisfaction_score",
    "assigned_team",
    "assigned_to",
    "resolved_by",
}

PRIORITY_MODEL_PATH = MODELS_DIR / "priority_model.joblib"
ESCALATION_MODEL_PATH = MODELS_DIR / "escalation_model.joblib"
MODEL_SUMMARY_PATH = REPORTS_DIR / "model_summary.json"
DATASET_SUMMARY_PATH = REPORTS_DIR / "dataset_summary.json"
EVALUATION_REPORT_PATH = REPORTS_DIR / "evaluation_report.json"
EXPERIMENT_REPORT_PATH = REPORTS_DIR / "experiment_report.json"

DOCS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index.bin"
DOCS_METADATA_PATH = VECTOR_STORE_DIR / "faiss_metadata.joblib"
