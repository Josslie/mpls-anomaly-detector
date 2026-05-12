import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import sys
sys.path.insert(0, "src")

class AnomalyDetector:
    def __init__(self):
        self.scaler = StandardScaler()
        self.iso_forest = IsolationForest(contamination=0.006, random_state=42)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.features = ["latency_ms","jitter_ms","utilization_pct","loss_pct","cpu_pct","active_flows"]
        self.is_trained = False

    def load_data(self, path="data/dataset.csv"):
        df = pd.read_csv(path)
        df["rolling_latency"] = df["latency_ms"].rolling(10, min_periods=1).mean()
        df["delta_latency"] = df["latency_ms"].diff().fillna(0)
        self.features = ["latency_ms","jitter_ms","utilization_pct","loss_pct","cpu_pct","active_flows","rolling_latency","delta_latency"]
        return df

    def train_isolation_forest(self, df):
        print("Entrainement Isolation Forest...")
        normal_data = df[df["event"] == "normal"][self.features]
        X_normal = self.scaler.fit_transform(normal_data)
        self.iso_forest.fit(X_normal)
        X_all = self.scaler.transform(df[self.features])
        df["anomaly_score"] = self.iso_forest.decision_function(X_all)
        df["is_anomaly"] = self.iso_forest.predict(X_all)
        df["is_anomaly"] = df["is_anomaly"].map({1: 0, -1: 1})
        real_anomalies = df[df["event"] != "normal"]
        detected = real_anomalies[real_anomalies["is_anomaly"] == 1]
        rate = round(len(detected) / len(real_anomalies) * 100, 1)
        print("Taux de detection : " + str(rate) + "% (" + str(len(detected)) + "/" + str(len(real_anomalies)) + " anomalies)")
        return df

    def train_classifier(self, df):
        print("Entrainement Random Forest classifier...")
        X = self.scaler.transform(df[self.features])
        y = df["event"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.classifier.fit(X_train, y_train)
        y_pred = self.classifier.predict(X_test)
        print("\nRapport de classification:")
        print(classification_report(y_test, y_pred))
        print("Matrice de confusion:")
        print(confusion_matrix(y_test, y_pred))
        importances = pd.Series(self.classifier.feature_importances_, index=self.features)
        print("\nFeatures les plus importantes:")
        print(importances.sort_values(ascending=False).to_string())
        self.is_trained = True
        return self.classifier

    def predict(self, metrics: dict):
        if not self.is_trained:
            return "non entraine"
        X = pd.DataFrame([metrics])[self.features]
        X_scaled = self.scaler.transform(X)
        prediction = self.classifier.predict(X_scaled)[0]
        score = self.iso_forest.decision_function(X_scaled)[0]
        return {"event_type": prediction, "anomaly_score": round(float(score), 3), "is_anomaly": prediction != "normal"}

if __name__ == "__main__":
    detector = AnomalyDetector()
    df = detector.load_data()
    df = detector.train_isolation_forest(df)
    detector.train_classifier(df)
    print("\nTest prediction en temps reel:")
    test = {"latency_ms": 25.0, "jitter_ms": 0.5, "utilization_pct": 8.0, "loss_pct": 10.0, "cpu_pct": 45.0, "active_flows": 10, "rolling_latency": 20.0, "delta_latency": 15.0}
    print(detector.predict(test))
    test2 = {"latency_ms": 2.5, "jitter_ms": 1.0, "utilization_pct": 5.0, "loss_pct": 0.0, "cpu_pct": 25.0, "active_flows": 12, "rolling_latency": 2.5, "delta_latency": 0.1}
    print(detector.predict(test2))
