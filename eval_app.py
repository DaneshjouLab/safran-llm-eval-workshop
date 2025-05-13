import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide")
st.title("Discharge Summary Evaluation Interface")

completed_file = "completed_evaluations.csv"
if os.path.exists(completed_file):
    completed_df = pd.read_csv(completed_file)
    completed_ids = set(completed_df["note_id"])
else:
    completed_df = pd.DataFrame()
    completed_ids = set()

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    total_notes = len(pd.read_excel(uploaded_file)["note_id"].unique())
    completed_notes = len(completed_ids)
    progress = completed_notes / total_notes if total_notes > 0 else 0
    st.markdown(f"### ✅ Progress: {completed_notes} of {total_notes} completed ({progress * 100:.1f}%)")
    st.progress(progress)
    df = df[~df["note_id"].isin(completed_ids)]

    if not df.empty:
        selected_note_id = st.selectbox("Select note_id to evaluate", df["note_id"].unique())
        row = df[df["note_id"] == selected_note_id].iloc[0]

        st.subheader("Phase 1: Alteration Evaluation")
        st.markdown(f"**Alteration Type:** `{row['alteration_type']}`")

        col1, col2 = st.columns(5)
        with col1:
            st.markdown("**Original Summary**")
            st.code(row["original_summary"], language="text")
        with col2:
            st.markdown("**Altered Summary**")
            st.code(row["alterated_summary"], language="text")

        is_type_accurate = st.radio("1. Is the alteration successful based on its type?",
            ["Yes – consistent with its type", "No – does not match the type", "Unsure"])

        factual_score = st.slider("2. Factual Integrity Score (0–5) - How much factual content is preserved after an alteration?", 0, 5, 5, help="""
0 = Completely misleading or off-topic
1 = Very limited factual overlap
2 = Major omissions or alterations
3 = Moderate factual loss but main story intact
4 = Minor factual omissions
5 = All critical facts preserved
""")

        issues = st.multiselect("3. Types of Issues Introduced - "
        "Based on a side-by-side comparison, which types of factual content were lost or changed? (check all that apply):", [
            "Missing primary diagnosis",
            "Changed or removed treatments/interventions",
            "Missing follow-up instructions",
            "Medication differences",
            "Omitted key clinical events (like tests, hospital course)",
            "Contradictory information",
            "No major issues found"
        ])

        comment1 = st.text_area("Comments on Alteration (optional)")

        st.divider()
        st.subheader("Phase 2: Error Report Evaluation")
 
        st.markdown("Raw LLM Response (read-only)")
        st.markdown(row["llm_response"])
        response = None

        is_format_valid = st.radio("Is the model response correctly formatted as a dictionary?", ["Yes", "No", "Unsure"])

        st.markdown("1. Did the model correctly identify whether errors exist in each section?")
        col1, col2 = st.columns(2)
        with col1:
            diagnosis = st.radio("1. Primary Diagnosis", ["Yes", "No", "Unsure"], key="diag")
            treatment = st.radio("2. Treatments & Procedures", ["Yes", "No", "Unsure"], key="treat")
            followup = st.radio("3. Follow-up Instructions", ["Yes", "No", "Unsure"], key="follow")
        with col2:
            meds = st.radio("4. Medications", ["Yes", "No", "Unsure"], key="meds")
            events = st.radio("5. Clinical Events/Omissions", ["Yes", "No", "Unsure"], key="events")

        complete_score = st.slider("2. How complete is the model’s report? (0–5) Does the model mention all major factual differences between" \
        " the altered and original summaries?", 0, 5, 5, help="""
0 = Fails to detect obvious problems
1 = Major gaps or only a few issues caught
2 = Many important issues missed
3 = Several moderate omissions
4 = Captures most; a few minor points missed
5 = Captures all the differences
""")

        clarity_score = st.slider("3. How clear and understandable is the model’s explanation? (0–5) - " \
        "Is the text in the <Reasoning> section easy to follow and informative?", 0, 5, 5, help="""
0 = Incomprehensible
1 = Very confusing or misleading
2 = Hard to follow or unclear
3 = Somewhat understandable but vague
4 = Mostly clear, a few confusing parts
5 = Very clear, easy to understand
""")

        is_trustworthy = st.radio("4. Does the model seem trustworthy based on this evaluation?", [
            "Yes – it generally made reasonable, accurate judgments",
            "No – it made clear factual errors or missed major issues",
            "Unsure"
        ])

        comment2 = st.text_area("Comments on LLM Response (optional)")

        if st.button("✅ Save Evaluation"):
            new_row = {
                "note_id": selected_note_id,
                "alteration_type": row["alteration_type"],
                "alteration_accurate": is_type_accurate,
                "factual_score": factual_score,
                "issue_flags": "|".join(issues),
                "alteration_comment": comment1,
                "response_format_valid": is_format_valid,
                "correct_diagnosis": diagnosis,
                "correct_treatment": treatment,
                "correct_followup": followup,
                "correct_meds": meds,
                "correct_events": events,
                "completeness_score": complete_score,
                "clarity_score": clarity_score,
                "trustworthy": is_trustworthy,
                "llm_comment": comment2
            }
            completed_df = pd.concat([completed_df, pd.DataFrame([new_row])], ignore_index=True)
            completed_df.to_csv(completed_file, index=False)
            st.success(f"✅ Evaluation for note_id `{selected_note_id}` saved successfully!")
            time.sleep(2)
            st.rerun()
    else:
        st.success("🎉 All note_ids in this file have been evaluated!")