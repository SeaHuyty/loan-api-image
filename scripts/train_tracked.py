"""Train several loan-default models and track every run in MLflow."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import RocCurveDisplay, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data.data import FEATURES, make_data  # noqa: E402

mlflow.set_experiment("loan-default")  # created on first use

df = make_data()
X_train, X_test, y_train, y_test = train_test_split(
    df[FEATURES], df.defaulted, test_size=0.2, random_state=42)

candidates = [
    ("logreg", {"C": 0.1, "class_weight": None}),
    ("logreg", {"C": 0.1, "class_weight": "balanced"}),
    ("logreg", {"C": 1.0, "class_weight": "balanced"}),
    ("forest", {"max_depth": 4, "class_weight": None}),
    ("forest", {"max_depth": 8, "class_weight": "balanced"}),
    ("forest", {"max_depth": 12, "class_weight": "balanced"}),
    ("gboost", {"learning_rate": 0.1, "max_depth": 2}),
    ("gboost", {"learning_rate": 0.05, "max_depth": 3}),
]

progress = tqdm(candidates, desc="Training", unit="run")
for kind, params in progress:
    progress.set_postfix_str(f"{kind} {params}")
    if kind == "logreg":
        model = make_pipeline(StandardScaler(), LogisticRegression(**params))
    elif kind == "gboost":
        model = GradientBoostingClassifier(n_estimators=150, random_state=42, **params)
    else:
        model = RandomForestClassifier(n_estimators=200, random_state=42, **params)

    with mlflow.start_run(run_name=f"{kind}-" + "-".join(f"{k}={v}" for k, v in params.items())):
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        predicted = proba >= 0.5

        mlflow.log_params({"model": kind, **{k: str(v) for k, v in params.items()}})
        mlflow.log_metrics({
            "auc": roc_auc_score(y_test, proba),
            "recall": recall_score(y_test, predicted),        
            "precision": precision_score(y_test, predicted),  
        })
        roc_figure = RocCurveDisplay.from_predictions(y_test, proba).figure_
        mlflow.log_figure(roc_figure, "roc_curve.png")
        plt.close(roc_figure)
        mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            signature=infer_signature(X_test, model.predict_proba(X_test)),
            input_example=X_test.head(3),
            pyfunc_predict_fn="predict_proba",
        )
        tqdm.write(f"{kind:<6} {params}  auc={roc_auc_score(y_test, proba):.3f}  "
              f"recall={recall_score(y_test, predicted):.3f}  precision={precision_score(y_test, predicted):.3f}")