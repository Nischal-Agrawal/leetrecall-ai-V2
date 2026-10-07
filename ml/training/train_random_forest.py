import joblib

from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    classification_report
)

from ml.preprocessing.preprocess import (
    load_and_preprocess
)


df = load_and_preprocess()

X = df.drop(
    columns=["remembered"]
)

y = df["remembered"]

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )
)

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(
    X_train,
    y_train
)

predictions = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    f"Accuracy: {accuracy:.4f}"
)

print(
    classification_report(
        y_test,
        predictions
    )
)

joblib.dump(
    model,
    "ml/artifacts/random_forest_model.pkl"
)

print(
    "Model saved successfully"
)