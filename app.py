import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import random
sys.path.insert(0, "src")
from anomaly_detector import AnomalyDetector

st.set_page_config(page_title="MPLS Anomaly Detector", page_icon="network", layout="wide")
st.title("Simulateur reseau IP/MPLS avec detection d anomalies IA")
st.markdown("Projet portfolio - Detection d anomalies reseau par Machine Learning")

@st.cache_data
def load_data():
    return pd.read_csv("data/dataset.csv")

@st.cache_resource
def load_model():
    detector = AnomalyDetector()
    df = detector.load_data()
    df = detector.train_isolation_forest(df)
    detector.train_classifier(df)
    return detector, df

df = load_data()
detector, df_model = load_model()

st.sidebar.header("Controles")
max_ticks = st.sidebar.slider("Nombre de ticks affiches", 100, 5000, 1000)
event_filter = st.sidebar.multiselect("Filtrer par evenement", ["normal","link_failure","traffic_spike","link_degradation"], default=["normal","link_failure","traffic_spike","link_degradation"])

st.sidebar.header("Injecter un evenement")
if st.sidebar.button("Injecter une panne de lien"):
    st.sidebar.error("ALERTE : Coupure de lien detectee !")
if st.sidebar.button("Injecter un pic de trafic"):
    st.sidebar.warning("ALERTE : Pic de trafic detecte !")

df_display = df[df["event"].isin(event_filter)].head(max_ticks)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latence moyenne", str(round(df_display["latency_ms"].mean(), 2)) + " ms")
col2.metric("Gigue moyenne", str(round(df_display["jitter_ms"].mean(), 2)) + " ms")
col3.metric("Perte moyenne", str(round(df_display["loss_pct"].mean(), 3)) + " %")
col4.metric("Anomalies detectees", str(len(df_display[df_display["event"] != "normal"])))

st.subheader("Evolution de la latence reseau")
fig1 = px.line(df_display, x="tick", y="latency_ms", color="event", title="Latence par tick", labels={"latency_ms": "Latence (ms)", "tick": "Tick"})
st.plotly_chart(fig1, use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.subheader("Utilisation des liens")
    fig2 = px.area(df_display, x="tick", y="utilization_pct", title="Utilisation (%)", color_discrete_sequence=["#1D9E75"])
    st.plotly_chart(fig2, use_container_width=True)
with col6:
    st.subheader("Distribution des evenements")
    event_counts = df_display["event"].value_counts().reset_index()
    event_counts.columns = ["event", "count"]
    fig3 = px.bar(event_counts, x="event", y="count", title="Evenements", color="event")
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Alertes IA en temps reel")
alertes = df_model[df_model["event"] != "normal"][["tick","timestamp","latency_ms","event","is_anomaly","anomaly_score"]].head(20)
st.dataframe(alertes, use_container_width=True)

st.subheader("Tester une prediction IA")
col7, col8, col9 = st.columns(3)
latency = col7.slider("Latence (ms)", 1.0, 30.0, 3.0)
cpu = col8.slider("CPU (%)", 10.0, 60.0, 25.0)
loss = col9.slider("Perte (%)", 0.0, 20.0, 0.0)

if st.button("Lancer la prediction"):
    test = {"latency_ms": latency, "jitter_ms": 1.0, "utilization_pct": 5.0, "loss_pct": loss, "cpu_pct": cpu, "active_flows": 12, "rolling_latency": latency, "delta_latency": latency - 3.0}
    result = detector.predict(test)
    if result["is_anomaly"]:
        st.error("ANOMALIE DETECTEE : " + result["event_type"] + " | Score: " + str(result["anomaly_score"]))
    else:
        st.success("Trafic NORMAL | Score: " + str(result["anomaly_score"]))
