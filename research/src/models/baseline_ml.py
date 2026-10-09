from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score


@dataclass
class ModelResult:
    model_name: str
    roc_auc: float
    pr_auc: float
    f1: float


def train_baselines(X_train, y_train, X_test, y_test) -> list[ModelResult]:
    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced"),
    }
    results = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        probs = model.predict_proba(X_test)[:, 1]
        preds = (probs >= 0.5).astype(int)
        results.append(
            ModelResult(
                model_name=name,
                roc_auc=float(roc_auc_score(y_test, probs)),
                pr_auc=float(average_precision_score(y_test, probs)),
                f1=float(f1_score(y_test, preds)),
            )
        )
    return results
