#!/usr/bin/env python3
"""
Streamlit Tabular Architecture Comparison Dashboard
==================================================
Displays flat tabular comparison with binary indicators and filtering capabilities.
Run with: streamlit run streamlit_tabular_comparison.py
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go


def load_comparison_data():
    """Load the tabular comparison data"""
    data_file = Path("comparison_output/tabular_architecture_comparison.csv")

    if not data_file.exists():
        st.error(f"Comparison data not found at {data_file}")
        st.info(
            "Please run the comparison script first: `python compare_architectures_tabular.py`"
        )
        return None

    try:
        df = pd.read_csv(data_file)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def create_summary_metrics(df):
    """Create summary metrics cards"""
    total_archs = len(df)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="Total Architectures", value=total_archs)

    with col2:
        services_same = df["Services_Same"].sum()
        st.metric(
            label="Services Same",
            value=f"{services_same}/{total_archs}",
            delta=f"{services_same/total_archs*100:.1f}%",
        )

    with col3:
        components_same = df["Components_Same"].sum()
        st.metric(
            label="Components Same",
            value=f"{components_same}/{total_archs}",
            delta=f"{components_same/total_archs*100:.1f}%",
        )

    with col4:
        attributes_same = df["Attributes_Same"].sum()
        st.metric(
            label="Attributes Same",
            value=f"{attributes_same}/{total_archs}",
            delta=f"{attributes_same/total_archs*100:.1f}%",
        )

    with col5:
        configurations_same = df["Configurations_Same"].sum()
        st.metric(
            label="Configurations Same",
            value=f"{configurations_same}/{total_archs}",
            delta=f"{configurations_same/total_archs*100:.1f}%",
        )


def create_summary_charts(df):
    """Create summary charts"""

    col1, col2 = st.columns(2)

    with col1:
        # Similarity by level chart
        similarity_data = {
            "Level": ["Services", "Components", "Attributes", "Configurations"],
            "Same_Count": [
                df["Services_Same"].sum(),
                df["Components_Same"].sum(),
                df["Attributes_Same"].sum(),
                df["Configurations_Same"].sum(),
            ],
            "Different_Count": [
                len(df) - df["Services_Same"].sum(),
                len(df) - df["Components_Same"].sum(),
                len(df) - df["Attributes_Same"].sum(),
                len(df) - df["Configurations_Same"].sum(),
            ],
        }

        similarity_df = pd.DataFrame(similarity_data)
        similarity_df["Same_Percentage"] = (
            similarity_df["Same_Count"]
            / (similarity_df["Same_Count"] + similarity_df["Different_Count"])
            * 100
        )

        fig1 = px.bar(
            similarity_df,
            x="Level",
            y="Same_Percentage",
            title="Similarity Percentage by Level",
            color="Same_Percentage",
            color_continuous_scale="RdYlGn",
            range_color=[0, 100],
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Architecture differences pattern
        df["Total_Differences"] = 4 - (
            df["Services_Same"]
            + df["Components_Same"]
            + df["Attributes_Same"]
            + df["Configurations_Same"]
        )

        diff_counts = df["Total_Differences"].value_counts().sort_index()

        fig2 = px.pie(
            values=diff_counts.values,
            names=[f"{int(x)} Differences" for x in diff_counts.index],
            title="Distribution of Architectures by Number of Differences",
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)


def display_detailed_table(df):
    """Display the detailed comparison table with filters"""

    st.subheader("🔍 Detailed Architecture Comparison")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        # Filter by differences
        difference_filter = st.selectbox(
            "Filter by Differences",
            [
                "All Architectures",
                "Only Identical",
                "Only Different",
                "Services Different",
                "Components Different",
                "Attributes Different",
                "Configurations Different",
            ],
        )

    with col2:
        # Search by architecture ID
        search_term = st.text_input("Search Architecture ID", "")

    with col3:
        # Number of rows to display
        num_rows = st.selectbox("Rows to Display", [10, 25, 50, 100, "All"], index=1)

    # Apply filters
    filtered_df = df.copy()

    if difference_filter == "Only Identical":
        filtered_df = filtered_df[
            (filtered_df["Services_Same"] == 1)
            & (filtered_df["Components_Same"] == 1)
            & (filtered_df["Attributes_Same"] == 1)
            & (filtered_df["Configurations_Same"] == 1)
        ]
    elif difference_filter == "Only Different":
        filtered_df = filtered_df[
            (filtered_df["Services_Same"] == 0)
            | (filtered_df["Components_Same"] == 0)
            | (filtered_df["Attributes_Same"] == 0)
            | (filtered_df["Configurations_Same"] == 0)
        ]
    elif difference_filter == "Services Different":
        filtered_df = filtered_df[filtered_df["Services_Same"] == 0]
    elif difference_filter == "Components Different":
        filtered_df = filtered_df[filtered_df["Components_Same"] == 0]
    elif difference_filter == "Attributes Different":
        filtered_df = filtered_df[filtered_df["Attributes_Same"] == 0]
    elif difference_filter == "Configurations Different":
        filtered_df = filtered_df[filtered_df["Configurations_Same"] == 0]

    if search_term:
        filtered_df = filtered_df[
            filtered_df["Architecture"].str.contains(search_term, case=False, na=False)
        ]

    if num_rows != "All":
        filtered_df = filtered_df.head(int(num_rows))

    st.write(f"Showing {len(filtered_df)} of {len(df)} architectures")

    # Create styled dataframe
    def style_binary_columns(val):
        if val == 1:
            return "background-color: #d4edda; color: #155724"  # Green for same
        elif val == 0:
            return "background-color: #f8d7da; color: #721c24"  # Red for different
        return ""

    # Apply styling to binary columns
    styled_df = filtered_df.style.map(
        style_binary_columns,
        subset=[
            "Services_Same",
            "Components_Same",
            "Attributes_Same",
            "Configurations_Same",
        ],
    )

    st.dataframe(styled_df, use_container_width=True)


def display_architecture_details(df):
    """Display detailed view for a specific architecture"""

    st.subheader("🔬 Architecture Deep Dive")

    # Architecture selector
    selected_arch = st.selectbox(
        "Select Architecture for Detailed View", df["Architecture"].tolist()
    )

    if selected_arch:
        arch_data = df[df["Architecture"] == selected_arch].iloc[0]

        # Status overview
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status = "✅ Same" if arch_data["Services_Same"] == 1 else "❌ Different"
            st.metric("Services", status)

        with col2:
            status = "✅ Same" if arch_data["Components_Same"] == 1 else "❌ Different"
            st.metric("Components", status)

        with col3:
            status = "✅ Same" if arch_data["Attributes_Same"] == 1 else "❌ Different"
            st.metric("Attributes", status)

        with col4:
            status = (
                "✅ Same" if arch_data["Configurations_Same"] == 1 else "❌ Different"
            )
            st.metric("Configurations", status)

        # Detailed differences
        st.subheader("📋 Detailed Differences")

        # Services differences
        if arch_data["Services_Same"] == 0:
            with st.expander("🔧 Services Differences", expanded=True):
                st.write(arch_data["Services_Differences"])

        # Components differences
        if arch_data["Components_Same"] == 0:
            with st.expander("⚙️ Components Differences", expanded=True):
                st.write(arch_data["Components_Differences"])

        # Attributes differences
        if arch_data["Attributes_Same"] == 0:
            with st.expander("🏷️ Attributes Differences", expanded=True):
                st.write(arch_data["Attributes_Differences"])

        # Configurations differences
        if arch_data["Configurations_Same"] == 0:
            with st.expander("⚡ Configurations Differences", expanded=True):
                st.write(arch_data["Configurations_Differences"])

        # Reasoning description
        with st.expander("💡 Reasoning Description", expanded=False):
            st.write(arch_data["Reasoning_Description"])


def main():
    """Main Streamlit application"""

    st.set_page_config(
        page_title="Architecture Comparison Dashboard", page_icon="🏗️", layout="wide"
    )

    st.title("🏗️ Architecture Comparison Dashboard")
    st.markdown("**Tabular comparison of baseline vs enhanced cloud architectures**")

    # Load data
    df = load_comparison_data()

    if df is None:
        return

    # Tabs
    tab1, tab2, tab3 = st.tabs(
        ["📊 Overview", "📋 Detailed Table", "🔬 Architecture Deep Dive"]
    )

    with tab1:
        st.header("📊 Comparison Overview")
        create_summary_metrics(df)
        st.markdown("---")
        create_summary_charts(df)

        # Quick insights
        st.subheader("💡 Quick Insights")

        total_archs = len(df)
        identical_archs = len(
            df[
                (df["Services_Same"] == 1)
                & (df["Components_Same"] == 1)
                & (df["Attributes_Same"] == 1)
                & (df["Configurations_Same"] == 1)
            ]
        )

        col1, col2 = st.columns(2)

        with col1:
            st.info(
                f"**{identical_archs}/{total_archs}** architectures are completely identical"
            )

            most_different_level = [
                "Services",
                "Components",
                "Attributes",
                "Configurations",
            ][
                [
                    df["Services_Same"].sum(),
                    df["Components_Same"].sum(),
                    df["Attributes_Same"].sum(),
                    df["Configurations_Same"].sum(),
                ].index(
                    min(
                        [
                            df["Services_Same"].sum(),
                            df["Components_Same"].sum(),
                            df["Attributes_Same"].sum(),
                            df["Configurations_Same"].sum(),
                        ]
                    )
                )
            ]
            st.warning(f"**{most_different_level}** level has the most differences")

        with col2:
            if total_archs - identical_archs > 0:
                st.error(
                    f"**{total_archs - identical_archs}** architectures have differences"
                )

            # Find most common difference pattern
            df["Diff_Pattern"] = (
                df["Services_Same"].astype(str)
                + "-"
                + df["Components_Same"].astype(str)
                + "-"
                + df["Attributes_Same"].astype(str)
                + "-"
                + df["Configurations_Same"].astype(str)
            )
            most_common_pattern = (
                df["Diff_Pattern"].mode()[0]
                if len(df["Diff_Pattern"].mode()) > 0
                else "Unknown"
            )
            st.info(f"Most common pattern: **{most_common_pattern}** (S-C-A-Cfg)")

    with tab2:
        display_detailed_table(df)

    with tab3:
        display_architecture_details(df)

    # Footer
    st.markdown("---")
    st.markdown(
        "**Legend:** 1 = Same between baseline and enhanced | 0 = Different | "
        "S=Services, C=Components, A=Attributes, Cfg=Configurations"
    )


if __name__ == "__main__":
    main()
