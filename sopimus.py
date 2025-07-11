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