# ui_submit_score.py
import streamlit as st
from db import get_predictions_collection
from datetime import datetime
from bson import ObjectId



def render_submit_score():
    """
    Student (or admin) may submit official score.
    Behavior (Option 1 chosen): update the most recent pending prediction
    for the logged-in user (created_by == username and actual_exam_score is None).
    Admin can optionally choose which student's pending record to update.
    """

    user = st.session_state.username
    role = st.session_state.role
    coll = get_predictions_collection()

    st.subheader("Submit Official Exam Score")

    if role == "admin":
        # Admin can select a user and the pending record to update
        # get distinct created_by with pending records
        pending_users = coll.distinct("created_by", {"actual_exam_score": None})
        if not pending_users:
            st.info("No pending records to update.")
            return
        selected_user = st.selectbox("Select student to update", pending_users)
        # list pending records for that student
        records = list(coll.find({"created_by": selected_user, "actual_exam_score": None}).sort("timestamp", -1))
        if not records:
            st.info("No pending records for selected student.")
            return
        # show brief info and select which to update
        options = [f"{r['_id']} | predicted: {r['predicted_exam_score']} | {r['timestamp']}" for r in records]
        choice = st.selectbox("Select record to update", options)
        chosen_idx = options.index(choice)
        chosen_rec = records[chosen_idx]
    else:
        # student: pick their latest pending record automatically
        chosen_rec = coll.find_one({"created_by": user, "actual_exam_score": None}, sort=[("timestamp", -1)])
        if not chosen_rec:
            st.info("You have no pending predictions to update.")
            return
        st.write("Updating your most recent pending prediction:")
        st.write(f"Predicted: {chosen_rec.get('predicted_exam_score')} — created at {chosen_rec.get('timestamp')}")

    actual_score = st.number_input("Enter Official Score (%)", min_value=0.0, max_value=100.0, value=0.0)
    if st.button("Submit Actual Score"):
        try:
            result = coll.update_one({"_id": chosen_rec["_id"]}, {"$set": {"actual_exam_score": float(actual_score), "updated_at": datetime.utcnow()}})
            if result.modified_count > 0:
                st.success("✅ Official score submitted and record updated.")
            else:
                st.warning("No changes made (maybe already updated).")
        except Exception as e:
            st.error(f"Failed to update record: {e}")
