import streamlit as st


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

        This MVP foundation is prepared for multi-page expansion into:
        - Marketing intelligence
        - Forecasting
        - Risk-aware decision support
        - Map-based visualization
        """
    )
    st.success("Phase 0 setup complete.")
    st.caption("Add new sections by creating page files inside the `pages/` directory.")


def main() -> None:
    configure_page()
    render_home()


if __name__ == "__main__":
    main()
