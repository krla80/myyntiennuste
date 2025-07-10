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
    st.markdown(f"<h3 style='color:green;'>Jo tehtyjen sopimusten arvo yhteensä: {total:.2f} €</h3>", unsafe_allow_html=True)

    # Lisää uusi sopimus
    st.subheader("Lisää sopimus")
    with st.form("uusi_sopimus_form"):
        nimi = st.text_input("Asiakkaan nimi")
        tuote = st.text_input("Tuote / sopimustunnus")
        sop_pvm = st.date_input("Sopimuksen päättymispäivä")
        sij = st.text_input("Sopimuksen sijainti")
        a_h = st.number_input("á-hinta (ilman ALV, €)", min_value=0.0, format="%.2f")
        maara = st.number_input("Määrä (kpl)", min_value=1, step=1)
        lisa = st.form_submit_button("Lisää sopimus")
    if lisa and nimi:
        uusi = {
            'nimi': nimi, 'tuote': tuote, 'sopimus': sop_pvm.isoformat(),
            'sijainti': sij, 'a_hinta': a_h, 'maara': maara,
            'kokonaisarvo': a_h * maara
        }
        sopimukset.append(uusi)
        save_json(SOPIMUS_FILE, sopimukset)
        st.success("Sopimus lisätty.")
        st.rerun()  # type: ignore

    # Näytä kaikki sopimukset listana
    st.subheader("Tallennetut sopimukset")
    if sopimukset:
        for s in sopimukset:
            st.markdown(
                f"- **{s['nimi']}**: {s['tuote']} – {s['a_hinta']:.2f} € × {s['maara']} kpl = {s['kokonaisarvo']:.2f} € "
                f"(päättyy {s['sopimus']}, sijainti: {s['sijainti']})"
            )
    else:
        st.info("Ei tallennettuja sopimuksia.")

    # Poista / muokkaa sopimus
    st.subheader("Muokkaa / poista sopimus")
    if sopimukset:
        opts = ["- Valitse sopimus -"] + [f"{s['nimi']} ({s['tuote']})" for s in sopimukset]
        sel = st.selectbox("Valitse sopimus", opts)
        if sel != opts[0]:
            idx = opts.index(sel) - 1
            orig = sopimukset[idx]
            with st.form("muokkaa_sopimus_form"):
                nimi_m = st.text_input("Asiakkaan nimi", value=orig['nimi'])
                tuote_m = st.text_input("Tuote", value=orig['tuote'])
                pvm_m = st.date_input("Päättymispäivä", value=datetime.fromisoformat(orig['sopimus']).date())
                sij_m = st.text_input("Sijainti", value=orig['sijainti'])
                a_h_m = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f", value=orig['a_hinta'])
                m_m = st.number_input("Määrä (kpl)", min_value=1, step=1, value=orig['maara'])
                save_b = st.form_submit_button("Tallenna muutokset")
                del_b = st.form_submit_button("Poista")
            if save_b:
                sopimukset[idx] = {
                    'nimi': nimi_m, 'tuote': tuote_m, 'sopimus': pvm_m.isoformat(),
                    'sijainti': sij_m, 'a_hinta': a_h_m,
                    'maara': m_m, 'kokonaisarvo': a_h_m * m_m
                }
                save_json(SOPIMUS_FILE, sopimukset)
                st.success("Sopimus päivitetty.")
                st.rerun()  # type: ignore
            if del_b:
                sopimukset.pop(idx)
                save_json(SOPIMUS_FILE, sopimukset)
                st.success("Sopimus poistettu.")
                st.rerun()  # type: ignore
    st.markdown(f"<h3 style='color:green;'>Jo tehtyjen sopimusten arvo yhteensä: {total:.2f} €</h3>", unsafe_allow_html=True)

