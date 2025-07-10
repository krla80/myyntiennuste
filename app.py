import streamlit as st
from ui import (
    render_sopimus_tab, 
    render_kulut_tab,
    render_ennuste_tab,
    render_summary_tab,
)
import texts

st.set_page_config(page_title=texts.PAGE_TITLE, layout='centered')

tab1, tab2, tab3, tab4 = st.tabs([
    texts.TAB1, texts.TAB2, texts.TAB3, texts.TAB4
])

with tab1:
    render_sopimus_tab()
with tab2:
    render_kulut_tab()
with tab3:
    render_ennuste_tab()
with tab4:
    render_summary_tab()
