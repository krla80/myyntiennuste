import streamlit as st
import json
import os
from datetime import date

# Polut tiedostoille
SOPIMUKSET_FILE = "asiakkaat_sopimus.json"
ENNUSTE_FILE = "asiakkaat_ennuste.json"
PALKKAENNUSTE_FILE = "asiakkaat_palkkaennuste.json"

# Funktiot tiedostojen lataukseen ja tallennukseen
def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Ladataan tiedot sessioon tai tiedostosta
if "asiakkaat_sopimus" not in st.session_state:
    st.session_state.asiakkaat_sopimus = load_data(SOPIMUKSET_FILE)
if "asiakkaat_ennuste" not in st.session_state:
    st.session_state.asiakkaat_ennuste = load_data(ENNUSTE_FILE)
if "asiakkaat_palkkaennuste" not in st.session_state:
    st.session_state.asiakkaat_palkkaennuste = load_data(PALKKAENNUSTE_FILE)

st.set_page_config(page_title="Myyntiennuste", layout="centered")
st.title("Myyntiennuste ja sopimusten hallinta")

tab1, tab3, tab2, tab_summary = st.tabs(["Sopimukset", "Arvio tulevasta palkasta", "Myyntiennuste", "Yhteenveto keskeisistä luvuista"])

st.subheader("Lisää sopimus")
with tab1:
    
    st.write("Syötä asiakkaat, joiden kanssa sinulla on jo sopimus. Voit antaa jokaiselle asiakkaalle oman hinnan ja kappalemäärän tilikautena.")
    st.write(f" <span style='color:red; font-style: italic;'>Jos sopimus on päättynyt, näkyy se allaolevassa listassa punaisella. Poista sopimus listasta tai uusi sopimus ja vaihda uusi päättymispäivä.</span>", unsafe_allow_html=True)
    st.write(f" <span style='color:red; font-style: italic;'>Laskuri laskee mukaan kaikki listalle tallennetut sopimukset, vaikka sopimus olisikin päättynyt.</span>", unsafe_allow_html=True)

    with st.form("uusi_asiakas_sopimus"):
        nimi = st.text_input("Asiakkaan nimi", value=st.session_state.get("nimi_sopimus", ""), key="nimi_sopimus")
        tuote = st.text_input("Tuote", value=st.session_state.get("tuote_sopimus", ""), key="tuote_sopimus")
        sopimus = st.date_input("Sopimuksen päättymispäivä", value=st.session_state.get("sopimus_sopimus", date.today()), key="sopimus_sopimus")
        sijainti = st.text_input("Sopimuksen sijainti (onedrive-osoite, verkkolevy tms.)", value=st.session_state.get("sijainti_sopimus", ""), key="sijainti_sopimus")
        a_hinta = st.number_input("Tuotteen/palvelun á-hinta (ei sisällä alv., €)", min_value=0.0, step=1.0, format="%.2f", value=st.session_state.get("a_hinta_sopimus", 0.0), key="a_hinta_sopimus")
        maara = st.number_input("Myyntimäärä tilikautena (kpl)", min_value=1, step=1, value=st.session_state.get("maara_sopimus", 1), key="maara_sopimus")
        lisaus = st.form_submit_button("Lisää asiakas")

    if lisaus and nimi:
        kokonaisarvo = a_hinta * maara
        uusi_asiakas = {
            "nimi": nimi,
            "tuote": tuote,
            "sopimus": sopimus.isoformat(),
            "a_hinta": a_hinta,
            "maara": maara,
            "kokonaisarvo": kokonaisarvo
        }
        st.session_state.asiakkaat_sopimus.append(uusi_asiakas)
        save_data(SOPIMUKSET_FILE, st.session_state.asiakkaat_sopimus)
        st.success(f"Asiakas '{nimi}' lisätty sopimuksiin.")

    # Asiakaslistan näyttö ja poisto
    st.subheader("Sopimukset")
    if st.session_state.asiakkaat_sopimus:
        poistettava = st.selectbox("Valitse poistettava asiakas", [a["nimi"] for a in st.session_state.asiakkaat_sopimus] + ["-"], index=len(st.session_state.asiakkaat_sopimus))
        if poistettava != "-":
            if st.button("Poista valittu asiakas"):
                st.session_state.asiakkaat_sopimus = [a for a in st.session_state.asiakkaat_sopimus if a["nimi"] != poistettava]
                save_data(SOPIMUKSET_FILE, st.session_state.asiakkaat_sopimus)
                st.success(f"Asiakas '{poistettava}' poistettu sopimuksista.")
        st.write("### Sopimukset ja myynnit:")
        for a in st.session_state.asiakkaat_sopimus:
            st.write(f"- {a['nimi']} (sopimus päättyy {a['sopimus']}): {a['a_hinta']:.2f} € × {a['maara']} kpl = {a['kokonaisarvo']:.2f} €")
    else:
        st.info("Ei vielä sopimuksia lisättynä.")

    # Summa
    total_sopimus = sum(a["kokonaisarvo"] for a in st.session_state.asiakkaat_sopimus) if st.session_state.asiakkaat_sopimus else 0
    st.write(f"**Sopimusten kokonaisarvo yhteensä:** {total_sopimus:.2f} €")

