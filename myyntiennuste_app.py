import streamlit as st
import json
import os
from datetime import date
query_params = st.query_params
user_id = query_params.get("user", ["default_user"])[0]

# Polut tiedostoille
SOPIMUKSET_FILE = f"{user_id}_asiakkaat_sopimus.json"
ENNUSTE_FILE = f"{user_id}_asiakkaat_ennuste.json"
PALKKAENNUSTE_FILE = f"{user_id}_asiakkaat_palkkaennuste.json"

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
st.markdown('<h1 style="color:#4EA72E;">Myyntiennuste ja sopimusten hallinta</h1>', unsafe_allow_html=True)

tab1, tab3, tab2, tab_summary = st.tabs(["Sopimukset", "Arvio tulevasta palkasta", "Myyntiennuste",  "Yhteenveto keskeisistä luvuista"])

from datetime import date, datetime

voimassa_olevat_sopimukset = [
    a for a in st.session_state.asiakkaat_sopimus
    if datetime.fromisoformat(a["sopimus"]).date() >= date.today()
]

with tab1:
    st.write("Syötä asiakkaat, joiden kanssa sinulla on jo sopimus. Voit antaa jokaiselle asiakkaalle oman hinnan ja kappalemäärän tilikautena.")

    st.write(f" <span style='color:red; font-style: italic;'>Jos sopimus on päättynyt, näkyy se allaolevassa listassa punaisella. Poista sopimus listasta tai uusi sopimus ja vaihda uusi päättymispäivä.</span>", unsafe_allow_html=True)

    st.write(f" <span style='color:red; font-style: italic;'>Laskuri laskee mukaan vain voimassaolevat sopimukset. Jos sopimus jatkuu, vaihda sopimuksen päättymispäivä.</span>", unsafe_allow_html=True)

    st.subheader("Lisää sopimus")
    with st.form("uusi_asiakas_sopimus"):
        nimi = st.text_input("Asiakkaan nimi", value=st.session_state.get("nimi_sopimus", ""), key="nimi_sopimus")
        tuote = st.text_input("Yksilöivä palvelun nimi tai sopimuksen tunnus", value=st.session_state.get("tuote_sopimus", ""), key="tuote_sopimus")
        sopimus = st.date_input("Sopimuksen päättymispäivä", value=st.session_state.get("sopimus_sopimus", date.today()), key="sopimus_sopimus")
        sijainti = st.text_input("Sopimuksen sijainti (onedrive-osoite, verkkolevy tms.)", value=st.session_state.get("sijainti_sopimus", ""), key="sijainti_sopimus")
        a_hinta = st.number_input("Tuotteen/palvelun á-hinta (ilman alv., €)", min_value=0.0, step=1.0, format="%.2f", value=st.session_state.get("a_hinta_sopimus", 0.0), key="a_hinta_sopimus")
        maara = st.number_input("Myyntimäärä tilikautena (kpl)", min_value=1, step=1, value=st.session_state.get("maara_sopimus", 1), key="maara_sopimus")
        lisaus = st.form_submit_button("Lisää asiakas")

    if lisaus and nimi:
        kokonaisarvo = a_hinta * maara
        uusi_asiakas = {
            "nimi": nimi,
            "tuote": tuote,
            "sopimus": sopimus.isoformat(),
            "sijainti": sijainti,
            "a_hinta": a_hinta,
            "maara": maara,
            "kokonaisarvo": kokonaisarvo
        }
        st.session_state.asiakkaat_sopimus.append(uusi_asiakas)
        save_data(SOPIMUKSET_FILE, st.session_state.asiakkaat_sopimus)
        st.success(f"Asiakas '{nimi}' lisätty sopimuksiin.")


    if "asiakkaat_sopimus" in st.session_state:
        st.write("### Sopimukset ja myynnit:")
        for a in st.session_state.asiakkaat_sopimus:
            loppupvm = datetime.fromisoformat(a['sopimus']).date()
            if loppupvm <= date.today():
                st.markdown(f"- <span style='color: red;'> {a['nimi']} (sopimus päättyy {a['sopimus']}): {a['tuote']}: {a['a_hinta']:.2f} € × {a['maara']} kpl = {a['kokonaisarvo']:.2f} €</span>", unsafe_allow_html=True)

            else:
                st.write(f"- {a['nimi']} (sopimus päättyy {a['sopimus']}): {a['a_hinta']:.2f} € × {a['maara']} kpl = {a['kokonaisarvo']:.2f} €")
    else:
        st.info("Ei vielä sopimuksia lisättynä.")

    # Asiakaslistan näyttö ja poisto
    st.subheader("Poista olemassa oleva sopimus")
    if st.session_state.asiakkaat_sopimus:
        poistettavat = ["- Valitse sopimus -"] + [f'{a["nimi"]} ({a["tuote"]})' for a in st.session_state.asiakkaat_sopimus
	]
        poistettava = st.selectbox("Valitse poistettava sopimus", poistettavat)

        if poistettava != "- Valitse sopimus -":
            if st.button("Poista valittu sopimus"):
                st.session_state.asiakkaat_sopimus = [
                    a for a in st.session_state.asiakkaat_sopimus if a["nimi"] != poistettava
                ]
                save_data(SOPIMUKSET_FILE, st.session_state.asiakkaat_sopimus)
                st.success(f"Sopimus '{poistettava}' poistettu.")
    
    # Lomake olemassa olevan sopimuksen muokkaamiseksi

    st.subheader("Muokkaa olemassa olevaa sopimusta")

    if st.session_state.asiakkaat_sopimus:
        # Rakennetaan valintalistan vaihtoehdot: ensin tyhjä, sitten asiakkaat
        valintaoptiot = ["- Valitse sopimus -"] + [
            f"{a['nimi']} {a["tuote"]} (sopimus päättyy {a['sopimus']})"
            for a in st.session_state.asiakkaat_sopimus
        ]
        valittu = st.selectbox("Valitse sopimus", options=valintaoptiot)

        # Tarkistetaan että käyttäjä on tehnyt valinnan
        if valittu != "- Valitse sopimus -":
            # Haetaan valitun asiakkaan indeksi ja tiedot
            valittu_index = valintaoptiot.index(valittu) - 1  # koska ensimmäinen on tyhjä
            valittu_sopimus = st.session_state.asiakkaat_sopimus[valittu_index]

            # Näytetään lomake valitun asiakkaan tietojen muokkaamiseksi
            with st.form("muokkaa_sopimus"):
                nimi = st.text_input("Asiakkaan nimi", value=valittu_sopimus["nimi"])
                tuote = st.text_input("Tuote", value=valittu_sopimus["tuote"])
                sopimus = st.date_input("Sopimuksen päättymispäivä", value=datetime.fromisoformat(valittu_sopimus["sopimus"]).date())
                sijainti = st.text_input("Sopimuksen sijainti", value=valittu_sopimus["sijainti"])    
                a_hinta = st.number_input("Tuotteen/palvelun á-hinta (ilman alv., €)", min_value=0.0, step=1.0, format="%.2f", value=valittu_sopimus["a_hinta"])
                maara = st.number_input("Myyntimäärä tilikautena (kpl)", min_value=1, step=1, value=valittu_sopimus["maara"])
                tallenna = st.form_submit_button("Tallenna muutokset")
            
            
            if tallenna:
                st.session_state.asiakkaat_sopimus[valittu_index] = {
                    "nimi": nimi,
                    "tuote": tuote,
                    "sopimus": sopimus.isoformat(),
	            "sijainti": sijainti,		
                    "a_hinta": a_hinta,
                    "maara": maara,
                    "kokonaisarvo": a_hinta * maara,
                    
                }
                save_data(SOPIMUKSET_FILE, st.session_state.asiakkaat_sopimus)
                st.success(f"Sopimus asiakkaalle '{nimi}' päivitetty onnistuneesti.")
    

    # Summa
    total_sopimus = sum(a["kokonaisarvo"] for a in st.session_state.asiakkaat_sopimus if datetime.fromisoformat(a["sopimus"]).date() >= date.today()) if st.session_state.asiakkaat_sopimus else 0
    st.write(f"<h3 style='color:#4EA72E;'>Jo tehtyjen sopimusten arvo yhteensä:{total_sopimus:.2f} €</h3>", unsafe_allow_html=True)

