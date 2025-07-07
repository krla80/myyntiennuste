import streamlit as st

st.set_page_config(page_title="Myyntiennuste", layout="centered")
st.title("Voimassaolevat sopimukset ja toteutuva myynti")

st.write("Syötä asiakkaat, joiden kanssa sinulla on jo myyntiä. Voit antaa jokaiselle asiakkaalle oman hinnan ja kappalemäärän tilikautena.")

# Tilapäinen tietorakenne asiakkaille
if "asiakkaat" not in st.session_state:
    st.session_state.asiakkaat = []

# Lomake uuden asiakkaan lisäämiseen
with st.form("uusi_asiakas"):
    nimi = st.text_input("Asiakkaan nimi")
    tuote = st.text_input("Tuote")
    sopimus= st.date_input("Sopimuksen päättymispäivä")
    a_hinta = st.number_input("Tuotteen/palvelun á-hinta (ei sisällä alv.,€)", min_value=0.0, step=1.0, format="%.2f")
    maara = st.number_input("Myyntimäärä tilikautena (kpl)", min_value=1, step=1)
    lisaus = st.form_submit_button("Lisää asiakas")

if lisaus and nimi:
    kokonaisarvo = a_hinta * maara
    st.session_state.asiakkaat.append({"nimi": nimi, "tuote":tuote, "sopimus":sopimus, "a_hinta": a_hinta, "maara": maara, "kokonaisarvo": kokonaisarvo})
    st.success(f"Asiakas '{nimi}' lisätty.")

# Asiakaslistan näyttö ja poisto
st.subheader("Asiakkaat")
poistettava = st.selectbox("Valitse poistettava asiakas", [a["nimi"] for a in st.session_state.asiakkaat] + ["-"], index=len(st.session_state.asiakkaat))
if poistettava != "-":
    if st.button("Poista valittu asiakas"):
        st.session_state.asiakkaat = [a for a in st.session_state.asiakkaat if a["nimi"] != poistettava]
        st.success(f"Asiakas '{poistettava}' poistettu.")

# Lasketaan kokonaisliikevaihto
if st.session_state.asiakkaat:
    st.subheader("Yhteenveto")
    total = sum(a["kokonaisarvo"] for a in st.session_state.asiakkaat)
    st.write("### Asiakkaat ja myynnit:")
    for a in st.session_state.asiakkaat:
        st.write(f"- {a['nimi']} (sopimus päättyy {a['sopimus']}): {a['a_hinta']:.2f} € × {a['maara']} kpl = {a['kokonaisarvo']:.2f} €")

    st.success(f"Yhteensä laskutettava: {total:.2f} €")
else:
    st.info("Ei vielä asiakkaita lisättynä.")