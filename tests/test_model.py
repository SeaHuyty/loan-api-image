"""The exported champion must load and score a known applicant. Guards against shipping a bad model."""
import os
from pathlib import Path

import mlflow.pyfunc
import pandas as pd

from app.services.scoring import FEATURES

MODEL_DIR = os.getenv("MODEL_DIR", str(Path(__file__).resolve().parent.parent / "model" / "champion"))

# champion-v1 on borrower 1042's first loan. Update with MODEL_VERSION when the champion changes.
KNOWN_APPLICANT = [1500, 12, 400.0, 0, 0]
EXPECTED_PROBABILITY = 0.0178


def test_champion_scores_known_applicant():
    model = mlflow.pyfunc.load_model(MODEL_DIR)
    assert [c.name for c in model.metadata.get_input_schema().inputs] == FEATURES
    proba = model.predict(pd.DataFrame([KNOWN_APPLICANT], columns=FEATURES))
    assert round(float(proba[0][1]), 4) == EXPECTED_PROBABILITY
