import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
def show_interactive_table(df, height=450):
    """Render a sortable, filterable, searchable interactive data grid."""
    if df is None or df.empty:
        st.info("No data available.")
        return
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
        floatingFilter=True,
    )
    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=20,
    )
    gb.configure_side_bar()
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True,
    )
    grid_options = gb.build()
    return AgGrid(
        df,
        gridOptions=grid_options,
        height=height,
        theme="streamlit",
        allow_unsafe_jscode=False,
        fit_columns_on_grid_load=True,
    )