def render_kulut_tab():
    st.header(texts.TAB2)
    st.markdown(texts.KULUT_INTRO)

    # Vakio-kulut
    vakio_kulut = [
        "Kirjanpito", "Tili- ja korttimaksut", "Lisenssikulut (microsoft/google, canva, chat gpt, yms.)",
        "Kotisivut", "Toimisto- ja työtarvikkeet", "Puhelin- ja nettiliittymä", "Tilavuokra",
        "Vakuutukset", "Myynti- ja markkinointi", "Verot", "Edustusmenot", "YEL",
        "Koulutus", "Sijoitus", "Jäsenmaksut", "Kulukorvaukset", "Autoetu", "Osinko",
        "Ennakkoverot", "Siirto seuraavalle tilikaudelle"
    ]
    # Vakio- ja omien kulujen syöttökentät lomakkeessa
    raw = load_json(PALKKA_FILE, default={'kulut': [], 'veroprosentti': 25, 'palkkatavoite': 0.0})
    if isinstance(raw, list):
        raw = {'kulut': raw, 'veroprosentti': 25, 'palkkatavoite': 0.0}
    tallennetut = raw['kulut']

    # Lomake vakio- ja omille kuluille sekä verot ja tavoite
    with st.form("kulut_lomake"):
        st.markdown("#### Syötä tilikauden kulut")
        uusi_kulut = []
        # Käydään läpi vakio-kulut
        for nimi in vakio_kulut:
            olet_h = next((k['a_hinta'] for k in tallennetut if k['kulu'] == nimi), 0.0)
            olet_m = next((k['maara'] for k in tallennetut if k['kulu'] == nimi), 0)
            col1, col2, col3 = st.columns([3,1,1])
            with col1:
                st.write(nimi)
            with col2:
                h = st.number_input(f"á-hinta (€)", min_value=0.0, format="%.2f", value=olet_h, key=f"vak_h_{nimi}")
            with col3:
                m = st.number_input(f"kpl/tilikausi (vuosi)", min_value=0, step=1, value=olet_m, key=f"vak_m_{nimi}")
            if h > 0 and m > 0:
                uusi_kulut.append({'kulu': nimi, 'a_hinta': h, 'maara': m, 'kokonaisarvo': h*m})

        # Käydään läpi käyttäjän aiemmin lisäämät omat kulut, joita ei ole vakio-kuluissa
        omat_kulut = [k for k in tallennetut if k['kulu'] not in vakio_kulut]
        if omat_kulut:
            st.markdown("#### Omat lisätyt kulut")
            for idx, k in enumerate(omat_kulut):
                col1, col2, col3 = st.columns([3,1,1])
                with col1:
                    oma_nimi = st.text_input("Kulun nimi", value=k['kulu'], key=f"oma_nimi_{idx}")
                with col2:
                    oma_hinta = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f", value=k['a_hinta'], key=f"oma_hinta_{idx}")
                with col3:
                    oma_maara = st.number_input("kpl/tilikausi (vuosi)", min_value=1, step=1, value=k['maara'], key=f"oma_maara_{idx}")
                if oma_nimi and oma_hinta > 0 and oma_maara > 0:
                    uusi_kulut.append({'kulu': oma_nimi, 'a_hinta': oma_hinta, 'maara': oma_maara, 'kokonaisarvo': oma_hinta*oma_maara})


        st.markdown("#### Lisää listasta puuttuva kulu")
        oma_n = st.text_input("Kulun nimi", key="oma_nimi_uusi")
        oma_h = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f", key="oma_hinta_uusi")
        oma_m = st.number_input("kpl/tilikausi (vuosi)", min_value=1, step=1, key="oma_maara_uusi")
        if oma_n and oma_h > 0 and oma_m > 0:
            uusi_kulut.append({'kulu': oma_n, 'a_hinta': oma_h, 'maara': oma_m, 'kokonaisarvo': oma_h*oma_m})

        # Tallenna lomakkeen tiedot
        save = st.form_submit_button("Tallenna lisätty kulu")
        if save:
            if not uusi_kulut:
                st.error("Lisää vähintään yksi kulu.")
            else:
                # Tallenna kulut ja veroprosentti
                save_json(PALKKA_FILE, {
                    'kulut': uusi_kulut,
                    'veroprosentti': raw['veroprosentti'],
                    'palkkatavoite': raw.get('palkkatavoite', 0.0)
                })
                st.success("Kulut tallennettu.")
                # Yritä uudelleenladata sivu, jos funktio on saatavilla
                try:
                    st.rerun()
                except Exception:
                    pass
                    st.markdown("---")

        st.markdown("### Kaikki lisätyt kulut")
        if uusi_kulut:
            for k in uusi_kulut:
                st.write(f"- {k['kulu']}: {k['a_hinta']:.2f} € × {k['maara']} kpl = {k['kokonaisarvo']:.2f} €")
        else:
            st.info("Ei lisättyjä kuluja.")
        # Muokkaa/Poista tallennettuja kuluja
 
        # Muokkaa / poista kulu
    # Muokkaa / poista kulu - nyt osana samaa lomaketta
    st.subheader("Muokkaa / poista kulu")
    if uusi_kulut:
        opts = ["- Valitse kulu -"] + [f"{k['kulu']} ({k['a_hinta']:.2f}€×{k['maara']})" for k in uusi_kulut]
        sel_k = st.selectbox("Valitse muokattava tai poistettava kulu", opts, key="sel_kulu")
        if sel_k != opts[0]:
            idx_k = opts.index(sel_k) - 1
            orig_k = uusi_kulut[idx_k]
            k_nimi = st.text_input("Kulun nimi", value=orig_k["kulu"], key="edit_kulu_nimi")
            k_ah   = st.number_input("Á-hinta (€)", min_value=0.0, format="%.2f", value=orig_k["a_hinta"], key="edit_kulu_ah")
            k_m    = st.number_input("kpl/tilikausi (vuosi)", min_value=1, step=1, value=orig_k["maara"], key="edit_kulu_m")
            save_k = st.form_submit_button("Tallenna muutokset")
            del_k  = st.form_submit_button("Poista kulu")
            if save_k:
                uusi_kulut[idx_k] = {
                    "kulu": k_nimi,
                    "a_hinta": k_ah,
                    "maara": k_m,
                    "kokonaisarvo": k_ah * k_m
                }
                save_json(PALKKA_FILE, {
                    "kulut": uusi_kulut,
                    "veroprosentti": raw["veroprosentti"],
                    "palkkatavoite": raw.get("palkkatavoite", 0.0)
                })
                st.success("Kulu päivitetty.")
                st.rerun()
            if del_k:
                uusi_kulut.pop(idx_k)
                save_json(PALKKA_FILE, {
                    "kulut": uusi_kulut,
                    "veroprosentti": raw["veroprosentti"],
                    "palkkatavoite": raw.get("palkkatavoite", 0.0)
                })
                st.success("Kulu poistettu.")
                st.rerun()

    # Näytetään tallennetut kulut listana
    raw_display = load_json(PALKKA_FILE, default={'kulut': []})
    if isinstance(raw_display, list):
        raw_display = {'kulut': raw_display}
    kulut_list = raw_display.get('kulut', [])
    total_kulut = sum(k['kokonaisarvo'] for k in kulut_list) if kulut_list else 0.0
    st.markdown(f"### Tallennetut kulut yhteensä:{total_kulut:.2f} €")
    for k in kulut_list:
        st.write(f"- {k['kulu']}: {k['a_hinta']:.2f} € × {k['maara']} kpl = {k['kokonaisarvo']:.2f} €")
    

        st.markdown("---")
        st.markdown("### Verotus ja palkkatavoite")
        with st.form("vero_palkka_form"):
            verop = st.slider("Arvioitu veroprosentti (%)", min_value=0, max_value=55, value=raw.get('veroprosentti', 25))
            tavoitestr = st.text_input("Nettopalkkatavoite (€ / kk)", value=str(raw.get('palkkatavoite', 0.0)), key="tavoite")
            st.markdown("**Huom!** Nettopalkkatavoite on palkka, jonka haluat jäävän sinulle verojen jälkeen. Veroprosentti vaikuttaa laskentaan.")
            save = st.form_submit_button("Tallenna")

        if save:
            try:
                tavoite = float(tavoitestr.replace(',', '.'))
            except ValueError:
                st.error("Syötä kelvollinen nettopalkkatavoite")
                return
            save_json(PALKKA_FILE, {'kulut': uusi_kulut, 'veroprosentti': verop, 'palkkatavoite': tavoite})
            st.success("Kulut ja palkkatavoite tallennettu.")
            # Yritä uudelleenladata sivu, jos funktio on saatavilla
            try:
                st.rerun()
            except Exception:
                pass


    # Lasketaan metrics ennen käyttöä
    sopimus_total = sum_sopimukset(load_json(SOPIMUS_FILE, default=[]))
    veroprosentti = raw_display.get('veroprosentti', 25)
    if isinstance(veroprosentti, list):
        veroprosentti = 25
    try:
        veroprosentti = int(veroprosentti)
    except (ValueError, TypeError):
        veroprosentti = 25
    palkkatavoite = raw_display.get('palkkatavoite', 0.0)
    if isinstance(palkkatavoite, list):
        palkkatavoite = 0.0
    try:
        palkkatavoite = float(palkkatavoite)
    except (ValueError, TypeError):
        palkkatavoite = 0.0
    # Always calculate total_kulut, even if kulut_list is empty
    total_kulut = sum(k['kokonaisarvo'] for k in kulut_list) if kulut_list else 0.0
    metrics = laske_palkka_metrics(sopimus_total, total_kulut, veroprosentti, palkkatavoite)

    st.markdown("---")
    st.markdown(f"<h3 style='color:green;'>Arvioitu nettopalkka: {metrics['netto']:.2f} €/ kk</h3>", unsafe_allow_html=True)
    gap = metrics['myyntikuilu']
    if gap < 0:
        st.markdown(f"<h3 style='color:red;'>Tarvitset {abs(gap):.2f} € lisämyyntiä saavuttaaksesi tavoitteen.</h3>", unsafe_allow_html=True)
    else:
        st.markdown("**Hienoa! Olet jo saavuttanut tavoitepalkkasi.**", unsafe_allow_html=True)

