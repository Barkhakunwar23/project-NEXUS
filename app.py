import streamlit as st
import pandas as pd
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="Project Nexus", page_icon="🔎", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #0f1426 0%, #171d35 100%); color: #f5f7ff;}
[data-testid="stMetric"] {background: #1b233b; padding: 16px; border-radius: 14px; border: 1px solid #37415f;}
div.stButton > button {border-radius: 10px; border: 1px solid #795dff;}
</style>
""", unsafe_allow_html=True)

st.title("🔎 PROJECT NEXUS")
st.caption("AI-Powered Customer Problem Intelligence System | Classroom prototype")
st.info("Demo note: included dataset is synthetic example data, not real customer feedback or verified claims about any company.")

DATA_PATH = Path(__file__).parent / "sample_feedback.csv"

def classify(text):
    t = text.lower()
    rules = [
        (["repeat", "same", "repetitive", "similar videos", "similar reels"], "Repetitive recommendations"),
        (["privacy", "permission", "microphone", "location", "personal data"], "Privacy settings clarity"),
        (["search", "results", "find a product"], "Search usefulness"),
        (["return", "refund", "return policy"], "Return policy clarity"),
        (["size", "availability", "product page"], "Product information clarity"),
        (["control", "not interested", "feed", "topic"], "User control"),
        (["ad", "advertisement", "personalized"], "Ad relevance / transparency"),
    ]
    for keywords, category in rules:
        if any(k in t for k in keywords):
            return category
    return "General user experience"

def suggest(category):
    suggestions = {
        "Repetitive recommendations": "Test a user-facing control for content diversity; compare satisfaction and relevance before and after.",
        "Privacy settings clarity": "Provide clearer permission explanations and a simple privacy-settings guide; do not infer spying from ads alone.",
        "Search usefulness": "Review search feedback and test clearer filters or better query refinement.",
        "Return policy clarity": "Make return conditions easier to find and test whether users understand them.",
        "Product information clarity": "Improve visibility of size/availability information and test task completion.",
        "User control": "Test clearer preference controls such as 'show less' or topic selection, where supported.",
        "Ad relevance / transparency": "Explain ad-personalisation controls clearly and evaluate user-reported relevance.",
        "General user experience": "Ask one follow-up question and collect more feedback before recommending a specific change."
    }
    return suggestions.get(category, suggestions["General user experience"])

if "feedback" not in st.session_state:
    if DATA_PATH.exists():
        st.session_state.feedback = pd.read_csv(DATA_PATH)
    else:
        st.session_state.feedback = pd.DataFrame(columns=["platform","area","customer_feedback","problem_category","priority_1_low_3_high","data_label"])

left, right = st.columns([1.05, 1.45], gap="large")

with left:
    st.subheader("💬 Customer problem chatbot")
    platform = st.selectbox("Choose a platform", ["Instagram", "YouTube", "Amazon", "Myntra", "Google", "Other"])
    message = st.text_area("Describe the problem in your own words", placeholder="Example: I keep seeing similar videos...")
    priority = st.slider("How important is this problem to you?", 1, 3, 2, help="1 = low, 2 = medium, 3 = high")
    if st.button("Analyse my problem", use_container_width=True):
        if not message.strip():
            st.warning("Please describe a problem first.")
        else:
            category = classify(message)
            st.session_state.last_result = {
                "platform": platform,
                "message": message.strip(),
                "category": category,
                "priority": priority,
                "suggestion": suggest(category)
            }
            new_row = {
                "platform": platform,
                "area": category,
                "customer_feedback": message.strip(),
                "problem_category": category,
                "priority_1_low_3_high": priority,
                "data_label": "User-submitted demo feedback"
            }
            st.session_state.feedback = pd.concat([st.session_state.feedback, pd.DataFrame([new_row])], ignore_index=True)

    if "last_result" in st.session_state:
        r = st.session_state.last_result
        st.success(f"Detected category: **{r['category']}**")
        st.write("**Possible next step for the user:**")
        st.write("Review the platform's available settings/help options related to this issue. The exact options depend on the platform and version.")
        st.write("**Suggested company experiment:**")
        st.write(r["suggestion"])
        st.caption("This prototype uses transparent keyword rules, not a trained AI model. Review the result before relying on it.")

with right:
    st.subheader("📊 Company intelligence dashboard")
    data = st.session_state.feedback.copy()
    if data.empty:
        st.warning("No feedback yet.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Feedback entries", len(data))
        c2.metric("Platforms", data["platform"].nunique())
        c3.metric("Problem categories", data["problem_category"].nunique())

        selected_platforms = st.multiselect("Filter platforms", sorted(data["platform"].dropna().unique()), default=sorted(data["platform"].dropna().unique()))
        filtered = data[data["platform"].isin(selected_platforms)] if selected_platforms else data.iloc[0:0]
        if not filtered.empty:
            st.markdown("**Most reported problem categories**")
            counts = filtered["problem_category"].value_counts()
            st.bar_chart(counts)
            st.markdown("**Feedback by platform**")
            st.bar_chart(filtered["platform"].value_counts())
            st.markdown("**Recent feedback**")
            st.dataframe(filtered[["platform","customer_feedback","problem_category","priority_1_low_3_high","data_label"]].tail(12), use_container_width=True, hide_index=True)
            csv = filtered.to_csv(index=False).encode("utf-8")
            st.download_button("Download filtered feedback CSV", csv, "nexus_feedback_export.csv", "text/csv")
        else:
            st.write("Choose one or more platforms to view insights.")

st.divider()
st.subheader("🧭 How to explain this prototype")
st.markdown("""
1. A user submits a problem.
2. The prototype assigns a category using transparent keyword rules.
3. It shows a possible improvement to test.
4. Feedback appears in an aggregate dashboard.
5. A real deployment would need secure storage, privacy review, better NLP/AI, user testing and validated data.
""")
st.caption("Privacy: do not enter passwords, private messages, health details or other sensitive personal information.")
