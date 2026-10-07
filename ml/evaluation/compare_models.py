import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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

rf = joblib.load(
    "ml/artifacts/random_forest_model.pkl"
)

xgb = joblib.load(
    "ml/artifacts/xgboost_model.pkl"
)

rf_acc = accuracy_score(
    y_test,
    rf.predict(X_test)
)

xgb_acc = accuracy_score(
    y_test,
    xgb.predict(X_test)
)

print("\nMODEL COMPARISON")

print(
    f"Random Forest Accuracy: {rf_acc:.4f}"
)

print(
    f"XGBoost Accuracy: {xgb_acc:.4f}"
)

if xgb_acc > rf_acc:
    print("\nWinner: XGBoost")
else:
    print("\nWinner: Random Forest")