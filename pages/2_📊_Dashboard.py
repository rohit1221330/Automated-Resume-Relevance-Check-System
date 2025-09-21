import streamlit as st
import pandas as pd
from src.database import delete_result, fetch_all_results

st.set_page_config(
    page_title="Evaluation Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Evaluation Dashboard")
st.write(
    "View all past resume evaluations here. Use the sidebar to filter the results."
)

# --- Main Logic ---
def get_dashboard_view():
    # Fetch all data from the database
    df = fetch_all_results()

    if df.empty:
        st.warning("No evaluations found in the database yet.")
        return

    # --- Sidebar Filters ---
    st.sidebar.header("Filter Results")
    
    verdicts = df["verdict"].unique()
    selected_verdict = st.sidebar.multiselect(
        "Filter by Verdict", options=verdicts, default=verdicts
    )

    # Ensure final_score is numeric before finding min/max
    df['final_score'] = pd.to_numeric(df['final_score'], errors='coerce')
    df.dropna(subset=['final_score'], inplace=True)
    
    min_score, max_score = int(df["final_score"].min()), int(df["final_score"].max())
    score_range = st.sidebar.slider(
        "Filter by Score",
        min_value=min_score,
        max_value=max_score,
        value=(min_score, max_score),
    )

    # Apply filters
    filtered_df = df[
        (df["verdict"].isin(selected_verdict))
        & (df["final_score"] >= score_range[0])
        & (df["final_score"] <= score_range[1])
    ]

    st.metric("Total Evaluations", len(df))
    st.metric("Showing Evaluations", len(filtered_df))

    st.info("Select one or more rows in the table below and a 'Delete' button will appear.")

    # --- Display The Clean Dataframe with Selection ---
    selection = st.dataframe(
        filtered_df,
        use_container_width=True,
        on_select="rerun",
        selection_mode="multi-row",
        # Hide the index column from the user view
        hide_index=True 
    )

    # --- Delete Button Logic ---
    if selection["selection"]["rows"]:
        st.write("---")
        st.subheader("Delete Selected Evaluations")
        
        selected_indices = selection["selection"]["rows"]
        
        # --- THIS IS THE ROBUST FIX ---
        # 1. Create a new dataframe containing only the selected rows.
        selected_rows_df = filtered_df.iloc[selected_indices]
        
        # 2. Get the list of unique database IDs directly from this new dataframe.
        ids_to_delete = selected_rows_df["id"].tolist()
        
        # (Optional) For debugging, you can uncomment the line below to see the IDs
        # st.write("Selected database IDs to delete:", ids_to_delete)

        st.write("You have selected the following resumes for deletion:")
        for name in selected_rows_df["resume_filename"]:
            st.markdown(f"- `{name}`")

        if st.button("🗑️ Delete Selected Records", type="primary"):
            for eval_id in ids_to_delete:
                delete_result(int(eval_id)) # Use int() for extra safety
            st.success("Successfully deleted the selected records!")
            st.rerun()
    
    # --- Expander for details ---
    st.write("---")
    st.write("### Detailed Feedback")
    for index, row in filtered_df.iterrows():
        with st.expander(
            f"**{row['resume_filename']}** vs **{row['jd_filename']}** (Score: {row['final_score']})"
        ):
            st.markdown(f"**Verdict:** {row['verdict']}")
            st.markdown(f"**Strengths:** {row['strengths']}")
            st.markdown(f"**Weaknesses:** {row['weaknesses']}")
            st.markdown(f"**Suggestions:** {row['suggestions']}")
            st.markdown(f"**Missing Skills:** {row['missing_skills']}")
            st.markdown(f"_*Evaluated on: {row['timestamp']}_")

# Run the main function
if __name__ == "__main__":
    get_dashboard_view()