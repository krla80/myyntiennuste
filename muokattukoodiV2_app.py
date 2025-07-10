# data_access.py
from typing import Any
import os, json

def load_json(file_path: str, default: Any = None) -> Any:
    """Lataa JSON-data tiedostosta. Jos tiedostoa ei ole, palauttaa default-arvon."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else []


def save_json(file_path: str, data: Any) -> None:
    """Tallenna data JSON-muodossa tiedostoon."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# calculations.py
from datetime import date, datetime
from typing import Any, Dict, List

def sum_sopimukset(sopimukset: List[Dict[str, Any]]) -> float:
    """Laskee voimassaolevien sopimusten kokonaisarvon."""
    total = 0.0
    for a in sopimukset:
        try:
            loppu = datetime.fromisoformat(a.get('sopimus', '')).date()
            if loppu >= date.today():
                total += a.get('kokonaisarvo', 0)
        except Exception:
            continue
    return total


def sum_kulut(kulut: List[Dict[str, Any]]) -> float:
    """Laskee kululistan vuosikulut yhteen."""
    return sum(item.get('kokonaisarvo', 0) for item in kulut)


def laske_palkka_metrics(total_sopimukset: float, kulut: float, vero_pct: int, tavoite_netto: float) -> Dict[str, float]:
    """Laskee kuukausittaiset myynti-, brutto-, netto- ja kuiluluvut."""
    kuukausi_myynnit = total_sopimukset / 12
    brutto = kuukausi_myynnit - (kulut / 12)
    verot = max(brutto, 0) * (vero_pct / 100)
    netto = max(brutto, 0) - verot
    myyntikuilu = total_sopimukset - (kulut + tavoite_netto * 12 / (1 - vero_pct / 100))
    return {
        'kuukausi_myynnit': kuukausi_myynnit,
        'brutto': brutto,
        'netto': netto,
        'verot': verot,
        'myyntikuilu': myyntikuilu,
    }


# texts.py
PAGE_TITLE = "Myyntiennuste ja sopimusten hallinta"
TAB1       = "Kirjaa sopimukset"
TAB2       = "Kulut & palkkatavoite"
TAB3       = "Myyntiennusteet"
TAB4       = "Yhteenveto"

SOPIMUS_HEADER    = "Kirjaa sopimukset ja sopimusten hallinta"
SOPIMUS_INTRO     = (
    """
Syötä asiakkaat, joiden kanssa sinulla on jo sopimus.  
Voit antaa jokaiselle asiakkaalle oman hinnan ja kappalemäärän tilikautena.  
Kirjaa hinnat ilman ALV:a.
"""
)
SOPIMUS_WARNINGS  = (
    """
<span style='color:red; font-style: italic;'>
1) Jos sopimus on päättynyt, näkyy se listassa punaisella – poista tai uusi sopimus.  
2) Laskuri laskee mukaan vain voimassaolevat sopimukset.
</span>
"""
)

KULUT_HEADER      = "Tunne yrityksesi kulut ja aseta palkkatavoite"
KULUT_INTRO       = (
    """
Syötä yrityksen vuosittaiset kulut (ilman ALV:a).  
Voit lisätä 'Muut kulut' -rivin, jos jotain ei löydy listasta.
"""
)

ENNUSTE_HEADER    = "Aseta myyntiennusteet"
ENNUSTE_INTRO     = (
    """
Ennusta tilikauden lisämyynti:  
kirjaa asiakas, tuote, á-hinta ja kappalemäärä.  
Merkitse ennuste 'aktiiviseksi', jos haluat sen mukaan laskettaessa.
"""
)

YHTEENVETO_HEADER = "Yhteenveto keskeisistä luvuista"
YHTEENVETO_INTRO  = (
    """
Tässä näet yhteenvedon:  
- Sopimusten kokonaisarvo  
- Ennusteiden kokonaisarvo  
- Kulut  
- Arvioitu nettopalkka kuukaudessa
"""
)


# ui.py
import streamlit as st
from data_access import load_json, save_json
from calculations import sum_sopimukset, sum_kulut, laske_palkka_metrics
from datetime import datetime
import texts

SOPIMUS_FILE = 'asiakkaat_sopimus.json'
ENNUS_FILE   = 'asiakkaat_ennuste.json'
PALKKA_FILE  = 'asiakkaat_palkkaennuste.json'


def render_sopimus_tab():
    st.header(texts.TAB1)
    st.markdown(texts.SOPIMUS_INTRO)
    st.markdown(texts.SOPIMUS_WARNINGS, unsafe_allow_html=True)
    sopimukset = load_json(SOPIMUS_FILE, default=[])
    total = sum_sopimukset(sopimukset)
    st.markdown(f"**Jo tehtyjen sopimusten arvo yhteensä: {total:.2f} €**", unsafe_allow_html=True)
    # Loput lomakelogiikat...


