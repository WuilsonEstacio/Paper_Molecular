from __future__ import annotations


def evaluate_bionemo_need(context: dict) -> str:
    relevant = context.get("protein_embeddings", False) or context.get("drug_target", False)
    if not relevant:
        return "NOT_REQUIRED"
    return "REQUIRES_EXTERNAL_EVALUATION"
