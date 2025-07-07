import streamlit as st
import pandas as pd

# Otsikko
st.title("Aloittavan yrittäjän myyntisuunnitelma")

# Kuvaus
st.write("""
Tässä voit täyttää oman myyntisuunnitelmasi vaihe vaiheelta.
""")

# Lomake
with st.form("myyntisuunnitelma_form"):
    yrityksen_nimi = st.text_input("Yrityksen nimi")
    tuotteet_palvelut = st.text_area("Mitä tuotteita/palveluita tarjoat?")
    asiakassegmentit = st.text_area("Kenelle myyt?")
    hinta = st.text_input("Hinnoittelun periaatteet")
    myyntikanavat = st.text_area("Missä myyt?")
    tavoitteet = st.text_area("Myynnin tavoitteet 3 kk / 6 kk")

    # Lähetä-painike
    submitted = st.form_submit_button("Tallenna")

# Näytä tulokset
if submitted:
    st.success("Suunnitelmasi on tallennettu lomakkeelle.")
    st.write("**Yritys:**", yrityksen_nimi)
    st.write("**Tuotteet/palvelut:**", tuotteet_palvelut)
    st.write("**Asiakassegmentit:**", asiakassegmentit)
    st.write("**Hinnoittelu:**", hinta)
    st.write("**Myyntikanavat:**", myyntikanavat)
    st.write("**Tavoitteet:**", tavoitteet)