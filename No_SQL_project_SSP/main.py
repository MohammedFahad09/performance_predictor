# main.py
import streamlit as st
import joblib
from db import seed_default_users
from auth import init_session_state, require_login_or_redirect
from ui_predict import render_predict
from ui_submit_score import render_submit_score
from ui_dashboard import render_dashboard

MODEL_PATH = "ML_model_SPP.pkl"

def load_model():
    try:
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"Could not load model '{MODEL_PATH}': {e}")
        return None

def main():
    st.set_page_config(page_title="Student Performance Predictor", layout="centered")
    init_session_state()

    
    seed_default_users()

    
    require_login_or_redirect()


    model = load_model()
    st.session_state["model"] = model

    st.title("🎓 Student Performance Prediction System")

 
    tab1, tab2, tab3 = st.tabs([
        "📈 Predict Performance",
        "📥 Submit Official Score",
        "📊 Dashboard"
    ])

    with tab1:
        render_predict(model)

    with tab2:
        render_submit_score()

    with tab3:
        render_dashboard()

if __name__ == "__main__":
    main()
