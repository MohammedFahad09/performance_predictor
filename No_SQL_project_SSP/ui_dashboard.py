# ui_dashboard.py
import streamlit as st
import pandas as pd
from db import get_predictions_collection
import matplotlib.pyplot as plt




def render_dashboard():
    coll = get_predictions_collection()
    role = st.session_state.role
    username = st.session_state.username

    st.subheader("📊 Student Performance Dashboard")

    try:
        data = list(coll.find().sort("timestamp", -1))
    except Exception as e:
        st.error(f"Could not fetch data: {e}")
        return

    if not data:
        st.info("No data available yet.")
        return

    df = pd.DataFrame(data)

    # Convert timestamp to readable if exists
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    if role == "admin":
        st.write("### Full Data Table (admin)")
        display_cols = ["_id", "created_by", "created_by_role", "timestamp",
                        "attendance_percent", "study_hours", "previous_score",
                        "predicted_exam_score", "actual_exam_score"]
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing].reset_index(drop=True))
    else:
        # student: filter rows created_by == username
        df_user = df[df["created_by"] == username]
        if df_user.empty:
            st.info("You have no predictions yet.")
            return
        st.write("### Your Predictions")
        display_cols = ["_id", "timestamp", "attendance_percent", "study_hours",
                        "previous_score", "predicted_exam_score", "actual_exam_score"]
        existing = [c for c in display_cols if c in df_user.columns]
        st.dataframe(df_user[existing].reset_index(drop=True))

    # Charts: show only if there are actual scores
    df_valid = df.dropna(subset=["actual_exam_score"])
    if not df_valid.empty:
        st.write("### Predicted vs Actual (all students)")
        st.line_chart(df_valid[["predicted_exam_score", "actual_exam_score"]])

        df_valid["error"] = df_valid["actual_exam_score"] - df_valid["predicted_exam_score"]
        st.write("### Prediction Error Distribution")
        st.bar_chart(df_valid["error"])
    else:
        st.info("No records with actual scores yet to chart.")

    # Feature importance if model added to session_state
    model = st.session_state.get("model")
    if model is not None and hasattr(model, "feature_importances_"):
        st.write("### 📌 Model Feature Importance")
        try:
            importance = model.feature_importances_
            features = ["Attendance", "Study Hours", "Previous Score"]
            fig, ax = plt.subplots()
            ax.bar(features, importance)
            ax.set_title("Feature Importance")
            st.pyplot(fig)
        except Exception as e:
            st.write("Could not render feature importance:", e)
