"""Register the two best loan-default runs, then point 'champion' and 'challenger' at them."""

# 1. Finds the two runs with the highest AUC in the loan-default experiment.
# 2. Registers each run's logged model under the name loan-default, which creates versions 1 and 2.
# 3. Writes a description on each version with the model type, parameters, metrics and run ID.
# 4. Points the alias champion at the best version and challenger at the runner-up.

import mlflow
from mlflow import MlflowClient

NAME = "loan-default"

client = MlflowClient()
experiment = client.get_experiment_by_name("loan-default")
best_two = client.search_runs(
    [experiment.experiment_id],
    order_by=["metrics.auc DESC"],
    max_results=2,
)

for alias, run in zip(["champion", "challenger"], best_two):
    version = mlflow.register_model(f"runs:/{run.info.run_id}/model", NAME)
    description = (
        f"{run.data.params['model']} ({run.info.run_name}): "
        f"auc={run.data.metrics['auc']:.3f}, recall={run.data.metrics['recall']:.3f}, "
        f"precision={run.data.metrics['precision']:.3f}. Run {run.info.run_id}."
    )
    client.update_model_version(NAME, version.version, description=description)
    client.set_registered_model_alias(NAME, alias, version.version)
    print(f"{alias:<10} -> version {version.version}: {description}")