with tab2:
    st.write("Ennusta ja suunnittele tähän tilikautesi tulevat asiakkaat tai tuotteet. Suunnittele siis tarvittava lisämyynti!")

    with st.form("uusi_asiakas_ennuste"):
        nimi = st.text_input("Asiakkaan nimi", value=st.session_state.get("nimi_ennuste", ""), key="nimi_ennuste")
        tuote = st.text_input("Tuote", value=st.session_state.get("tuote_ennuste", ""), key="tuote_ennuste")
        a_hinta = st.number_input("Tuotteen/palvelun á-hinta (ei sisällä alv., €)", min_value=0.0, step=1.0, format="%.2f", value=st.session_state.get("a_hinta_ennuste", 0.0), key="a_hinta_ennuste")
        maara = st.number_input("Myyntimäärä tilikautena (kpl)", min_value=1, step=1, value=st.session_state.get("maara_ennuste", 1), key="maara_ennuste")
        lisaus = st.form_submit_button("Lisää asiakas")

    if lisaus and nimi:
        kokonaisarvo = a_hinta * maara
        uusi_asiakas = {
            "nimi": nimi,
            "tuote": tuote,
            "a_hinta": a_hinta,
            "maara": maara,
            "kokonaisarvo": kokonaisarvo
        }
        st.session_state.asiakkaat_ennuste.append(uusi_asiakas)
        save_data(ENNUSTE_FILE, st.session_state.asiakkaat_ennuste)
        st.success(f"Asiakas '{nimi}' lisätty myyntiennusteeseen.")

    # Asiakaslistan näyttö ja poisto
    st.subheader("Myyntiennuste")
    if st.session_state.asiakkaat_ennuste:
        poistettava = st.selectbox("Valitse poistettava asiakas", [a["nimi"] for a in st.session_state.asiakkaat_ennuste] + ["-"], index=len(st.session_state.asiakkaat_ennuste))
        if poistettava != "-":
            if st.button("Poista valittu asiakas", key="poista_ennuste"):
                st.session_state.asiakkaat_ennuste = [a for a in st.session_state.asiakkaat_ennuste if a["nimi"] != poistettava]
                save_data(ENNUSTE_FILE, st.session_state.asiakkaat_ennuste)
                st.success(f"Asiakas '{poistettava}' poistettu myyntiennusteesta.")
        st.write("### Ennustetut asiakkaat ja myynnit:")
        for a in st.session_state.asiakkaat_ennuste:
            st.write(f"- {a['nimi']}: {a['a_hinta']:.2f} € × {a['maara']} kpl = {a['kokonaisarvo']:.2f} €")
    else:
        st.info("Ei vielä ennustettuja asiakkaita.")

    # Summa
    total_ennuste = sum(a["kokonaisarvo"] for a in st.session_state.asiakkaat_ennuste) if st.session_state.asiakkaat_ennuste else 0
    st.write(f"**Myyntiennusteen kokonaisarvo yhteensä:** {total_ennuste:.2f} €")

# Näytetään molempien välilehtien yhteissumma sivun alaosassa
st.markdown("---")
st.write(f"### Kokonaisarvo (sopimukset + ennuste): {total_sopimus + total_ennuste:.2f} €")

