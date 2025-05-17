from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import pandas as pd
import lightgbm as lgb
import mlflow 
import mlflow.lightgbm
import os

os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')

mlflow.set_tracking_uri("http://a7ff29e59272e44458bae980a656cb8f-1038010547.us-east-2.elb.amazonaws.com:5000")
mlflow.lightgbm.autolog()



def main():
    # Prepare training data
    df = pd.read_csv('data/iris.csv')
    flower_names = {'Setosa': 0, 'Versicolor': 1, 'Virginica': 2}

    X = df[['sepal.length', 'sepal.width', 'petal.length', 'petal.width']]
    y = df['variety'].map(flower_names)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    train_data = lgb.Dataset(X_train, label=y_train)

    # Create or get experiment with custom artifact location
    experiment_name = "iris-classification"
    artifact_location = "s3://osaps-artifact-storage"

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(
            name=experiment_name,
            artifact_location=artifact_location
        )
    else:
        experiment_id = experiment.experiment_id

    # Train model
    with mlflow.start_run(experiment_id=experiment_id) as run: 
        params = {
            "objective": "multiclass",
            "num_class": 3, 
            "learning_rate": 0.2,
            "metric": "multi_logloss",
            "feature_fraction": 0.8,
            "bagging_fraction": 0.9,
            "seed": 42,
        }

        model = lgb.train(params, train_data, valid_sets=[train_data])

        # Evaluate model
        y_proba = model.predict(X_test)
        y_pred = y_proba.argmax(axis=1)

        loss = log_loss(y_test, y_proba)
        acc = accuracy_score(y_test, y_pred)

        mlflow.log_metrics({
            "log_loss": loss,
            "accuracy": acc
        })
    
    print("RUN ID:", run.info.run_id)
    print("Tracking URI:", mlflow.get_tracking_uri())
    print("Artifact URI:", run.info.artifact_uri)

if __name__ == "__main__":
    main()