# ui_predict.py
import streamlit as st
from db import get_predictions_collection
from datetime import datetime

def render_predict(model):
    st.subheader("Enter Student Information")

    col1, col2 = st.columns(2)
    with col1:
        previous_score = st.number_input("Previous Score (%)", min_value=0, max_value=100, value=70)
    with col2:
        study_hours = st.number_input("Study Hours (6 hrs college + self-study)", min_value=0, max_value=24, value=6)

    attendance = st.slider("Attendance (%)", 0, 100, 75)

    st.metric("Attendance Level", f"{attendance}%")
    st.progress(attendance / 100)

    if st.button("Predict Performance"):
        try:
            prediction = model.predict([[attendance, study_hours, previous_score]])
            pred_val = float(prediction[0])
            pred_val = min(pred_val, 100.0)
            predicted_score = round(pred_val, 2)
        except Exception as e:
            st.error(f"Model prediction failed: {e}")
            return

        st.success(f"🎯 Predicted Marks: {predicted_score:.2f}%")

        # Feedback
        st.write("### 🧠 Personalized Recommendation")
        if predicted_score < 50:
            st.warning("⚠️ Low predicted performance. Increase daily study hours and improve attendance.")
        elif predicted_score < 70:
            st.info("📘 Decent performance — consistent revision will help.")
        elif predicted_score < 90:
            st.success("👍 Good performance! Keep consistency.")
        else:
            st.success("🎉 Excellent! Keep up the great work.")

        
        
        
        user = st.session_state.username
        role = st.session_state.role
        rec = {
            "attendance_percent": attendance,
            "study_hours": study_hours,
            "previous_score": previous_score,
            "predicted_exam_score": predicted_score,
            "actual_exam_score": None,
            "created_by": user,
            "created_by_role": role,
            "timestamp": datetime.utcnow()
        }
        try:
            coll = get_predictions_collection()
            res = coll.insert_one(rec)
            st.info(f"✅ Record saved (you don't need the ObjectId).")
            st.caption(f"Record created_by: {user} at {rec['timestamp'].isoformat()} .")
        except Exception as e:
            st.error(f"Failed saving to DB: {e}")