with tab3:
    st.write("Syötä arvioidut liiketoiminnan kulut kuukaudessa (ilman ALV:tä) ja veroprosentti.")

# Alustetaan lista, jos sitä ei ole vielä olemassa
    if "asiakkaat_palkkaennuste" not in st.session_state:
        st.session_state.asiakkaat_palkkaennuste = []

    with st.form("liiketoiminnan_kulut_palkka"):
        kulu = st.text_input("Kulu", value=st.session_state.get("kulu_ennuste", ""), key="kulu_ennuste")
        a_hinta = st.number_input("Kulun á_hinta kuukaudessa (ilman alv., €)", min_value=0.0, step=1.0, format="%.2f", value=st.session_state.get("a_hinta", 0.0), key="a_hinta")
        maara = st.number_input("Kulujen lukumäärä tilikautena (kpl)", min_value=1, step=1, value=st.session_state.get("maara", 1), key="maara")
        lisaus = st.form_submit_button("Lisää kulu")

    if lisaus and kulu:
        kokonaisarvo = a_hinta * maara
        uusi_kulu = {
            "kulu": kulu,
            "a_hinta": a_hinta,
            "maara": maara,
            "kokonaisarvo": kokonaisarvo
        }
        st.session_state.asiakkaat_palkkaennuste.append(uusi_kulu)
        save_data(PALKKAENNUSTE_FILE, st.session_state.asiakkaat_palkkaennuste)
        st.success(f"Kulu '{kulu}' lisätty.")

# Poistettava kulu -valinta
    if st.session_state.asiakkaat_palkkaennuste:
        poistettava_kulu = st.selectbox(
            "Valitse poistettava kulu",
            [f"{k['kulu']} ({k['a_hinta']:.2f} € × {k['maara']} kpl)"
            for k in st.session_state.asiakkaat_palkkaennuste
            if isinstance(k, dict) and all(key in k for key in ['kulu', 'a_hinta', 'maara'])
        ] + ["-"]
        )
   
        if poistettava_kulu != "-":
            if st.button("Poista valittu kulu"):
                # Poistetaan valittu kulu listasta
                st.session_state.asiakkaat_palkkaennuste = [
                    k for k in st.session_state.asiakkaat_palkkaennuste
                    if f"{k['kulu']} ({k['a_hinta']:.2f} € × {k['maara']} kpl)" != poistettava_kulu
                ]
                save_data(PALKKAENNUSTE_FILE, st.session_state.asiakkaat_palkkaennuste)
                st.success(f"Kulu '{poistettava_kulu}' poistettu.")

# Näytetään kaikki lisätyt kulut ja poistetaan tarvittaessa
    st.subheader("Lisätyt kulut:")
    if st.session_state.asiakkaat_palkkaennuste:
        for k in st.session_state.asiakkaat_palkkaennuste:
            if isinstance(k, dict) and all(key in k for key in ['kulu', 'a_hinta', 'maara', 'kokonaisarvo']):
                st.write(f"- {k['kulu']}: {k['a_hinta']:.2f} € × {k['maara']} kpl = {k['kokonaisarvo']:.2f} €")
    else:
        st.info("Ei lisättyjä kuluja.")

    kulut = st.number_input("Liiketoiminnan kulut yhteensä (€)", min_value=0.0, step=100.0, format="%.2f", key = "kulut")
    vero_prosentti = st.slider("Arvioitu veroprosentti (%)", min_value=0, max_value=55, value=st.session_state.get("veroprosentti",25))

    kokonaismyynti = total_sopimus + total_ennuste
    bruttopalkka = kokonaismyynti - kulut
    verot = bruttopalkka * (vero_prosentti / 100) if bruttopalkka > 0 else 0
    nettopalkka = bruttopalkka - verot if bruttopalkka > 0 else 0

    st.markdown(f"**Kokonaismyynti (ennuste + sopimus):** {kokonaismyynti:.2f} €")
    st.markdown(f"**Bruttopalkka (ennen veroja):** {bruttopalkka:.2f} €")
    st.markdown(f"**Arvioidut verot:** {verot:.2f} €")
    st.markdown(f"### Arvioitu nettopalkka: {nettopalkka:.2f} €")