with tab2:
    st.write("Ennusta ja suunnittele tähän tilikautesi tulevat asiakkaat, palvelut ja tuotteet. Suunnittele siis tarvittava lisämyynti!")

    st.write("Voit suunnitella kenelle aiot myydä, mitä palveluita tai tuotteita aiot myydä. Ennustetut myynnit siirtyvät suoraan Arvio tulevasta palkka lehdestä, jolloin näet tavoitemyyntisi vaikutuksen kuukausipalkkaan.")

    st.markdown("<span style='color:red; font-style: italic;'>Jos ennustettu myyntisi ei ole aktiivinen, ei ennustetta lasketa jo tehtyjen sopimusten ja ennustetun myynnin kokonaisarvoon. Voit siis valintasi mukaan jättää \"hävityn\" kaupan listalle ei-aktiiviseksi tai poistaa sen kokonaan. Ei aktiiviset ennusteet näkyvät punaisella allaolevalla listalla.</span>", unsafe_allow_html=True)

    st.subheader("Lisää uusi ennuste")
    with st.form("uusi_asiakas_ennuste"):
        nimi = st.text_input("Asiakkaan nimi", value=st.session_state.get("nimi_ennuste", ""), key="nimi_ennuste")
        tuote = st.text_input("Tuote", value=st.session_state.get("tuote_ennuste", ""), key="tuote_ennuste")
        a_hinta = st.number_input("Tuotteen/palvelun á-hinta (ilman alv., €)", min_value=0.0, step=1.0, format="%.2f", value=st.session_state.get("a_hinta_ennuste", 0.0), key="a_hinta_ennuste")
        maara = st.number_input("Myyntimäärä tilikautena (kpl)", min_value=1, step=1, value=st.session_state.get("maara_ennuste", 1), key="maara_ennuste")
        sijainti = st.text_input("Tarjousdokumenttien sijainti", value=st.session_state.get("sijainti_ennuste", ""), key="sijainti_ennuste")    
        aktiivinen = st.checkbox("Aktiivinen", value=True)
        lisaus = st.form_submit_button("Lisää asiakas")

    if lisaus and nimi:
        kokonaisarvo = a_hinta * maara
        uusi_asiakas = {
            "nimi": nimi,
            "tuote": tuote,
            "a_hinta": a_hinta,
            "maara": maara,
            "sijainti": sijainti,		
            "kokonaisarvo": kokonaisarvo,
            "aktiivinen": aktiivinen
        }
        st.session_state.asiakkaat_ennuste.append(uusi_asiakas)
        save_data(ENNUSTE_FILE, st.session_state.asiakkaat_ennuste)
        st.success(f"Asiakas '{nimi}' lisätty myyntiennusteeseen.")

    #Näytä ennusteet
    if "asiakkaat_ennuste" in st.session_state and st.session_state.asiakkaat_ennuste:
        st.write("### Ennustetut asiakkaat ja myynnit:")
        for a in st.session_state.asiakkaat_ennuste:
            aktiivinen = a.get("aktiivinen", True)
            teksti = f"- {a['nimi']}: {a['tuote']}: {a['a_hinta']:.2f} € × {a['maara']} kpl = {a['kokonaisarvo']:.2f} €"
            if not aktiivinen:
                teksti += " (ei aktiivinen)"
                st.markdown(f"- <span style='color: red;'>{a['nimi']}: {a['tuote']}: {a['a_hinta']:.2f} € × {a['maara']} kpl = {a['kokonaisarvo']:.2f} €</span>", unsafe_allow_html=True)
            else:
                st.write(teksti)
    else:
        st.info("Ei vielä ennustettuja asiakkaita.")

    # Asiakaslistan poisto
    st.subheader("Poista olemassa oleva ennuste")
    if st.session_state.asiakkaat_ennuste:
        poistettava = st.selectbox("Valitse poistettava ennuste", ["- Valitse ennuste -"] + [f"{a['nimi']} (tuote {a['tuote']})" for a in st.session_state.asiakkaat_ennuste], index=0
        )

        if poistettava != "- Valitse ennuste -":
            if st.button("Poista valittu ennuste", key="poista_ennuste"):
                st.session_state.asiakkaat_ennuste = [a for a in st.session_state.asiakkaat_ennuste if a["nimi"] != poistettava]
                save_data(ENNUSTE_FILE, st.session_state.asiakkaat_ennuste)
                st.success(f"Asiakas '{poistettava}' poistettu myyntiennusteesta.")

     # Lomake olemassa olevan ennusteen muokkaamiseksi

    st.subheader("Muokkaa olemassa olevaa ennustetta")

    if st.session_state.asiakkaat_ennuste:
        # Rakennetaan valintalistan vaihtoehdot: ensin tyhjä, sitten asiakkaat
        valintaoptiot = ["- Valitse ennuste -"] + [
            f"{a['nimi']} (tuote {a['tuote']})"
            for a in st.session_state.asiakkaat_ennuste
        ]
        valittu = st.selectbox("Valitse muokattava ennuste", options=valintaoptiot)

        # Tarkistetaan että käyttäjä on tehnyt valinnan
        if valittu != "- Valitse ennuste -":
            # Haetaan valitun asiakkaan indeksi ja tiedot
            valittu_index = valintaoptiot.index(valittu) - 1  # koska ensimmäinen on tyhjä
            valittu_ennuste = st.session_state.asiakkaat_ennuste[valittu_index]

            # Näytetään lomake valitun asiakkaan tietojen muokkaamiseksi
            with st.form("muokkaa_sopimus"):
                nimi = st.text_input("Asiakkaan nimi", value=valittu_ennuste["nimi"])
                tuote = st.text_input("Tuote", value=valittu_ennuste["tuote"])
                a_hinta = st.number_input("Tuotteen/palvelun á-hinta (ilman alv., €)", min_value=0.0, step=1.0, format="%.2f", value=valittu_ennuste["a_hinta"])
                maara = st.number_input("Myyntimäärä tilikautena (kpl)", min_value=1, step=1, value=valittu_ennuste["maara"])
                sijainti = st.text_input("Ennusteen sijainti", value=valittu_ennuste["sijainti"])    
                aktiivinen = st.checkbox("Aktiivinen", value=True)
                tallenna = st.form_submit_button("Tallenna muutokset")
            
            
            if lisaus and nimi:
                kokonaisarvo = a_hinta * maara
                uusi_asiakas = {
                    "nimi": nimi,
                    "tuote": tuote,
                    "a_hinta": a_hinta,
                    "maara": maara,
	            "sijainti": sijainti,		
                    "kokonaisarvo": kokonaisarvo,
                    "aktiivinen": aktiivinen
                    
            }
            save_data(ENNUSTE_FILE, st.session_state.asiakkaat_sopimus)
            st.success(f"Ennuste '{nimi}' (tuote {a['tuote']}) päivitetty onnistuneesti.")

    # Summa
    total_ennuste = sum(a["kokonaisarvo"] for a in st.session_state.asiakkaat_ennuste if a.get("aktiivinen", True))
    st.write(f"<h3>Aktiivisten ennustettujen myyntien arvo yhteensä: {total_ennuste:.2f} €</h3>", unsafe_allow_html=True)
    st.write(f"<h3 style='color:#4EA72E;'> Kokonaisarvo (sopimukset + myyntiennuste): {total_sopimus + total_ennuste:.2f} €</h3>", unsafe_allow_html=True)

