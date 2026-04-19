# 🚦 Vancouver Traffic Accident Risk Predictor
**An End-to-End Machine Learning Pipeline: From EDA to Dockerized API**

This repository showcases a structured progression through the ML lifecycle. The project analyzes the relationship between Vancouver's weather patterns and traffic collisions to build a predictive system served via a production-ready REST API.

---

## 📺 Project Evolution & Presentations
The project is divided into three distinct phases, demonstrating a transition from raw data exploration to a deployed software product.

### Phase 1: Exploratory Data Analysis (EDA)
*   **Objective:** Statistical analysis of historical Vancouver weather and collision data.
*   **Outcome:** Identified key features (precipitation, temperature) that significantly impact accident frequency.
*   **Presentation:** [Watch Phase 1 Overview](./docs/Weather and Traffic Accident Analysis in Vancouver Part 1 (480).mp4)  
*   **Notebook:** [`01_Data_Analysis.ipynb`](./01_Data_Analysis.ipynb)

### Phase 2: Predictive Modeling
*   **Objective:** Feature engineering and model training.
*   **Outcome:** Developed a classification model to predict "High Risk" days. Optimized the pipeline for high recall to capture maximum safety risks.
*   **Presentation:** [Watch Phase 2 Overview](./docs/Weather and Traffic Accident Analysis in Vancouver Part 2 (480).mp4)  
*   **Notebook:** [`02_Model_Training.ipynb`](./02_Model_Training.ipynb)

### Phase 3: Productionalization & Deployment
*   **Objective:** Converting a model into a usable application.
*   **Outcome:** Wrapped the model in a **FastAPI** server with an in-memory prediction cache for low-latency responses. The entire environment is **Dockerized** for seamless deployment.
*   **Full Module:** [Explore the Production API](./production-service)

---

## 🛠️ Technical Stack

| Category | Tools |
| :--- | :--- |
| **Languages** | Python (3.x) |
| **Data Science** | Pandas, Scikit-Learn, Jupyter |
| **Backend** | FastAPI, Uvicorn |
| **DevOps** | Docker, .dockerignore |
| **Communication** | REST API (JSON) |

---

## 🚀 Quick Start (Phase 3)

The production-ready predictor is located in the `/production-service` directory.

