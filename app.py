import streamlit as st

from src.data_loader import load_projects_data


def configure_page() -> None:
    st.set_page_config(
        page_title="Tunisia Real-Estate Demand Intelligence",
        layout="wide",
    )


def render_home() -> None:
    st.title("Tunisia Real-Estate Demand Intelligence")
    st.markdown(
        """
        A real-estate demand intelligence platform for Tunisia.
        This page confirms the Phase 1 data foundation is ready and loaded.
        """
    )


def render_data_section() -> None:
    try:
        projects_df = load_projects_data()
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        st.error(f"Unable to load project dataset: {error}")
        st.info("Please verify `data/projects.csv` and try again.")
        return

    st.success("Phase 1 data foundation ready.")
    st.subheader("Project Dataset Preview")
    st.write(f"Projects loaded: **{len(projects_df)}**")
    st.dataframe(projects_df.head(12), use_container_width=True)
    st.caption("Showing the first 12 rows from `data/projects.csv`.")


def render_footer() -> None:
    st.caption("Add new sections by creating page files inside the `pages/` directory.")


def main() -> None:
    configure_page()
    render_home()
    render_data_section()
    render_footer()


if __name__ == "__main__":
    main()