with tab3:

    st.write("Täytä yrityskulut (ilman ALV:tä) syöttämällä á-hinta ja kappalemäärä kullekin valmiiksi nimetylle kululle. Voit myös lisätä puuttuvan kulun.")

    vakio_kulut = [
        "Kirjanpito",
        "Tili- ja korttimaksut",
        "Lisenssimaksut(microsoft/google, canva, chatgpt yms.)",
        "Kotisivut",
        "Puhelin- ja nettiliittymä",
        "Tilavuokra",
        "Vakuutukset",
        "Myynti- ja markkinointi",
        "Toimisto- ja työtarvikkeet",
        "Edustusmenot",
        "YEL",
        "Koulutumenot",
        "Sijoitus",
        "Jäsenmaksut",
        "Kulukorvaukset tai autoetu",
        "Osinko",
        "Ennakkoverot",
        "Seuraavalle tilikaudelle siirtyvä kassa",
        "Muut kulut (mikäli kulua ei löydy luettelosta, lisää niiden yhteenlaskettu summa tähän)",
    ]

    if "asiakkaat_palkkaennuste" not in st.session_state:
        st.session_state.asiakkaat_palkkaennuste = []

    with st.form("valmiit_kulut_lomake"):
        kulutiedot = []
        st.markdown("### Liiketoiminnan vuosittaiset kulut")

        for kulunimi in vakio_kulut:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                st.markdown(f"<span style='color:#4EA72E; font-weight: bold'>{kulunimi}</span>", unsafe_allow_html=True)
            with col2:
                a_hinta = st.number_input("á-hinta (€)", min_value=0.0, step=1.0, format="%.2f", key=f"{kulunimi}_hinta")
            with col3:
                maara = st.number_input("kpl/vuodessa", min_value=0, step=1, key=f"{kulunimi}_maara")
            with col4:
                summa = a_hinta * maara
                st.markdown(f"<div style='margin-top: 0.5em; font-weight: bold'>{summa:.2f} €</div>", unsafe_allow_html=True)

            if a_hinta > 0 and maara > 0:
                kulutiedot.append({
                    "kulu": kulunimi,
                    "a_hinta": a_hinta,
                    "maara": maara,
                    "kokonaisarvo": summa
                })

        st.form_submit_button("Tallenna kulut")
        st.session_state.asiakkaat_palkkaennuste = kulutiedot
        save_data(PALKKAENNUSTE_FILE, kulutiedot)
        st.success("Kulut tallennettu onnistuneesti.")

    st.subheader("Tallennetut kulut:")
    if st.session_state.asiakkaat_palkkaennuste:
        for k in st.session_state.asiakkaat_palkkaennuste:
            st.write(f"- {k['kulu']}: {k['a_hinta']:.2f} € × {k['maara']} kpl = {k['kokonaisarvo']:.2f} €")
    else:
        st.info("Ei tallennettuja kuluja.")