def render_ennuste_tab():
    st.header(texts.TAB3)
    st.markdown(texts.ENNUSTE_INTRO)
    ennuste = load_json(ENNUS_FILE, default=[])
    total_enn = sum(a.get('kokonaisarvo', 0) for a in ennuste if a.get('aktiivinen', True))

    # Calculate metrics as in other tabs
    sopimus_total = sum_sopimukset(load_json(SOPIMUS_FILE, default=[]))
    raw_display = load_json(PALKKA_FILE, default={'kulut': []})
    if isinstance(raw_display, list):
        raw_display = {'kulut': raw_display}
    kulut_list = raw_display.get('kulut', [])
    total_kulut = sum(k['kokonaisarvo'] for k in kulut_list) if kulut_list else 0.0
    veroprosentti = raw_display.get('veroprosentti', 25)
    if isinstance(veroprosentti, list):
        veroprosentti = 25
    try:
        veroprosentti = int(veroprosentti)
    except (ValueError, TypeError):
        veroprosentti = 25
    palkkatavoite = raw_display.get('palkkatavoite', 0.0)
    if isinstance(palkkatavoite, list):
        palkkatavoite = 0.0
    try:
        palkkatavoite = float(palkkatavoite)
    except (ValueError, TypeError):
        palkkatavoite = 0.0
    metrics = laske_palkka_metrics(sopimus_total, total_kulut, veroprosentti, palkkatavoite)

    gap = metrics['myyntikuilu']
    if gap < 0:
        st.markdown(f"<h3 style='color:red;'>Tarvitset jo ennustetun lisämyynnin lisäksi {abs(gap+total_enn):.2f} € lisämyyntiä saavuttaaksesi palkkatavoitteesi.</h3>", unsafe_allow_html=True)
    else:
        st.markdown("**Periaatteessa sinun ei tarvitse myydä enempää saavuttaaksesi tavoitepalkkasi.**", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:green;'>Ennustettu lisämyynti tilikaudella: {total_enn:.2f} €</h3>", unsafe_allow_html=True)

    # Lisää ennuste
    st.subheader("Lisää ennuste")
    with st.form("uusi_ennuste_form"):
        e_nimi = st.text_input("Asiakkaan nimi")
        e_tuote = st.text_input("Tuote")
        e_a_h = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f")
        e_m = st.number_input("kpl/vuodessa", min_value=1, step=1)
        e_sij = st.text_input("Sijainti")
        e_akt = st.checkbox("Aktiivinen", value=True)
        e_lisa = st.form_submit_button("Lisää ennuste")
    if e_lisa and e_nimi:
        ennuste.append({'nimi': e_nimi, 'tuote': e_tuote, 'a_hinta': e_a_h, 'maara': e_m, 'sijainti': e_sij, 'kokonaisarvo': e_a_h * e_m, 'aktiivinen': e_akt})
        save_json(ENNUS_FILE, ennuste)
        st.success("Ennuste lisätty.")
        st.experimental_rerun()  # type: ignore

    # Muokkaa / poista ennuste
    st.subheader("Muokkaa / poista ennuste")
    if ennuste:
        opts = ["- Valitse ennuste -"] + [f"{e['nimi']} ({e['tuote']})" for e in ennuste]
        sel = st.selectbox("Valitse ennuste", opts)
        if sel != opts[0]:
            idx = opts.index(sel) - 1
            orig = ennuste[idx]
            with st.form("muokkaa_ennuste_form"):
                nimi_m = st.text_input("Asiakkaan nimi", value=orig['nimi'])
                tuote_m = st.text_input("Tuote", value=orig['tuote'])
                a_h_m = st.number_input("á-hinta (€)", min_value=0.0, format="%.2f", value=orig['a_hinta'])
                m_m = st.number_input("kpl/vuodessa", min_value=1, step=1, value=orig['maara'])
                sij_m = st.text_input("Sijainti", value=orig['sijainti'])
                akt_m = st.checkbox("Aktiivinen", value=orig.get('aktiivinen', True))
                save_b = st.form_submit_button("Tallenna")
                del_b = st.form_submit_button("Poista")
            if save_b:
                ennuste[idx] = {'nimi': nimi_m, 'tuote': tuote_m, 'a_hinta': a_h_m, 'maara': m_m, 'sijainti': sij_m, 'kokonaisarvo': a_h_m * m_m, 'aktiivinen': akt_m}
                save_json(ENNUS_FILE, ennuste)
                st.success("Ennuste päivitetty.")
                st.experimental_rerun()  # type: ignore
            if del_b:
                ennuste.pop(idx)
                save_json(ENNUS_FILE, ennuste)
                st.success("Ennuste poistettu.")
                st.experimental_rerun()  # type: ignore
    st.subheader("Tallennetut ennusteet")
    if ennuste:
        for e in ennuste:
            # Voit muokata ulkoasua haluamallasi tavalla
            st.markdown(
                f"- **{e['nimi']}**: {e['tuote']} – {e['a_hinta']:.2f} € × {e['maara']} kpl = {e['kokonaisarvo']:.2f} € "
                f"{'(aktiivinen)' if e.get('aktiivinen', True) else '(ei aktiivinen)'}"
            )
    else:
        st.info("Ei tallennettuja ennusteita.")

def render_summary_tab():
    st.header(texts.TAB4)
    st.markdown(texts.YHTEENVETO_INTRO)
    sop = sum_sopimukset(load_json(SOPIMUS_FILE, default=[]))

    raw = load_json(PALKKA_FILE, default=[])
    # Jos raw on lista, muunna dictiksi
    if isinstance(raw, list):
        raw = {'kulut': raw, 'palkkatavoite': 0.0, 'veroprosentti': 25}
    kul = sum_kulut(raw.get('kulut', []))
    tavoite = raw.get('palkkatavoite', 0)
    vero = raw.get('veroprosentti', 25)

    metrics = laske_palkka_metrics(sop, kul, vero, tavoite)

    ennuste = load_json(ENNUS_FILE, default=[])
    total_enn = sum(a.get('kokonaisarvo', 0) for a in ennuste if a.get('aktiivinen', True))
    st.markdown(
        """
        <div style='background-color:#d4edda; border-radius:12px; padding:18px; margin-bottom:16px;'>
            <h4 style='color:green;'>Sopimusten ja ennusteiden kokonaisarvo: {total:.2f} €</h4>
            <h4 style='color:green;'>Sopimusten kokonaisarvo: {sop:.2f} €</h4>
            <h4 style='color:green;'>Ennusteiden kokonaisarvo: {enn:.2f} €</h4>
            <h4 style='color:green;'>Liiketoiminnan kulut: {kul:.2f} €</h4>
            <h4 style='color:green;'>Arvioitu nettopalkka kuukaudessa perustuen sovittuihin myynteihin: {netto:.2f} €</h4>
            <h4 style='color:red;'>Tavoitepalkan edellyttämä lisämyynti tilikaudelle: {lisamyynti:.0f} €</h4>
        </div>
        """.format(
            total=sop + total_enn,
            sop=sop,
            enn=total_enn,
            kul=kul,
            netto=metrics['netto'],
            lisamyynti=abs(metrics['myyntikuilu'])
        ),
        unsafe_allow_html=True
    )