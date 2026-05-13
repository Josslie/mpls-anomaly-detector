# Simulateur reseau IP/MPLS avec detection d anomalies IA

## Demo en ligne

https://josslie-mpls-anomaly-detector.streamlit.app

## Description

Projet portfolio simulant un backbone reseau IP/MPLS d operateur telecom avec detection automatique d anomalies par Machine Learning.

## Concepts implementes

- Topologie reseau avec noeuds PE/P
- Routage OSPF avec reconvergence automatique
- Label switching MPLS (PUSH / SWAP / POP)
- Segmentation L3VPN avec VRFs isolees
- Generateur de trafic QoS (DSCP EF, AF41, BE)
- Detection d anomalies par Isolation Forest et Random Forest
- Dashboard interactif Streamlit

## Stack technique

- Python 3.11
- NetworkX, scikit-learn, Matplotlib, Plotly, Streamlit

## Resultats ML

- Precision globale : 100%
- Detection coupures de lien : 100%
- Features importantes : latence (36%), delta latence (24%), CPU (17%)

## Installation

```
git clone https://github.com/Josslie/mpls-anomaly-detector.git
cd mpls-anomaly-detector
pip install -r requirements.txt
python -m streamlit run app.py
```

## Auteur

Projet portfolio pour des postes en reseaux et telecoms.