# Lasketaan yhteissumma
    kulut_yhteensa = 0.0
    if st.session_state.get("asiakkaat_palkkaennuste"):
        kulut_yhteensa = sum(float(k.get("kokonaisarvo", 0.0)) if isinstance(k, dict) else 0.0
	    for k in st.session_state.asiakkaat_palkkaennuste
    )
    st.markdown(f"<h4>Liiketoiminnan kulut yhteensä: {kulut_yhteensa:.2f} €</h4>", unsafe_allow_html=True)

	# Veroprosentti ja palkkatavoite
    vero_prosentti = st.slider("Arvioitu veroprosentti (%)", min_value=0, max_value=55, value=st.session_state.get("veroprosentti", 25))

# Tavoitepalkka (varmistetaan että merkkijono)
    tavoitepalkka_oletus = st.session_state.get("tavoite_palkka", "2500")
    tavoitepalkka_input = st.text_input("Nettopalkka tavoite (€ / kk)", value=str(tavoitepalkka_oletus))

# Tallennusnappi
    if st.button("Tallenna veroprosentti ja palkkatavoite"):
        try:
            tavoite_float = float(tavoitepalkka_input.replace(",", "."))
            veroprosentti_int = int(vero_prosentti)

            # Tallennetaan merkkijonona, jotta käyttö text_inputissa ei kaadu
            st.session_state["tavoite_palkka"] = str(tavoite_float)
            st.session_state["veroprosentti"] = veroprosentti_int

            save_data(PALKKAENNUSTE_FILE, {"palkkatavoite": tavoite_float, "veroprosentti": veroprosentti_int})
            st.success("Veroprosentti ja palkkatavoite tallennettu.")
        except ValueError:
            st.error("Syötä kelvollinen numero nettopalkkatavoitteeksi.")

    # Palkkalaskelmat
    try:
        tavoitepalkka = float(st.session_state.get("tavoite_palkka", 0))
        vero_prosentti = int(st.session_state.get("veroprosentti", 25))

        kokonaismyynti = total_sopimus / 12
        bruttopalkka = kokonaismyynti - (kulut_yhteensa / 12)
        verot = bruttopalkka * (vero_prosentti / 100) if bruttopalkka > 0 else 0
        nettopalkka = bruttopalkka - verot if bruttopalkka > 0 else 0
        myyntikuilu = total_sopimus - (kulut_yhteensa + tavoitepalkka * 12 / (1 - vero_prosentti / 100))
        
        st.markdown(f"**Nettopalkka-arvio:** {nettopalkka:.2f} € / kk")
        st.markdown(f"**Myyntikuilu (vuositasolla):** {myyntikuilu:.2f} €")
	    
    except ZeroDivisionError:
        st.warning("Veroprosentti ei voi olla 100 %. Tarkista syöte.")
    except Exception as e:
        st.warning(f"Virhe palkkalaskennassa: {e}")