def render_kulut_tab():
    st.header(texts.TAB2)
    st.markdown(texts.KULUT_INTRO)
    raw = load_json(PALKKA_FILE, default={'kulut': [], 'palkkatavoite': 0.0, 'veroprosentti': 25})
    kulut = raw.get('kulut', [])
    total_k = sum_kulut(kulut)
    st.markdown(f"**Liiketoiminnan kulut yhteensä: {total_k:.2f} €**", unsafe_allow_html=True)

    # Lisää uusi kulu
    st.subheader("Lisää kulu")
    with st.form("uusi_kulu_form"):
        nimi = st.text_input("Kulun nimi")
        a_h = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f")
        maara = st.number_input("kpl/vuodessa", min_value=0, step=1)
        lisa = st.form_submit_button("Lisää kulu")
    if lisa and nimi:
        kulut.append({'kulu': nimi, 'a_hinta': a_h, 'maara': maara, 'kokonaisarvo': a_h * maara})
        raw['kulut'] = kulut
        save_json(PALKKA_FILE, raw)
        st.success("Kulu lisätty.")
        st.experimental_rerun()

    # Muokkaa ja poista kulu
    st.subheader("Muokkaa / poista kulu")
    if kulut:
        opts = ["- Valitse kulu -"] + [f"{k['kulu']} ({k['a_hinta']:.2f}€×{k['maara']})" for k in kulut]
        sel = st.selectbox("Valitse kulu", opts)
        if sel != "- Valitse kulu -":
            idx = opts.index(sel) - 1
            item = kulut[idx]
            with st.form("muokkaa_kulu_form"):
                nimi_m = st.text_input("Kulun nimi", value=item['kulu'])
                a_h_m = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f", value=item['a_hinta'])
                m_m = st.number_input("kpl/vuodessa", min_value=0, step=1, value=item['maara'])
                save_b = st.form_submit_button("Tallenna muutokset")
                del_b = st.form_submit_button("Poista kulu")
            if save_b:
                kulut[idx] = {'kulu': nimi_m, 'a_hinta': a_h_m, 'maara': m_m, 'kokonaisarvo': a_h_m * m_m}
                raw['kulut'] = kulut
                save_json(PALKKA_FILE, raw)
                st.success("Kulu päivitetty.")
                st.experimental_rerun()
            if del_b:
                kulut.pop(idx)
                raw['kulut'] = kulut
                save_json(PALKKA_FILE, raw)
                st.success("Kulu poistettu.")
                st.experimental_rerun()


def render_ennuste_tab():
    st.header(texts.TAB3)
    st.markdown(texts.ENNUSTE_INTRO)
    ennuste = load_json(ENNUS_FILE, default=[])
    total_enn = sum(a.get('kokonaisarvo', 0) for a in ennuste if a.get('aktiivinen', True))
    st.markdown(f"**Aktiiviset ennustetut lisämyynnit yhteensä: {total_enn:.2f} €**", unsafe_allow_html=True)

    # Lisää uusi ennuste
    st.subheader("Lisää ennuste")
    with st.form("uusi_ennuste_form"):
        nimi = st.text_input("Asiakkaan nimi")
        tuote = st.text_input("Tuote")
        a_h = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f")
        maara = st.number_input("kpl/vuodessa", min_value=1, step=1)
        sij = st.text_input("Sijainti")
        akt = st.checkbox("Aktiivinen", value=True)
        lisa = st.form_submit_button("Lisää ennuste")
    if lisa and nimi:
        ennuste.append({'nimi': nimi, 'tuote': tuote, 'a_hinta': a_h, 'maara': maara, 'sijainti': sij, 'kokonaisarvo': a_h * maara, 'aktiivinen': akt})
        save_json(ENNUS_FILE, ennuste)
        st.success("Ennuste lisätty.")
        st.experimental_rerun()

    # Muokkaa ja poista ennuste
    st.subheader("Muokkaa / poista ennuste")
    if ennuste:
        opts = ["- Valitse ennuste -"] + [f"{e['nimi']} ({e['tuote']})" for e in ennuste]
        sel = st.selectbox("Valitse ennuste", opts)
        if sel != "- Valitse ennuste -":
            idx = opts.index(sel) - 1
            orig = ennuste[idx]
            with st.form("muokkaa_ennuste_form"):
                nimi_m = st.text_input("Asiakkaan nimi", value=orig['nimi'])
                tuote_m = st.text_input("Tuote", value=orig['tuote'])
                a_h_m = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f", value=orig['a_hinta'])
                m_m = st.number_input("kpl/vuodessa", min_value=1, step=1, value=orig['maara'])
                sij_m = st.text_input("Sijainti", value=orig['sijainti'])
                akt_m = st.checkbox("Aktiivinen", value=orig.get('aktiivinen', True))
                save_b = st.form_submit_button("Tallenna muutokset")
                del_b = st.form_submit_button("Poista ennuste")
            if save_b:
                ennuste[idx] = {'nimi': nimi_m, 'tuote': tuote_m, 'a_hinta': a_h_m, 'maara': m_m, 'sijainti': sij_m, 'kokonaisarvo': a_h_m * m_m, 'aktiivinen': akt_m}
                save_json(ENNUS_FILE, ennuste)
                st.success("Ennuste päivitetty.")
                st.experimental_rerun()
            if del_b:
                ennuste.pop(idx)
                save_json(ENNUS_FILE, ennuste)
                st.success("Ennuste poistettu.")
                st.experimental_rerun()

# app.py
import streamlit as st
from ui import render_sopimus_tab, render_kulut_tab, render_ennuste_tab, render_summary_tab
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
