# import streamlit as st
# import pandas as pd

# st.title("OPEN CI File Consolidate")

# uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# if uploaded_file:
#     df = pd.read_csv(uploaded_file)

#     st.subheader("Original Data")
#     st.write(df)

#     def consolidate_rows(group):
#         merged = {}
#         for col in group.columns:
#             merged[col] = ", ".join(group[col].dropna().astype(str).unique())
#         return pd.Series(merged)

#     consolidated_df = df.groupby(['name', 'borrower_type'], as_index=False).apply(consolidate_rows)

#     st.subheader("Consolidated Data")
#     st.write(consolidated_df)

#     @st.cache_data
#     def convert_df_to_csv(df):
#         return df.to_csv(index=False).encode('utf-8')

#     csv = convert_df_to_csv(consolidated_df)
#     st.download_button(
#         label="Download Consolidated CSV",
#         data=csv,
#         file_name="Ready-for-Uploading-Endo.csv",
#         mime="text/csv"
#     )


import streamlit as st
import pandas as pd

# Set page title and layout
st.set_page_config(page_title="OPEN CI File Consolidate", layout="wide")

# Title
st.title("📂 OPEN CI File Consolidator")

# File uploader
uploaded_file = st.file_uploader("📥 Upload your CSV file", type=["csv"])

if uploaded_file:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Display original data
    st.subheader("📊 Original Data")
    st.dataframe(df, use_container_width=True)

    # Count the total number of unique names in the original data
    original_unique_names = df['name'].nunique()

    # Consolidation function (unchanged from original code)
    def consolidate_rows(group):
        merged = {}
        for col in group.columns:
            merged[col] = ", ".join(group[col].dropna().astype(str).unique())
        return pd.Series(merged)

    # Consolidate the data
    consolidated_df = df.groupby(['name', 'borrower_type'], as_index=False).apply(consolidate_rows)

    # Count the total number of unique names after consolidation
    consolidated_unique_names = consolidated_df['name'].nunique()

    # Calculate rows consolidated (duplicates removed)
    rows_consolidated = len(df) - len(consolidated_df)

    # Display consolidated data
    st.subheader("🔍 Consolidated Data")
    st.dataframe(consolidated_df, use_container_width=True)

    # Consolidation Summary
    st.subheader("📋 Consolidation Summary")
    st.markdown(
        f"""
        - **Total Rows (Original):** {len(df):,}
        - **Total Rows (Consolidated):** {len(consolidated_df):,}
        - **Unique Names (Original):** {original_unique_names:,}
        - **Unique Names (Consolidated):** {consolidated_unique_names:,}
        - **Rows Consolidated (Duplicates Removed):** {rows_consolidated:,}
        """
    )

    # Download consolidated CSV
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(consolidated_df)
    st.download_button(
        label="📥 Download Consolidated CSV",
        data=csv,
        file_name="Ready-for-Uploading-Endo.csv",
        mime="text/csv"
    )

    # Data Visualization
    st.subheader("📈 Data Visualization")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Original Data Borrower Type Distribution")
        st.bar_chart(df['borrower_type'].value_counts(), use_container_width=True)
    with col2:
        st.markdown("### Consolidated Data Borrower Type Distribution")
        st.bar_chart(consolidated_df['borrower_type'].value_counts(), use_container_width=True)

    # Success Message
    st.success("✅ Data consolidated successfully! You can download the consolidated file above.")

else:
    st.info("Please upload a CSV file to start consolidating your data.")