# Tulokset näkyviin
    st.markdown(f"<h4>Liikevaihto kuukaudessa perustuen toteutuneeseen myyntiin: {kokonaismyynti:.2f} €</h4>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:#4EA72E;'>Arvioitu nettopalkka kuukaudessa: {nettopalkka:.2f} €</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:red;'>Myyntikuilu vuodessa: {myyntikuilu:.2f} €</h2>", unsafe_allow_html=True)
    #st.markdown(f"<h4>Arvioitu bruttopalkka kuukaudessa: {bruttopalkka:.2f} €</h4>", unsafe_allow_html=True)
with tab_summary:
    st.header("Yhteenveto keskeisistä luvuista")

    st.markdown(f"""
    <div style="
        border: 3px solid #4EA72E; 
        padding: 15px; 
        border-radius: 10px;
        background-color: #F0F8F5;  /* halutessa vaalea taustaväri        
	width: 1000;
        white-space: nowrap;
        overflow-x: auto; */">
        <h3 style='color:#4EA72E;'>Sopimusten kokonaisarvo yhteensä: {total_sopimus:.2f} €</h3>
        <h3 style='color:#4EA72E;'>Myyntiennusteen kokonaisarvo yhteensä: {total_ennuste:.2f} €</h3>
        <h3 style='color:#4EA72E;'>Liiketoiminnan kulut yhteensä: {kulut_yhteensa:.2f} €</h3>
        <h3 style='color:#4EA72E;'>Arvioitu nettopalkka kuukaudessa: {nettopalkka:.2f} €</h3>
	<h3 style='color:#D94D4D;'>Myyntikuilu (vuositasolla): {myyntikuilu:.2f} €</h3>
        # Lisää tämä tarvittessa: <h3 style='color:#4EA72E;'>Kokonaisarvo (sopimukset + myyntiennuste): {total_sopimus + total_ennuste:.2f} €</h3>

</div>
""", unsafe_allow_html=True)
