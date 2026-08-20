import streamlit as st
import pandas as pd
import sqlite3
import time

from src.agent_graph import run_agent, run_batch
from data.sample_products import sample_products
from src.notifier import send_to_slack

st.set_page_config(page_title="Marketing Automation Agent", layout="wide")

st.title("Autonomous Marketing Content Agent")
st.caption("Classifies request type → RAG-grounded generation → self-critique → retry → logged & tracked")

TASK_LABELS = {
    "product_description": "Product Description",
    "ad_headline": "Ad Headline",
    "customer_reply": "Customer Reply",
}

tab1, tab2, tab3 = st.tabs(["Single Request", "Batch Run", "Stats Dashboard"])

with tab1:
    st.subheader("Send any marketing request")
    st.caption("The agent automatically detects whether this is a new product, an ad campaign, or a customer message — no need to specify.")

    request_input = st.text_area(
        "Request",
        placeholder=(
            "Examples:\n"
            "- Green Tea Antioxidant Serum, 8% EGCG extract, protects against environmental damage\n"
            "- Our summer sale campaign for the Vitamin C Serum\n"
            "- Customer says the moisturizer broke them out, they want a refund"
        ),
        height=100,
    )

    if st.button("Generate", key="single"):
        if request_input:
            with st.status("Agent working...", expanded=True) as status:
                st.write("Classifying request type...")
                st.write("Retrieving relevant brand context...")
                st.write("Generating content...")
                result = run_agent(request_input)
                st.write("Self-critiquing output...")
                time.sleep(0.2)
                status.update(
                    label=f"Done — detected as {TASK_LABELS.get(result['task_type'], result['task_type'])}",
                    state="complete",
                )

            badge = TASK_LABELS.get(result["task_type"], result["task_type"])
            st.info(f"**Detected type:** {badge}")
            st.success(f"**Status:** {result['status']} | **Score:** {result['score']}/10")
            st.write("**Output:**")
            st.write(result["description"])

            if result["status"] == "APPROVED":
                send_to_slack(request_input, result["description"], result["score"], result["status"])
                st.caption("Sent to Slack")

            if len(result["attempt_history"]) > 1:
                st.warning(f"Took {len(result['attempt_history'])} attempts (retried due to low initial score)")
                with st.expander("See attempt history"):
                    for a in result["attempt_history"]:
                        st.write(f"Attempt {a['attempt']}: Score {a['score']}/10 — {a['reason']}")
        else:
            st.warning("Enter a request first.")

with tab2:
    st.subheader("Batch process multiple requests")
    st.write(f"Sample batch of {len(sample_products)} product requests loaded from `sample_products.py`")
    st.caption("Each request is independently classified — this batch happens to be all products, but the agent handles mixed types the same way.")

    if st.button("Run Batch", key="batch"):
        progress_bar = st.progress(0)
        results_placeholder = st.empty()
        results = []

        for i, product in enumerate(sample_products):
            result = run_agent(product)
            results.append({
                "Request": product[:45] + "...",
                "Type": TASK_LABELS.get(result["task_type"], result["task_type"]),
                "Score": result["score"],
                "Status": result["status"],
                "Attempts": len(result["attempt_history"]),
            })
            progress_bar.progress((i + 1) / len(sample_products))
            results_placeholder.dataframe(pd.DataFrame(results), use_container_width=True)

        approved = sum(1 for r in results if r["Status"] == "APPROVED")
        st.success(f"Processed {len(results)} requests — {approved} approved, {len(results) - approved} flagged for review")

with tab3:
    st.subheader("Performance Stats")

    conn = sqlite3.connect("agent_logs.db")
    df = pd.read_sql_query("SELECT * FROM runs ORDER BY id DESC", conn)
    conn.close()

    if len(df) > 0:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Runs", len(df))
        col2.metric("Avg Score", round(df["final_score"].mean(), 2))
        col3.metric("Approval Rate", f"{round((df['status']=='APPROVED').mean()*100, 1)}%")
        col4.metric("Avg Duration", f"{round(df['duration_seconds'].mean(), 1)}s")

        st.line_chart(df.sort_values("id")["final_score"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No runs logged yet — generate something first!")