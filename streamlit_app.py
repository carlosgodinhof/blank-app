import streamlit as st
from datetime import date, time, datetime
import uuid
import pandas as pd
from data_manager import load_events, save_events, load_polls, save_polls

st.set_page_config(
    page_title="Nas Ideias - Gestão de Eventos & Votações",
    page_icon="🏃",
    layout="wide"
)

# Custom header
st.title("🏃 Nas Ideias")
st.caption("Painel de Gestão de Eventos Semanais, Treinos e Votações")

# Carregar dados
events = load_events()
polls = load_polls()

# Separador em abas principais
tab_events, tab_polls = st.tabs(["📅 Eventos & Treinos", "🗳️ Votações"])

# ==========================================
# ABA 1: EVENTOS & TREINOS
# ==========================================
with tab_events:
    col_list, col_form = st.columns([1.6, 1.1], gap="large")

    with col_list:
        st.subheader("📋 Calendário & Lista de Treinos")

        # Filtros rápidos
        filter_type = st.selectbox(
            "Filtrar por tipo:",
            ["Todos", "Treino Semanal", "Treino Longo", "Prova / Competição", "Convívio"],
            key="filter_type"
        )

        filtered_events = events
        if filter_type != "Todos":
            filtered_events = [e for e in events if e.get("type") == filter_type]

        # Ordenar por data
        filtered_events = sorted(filtered_events, key=lambda x: (x.get("date", ""), x.get("time", "")))

        if not filtered_events:
            st.info("Nenhum evento ou treino encontrado.")
        else:
            for ev in filtered_events:
                with st.container(border=True):
                    header_col1, header_col2 = st.columns([3, 1])
                    with header_col1:
                        st.markdown(f"### {ev.get('title', 'Sem título')}")
                        badge_color = "blue"
                        if ev.get("type") == "Treino Longo":
                            badge_color = "orange"
                        elif ev.get("type") == "Prova / Competição":
                            badge_color = "red"
                        elif ev.get("type") == "Convívio":
                            badge_color = "green"
                        st.caption(f":{badge_color}[**{ev.get('type', 'Evento')}**] | 📅 **{ev.get('date')}** às **{ev.get('time')}**")
                    with header_col2:
                        # Ações rápidas
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("✏️", key=f"edit_btn_{ev['id']}", help="Editar evento"):
                                st.session_state["editing_event_id"] = ev["id"]
                                st.rerun()
                        with col_btn2:
                            if st.button("🗑️", key=f"del_btn_{ev['id']}", help="Apagar evento"):
                                events = [e for e in events if e["id"] != ev["id"]]
                                save_events(events)
                                if st.session_state.get("editing_event_id") == ev["id"]:
                                    st.session_state.pop("editing_event_id", None)
                                st.success("Evento removido com sucesso!")
                                st.rerun()

                    details = []
                    if ev.get("location"):
                        details.append(f"📍 **Local:** {ev['location']}")
                    if ev.get("distance"):
                        details.append(f"📏 **Distância:** {ev['distance']}")
                    if details:
                        st.markdown(" • ".join(details))

                    if ev.get("description"):
                        st.markdown(f"_{ev['description']}_")

    with col_form:
        # Modo de Edição vs Modo de Adição
        editing_id = st.session_state.get("editing_event_id")
        event_to_edit = next((e for e in events if e["id"] == editing_id), None) if editing_id else None

        if event_to_edit:
            st.subheader("✏️ Editar Treino / Evento")
            st.info(f"A editar: **{event_to_edit['title']}**")
        else:
            st.subheader("➕ Novo Treino ou Evento")

        with st.form("event_form", clear_on_submit=False):
            title = st.text_input("Título / Nome:", value=event_to_edit["title"] if event_to_edit else "")
            
            types_list = ["Treino Semanal", "Treino Longo", "Prova / Competição", "Convívio"]
            current_type_idx = types_list.index(event_to_edit["type"]) if event_to_edit and event_to_edit.get("type") in types_list else 0
            event_type = st.selectbox("Tipo de Atividade:", types_list, index=current_type_idx)

            # Data e Hora
            try:
                def_date = datetime.strptime(event_to_edit["date"], "%Y-%m-%d").date() if event_to_edit else date.today()
            except Exception:
                def_date = date.today()

            try:
                def_time = datetime.strptime(event_to_edit["time"], "%H:%M").time() if event_to_edit else time(19, 30)
            except Exception:
                def_time = time(19, 30)

            c_date, c_time = st.columns(2)
            with c_date:
                ev_date = st.date_input("Data:", value=def_date)
            with c_time:
                ev_time = st.time_input("Hora:", value=def_time)

            location = st.text_input("Local de Encontro:", value=event_to_edit.get("location", "") if event_to_edit else "")
            distance = st.text_input("Distância Prevista (ex: 10 km):", value=event_to_edit.get("distance", "") if event_to_edit else "")
            description = st.text_area("Observações / Notas do Treino:", value=event_to_edit.get("description", "") if event_to_edit else "")

            btn_label = "💾 Atualizar Evento" if event_to_edit else "➕ Adicionar Evento"
            submit_btn = st.form_submit_button(btn_label, use_container_width=True, type="primary")

            if submit_btn:
                if not title.strip():
                    st.error("Por favor, introduza o título do evento.")
                else:
                    new_event_data = {
                        "id": event_to_edit["id"] if event_to_edit else str(uuid.uuid4())[:8],
                        "title": title.strip(),
                        "type": event_type,
                        "date": ev_date.strftime("%Y-%m-%d"),
                        "time": ev_time.strftime("%H:%M"),
                        "location": location.strip(),
                        "distance": distance.strip(),
                        "description": description.strip()
                    }

                    if event_to_edit:
                        # Atualizar evento existente
                        events = [new_event_data if e["id"] == event_to_edit["id"] else e for e in events]
                        save_events(events)
                        st.session_state.pop("editing_event_id", None)
                        st.success("Evento atualizado com sucesso!")
                    else:
                        events.append(new_event_data)
                        save_events(events)
                        st.success("Evento adicionado com sucesso!")
                    st.rerun()

        if event_to_edit:
            if st.button("❌ Cancelar Edição", use_container_width=True):
                st.session_state.pop("editing_event_id", None)
                st.rerun()

# ==========================================
# ABA 2: VOTAÇÕES
# ==========================================
with tab_polls:
    col_polls, col_new_poll = st.columns([1.6, 1.1], gap="large")

    with col_polls:
        st.subheader("🗳️ Sondagens & Votações Ativas")

        if not polls:
            st.info("Nenhuma votação criada até ao momento.")
        else:
            for p_idx, poll in enumerate(polls):
                with st.container(border=True):
                    col_p_title, col_p_del = st.columns([3, 1])
                    with col_p_title:
                        st.markdown(f"#### ❓ {poll.get('question')}")
                        st.caption(f"Criada a: {poll.get('created_at', 'N/D')}")
                    with col_p_del:
                        if st.button("🗑️ Remover", key=f"del_poll_{poll['id']}"):
                            polls = [p for p in polls if p["id"] != poll["id"]]
                            save_polls(polls)
                            st.success("Votação eliminada!")
                            st.rerun()

                    # Opções de voto
                    options = poll.get("options", [])
                    total_votes = sum(opt.get("votes", 0) for opt in options)

                    st.markdown("**Registar o seu voto:**")
                    selected_opt_idx = st.radio(
                        "Selecione uma opção:",
                        options=range(len(options)),
                        format_func=lambda i: options[i]["text"],
                        key=f"radio_poll_{poll['id']}",
                        label_visibility="collapsed"
                    )

                    if st.button("🗳️ Votar", key=f"btn_vote_{poll['id']}", type="primary"):
                        options[selected_opt_idx]["votes"] = options[selected_opt_idx].get("votes", 0) + 1
                        save_polls(polls)
                        st.success(f"Voto registado na opção: '{options[selected_opt_idx]['text']}'!")
                        st.rerun()

                    st.divider()
                    st.markdown(f"**Resultados Parciais ({total_votes} votos no total):**")
                    
                    if options and total_votes > 0:
                        df_results = pd.DataFrame([
                            {"Opção": opt["text"], "Votos": opt.get("votes", 0)}
                            for opt in options
                        ])
                        st.bar_chart(df_results.set_index("Opção"))
                    elif options:
                        for opt in options:
                            st.write(f"- **{opt['text']}**: 0 votos")

    with col_new_poll:
        st.subheader("➕ Criar Nova Votação")
        with st.form("new_poll_form", clear_on_submit=True):
            poll_question = st.text_input("Pergunta da Votação:", placeholder="ex: Onde fazemos o treino longo de Domingo?")
            st.caption("Insira as opções disponíveis (uma por linha):")
            poll_options_raw = st.text_area(
                "Opções:",
                placeholder="Marginal de Gaia\nParque da Cidade\nFoz do Douro\nEstádio do Dragão",
                height=130
            )

            create_poll_btn = st.form_submit_button("🚀 Lançar Votação", use_container_width=True, type="primary")

            if create_poll_btn:
                clean_question = poll_question.strip()
                opts_list = [line.strip() for line in poll_options_raw.splitlines() if line.strip()]

                if not clean_question:
                    st.error("Por favor, introduza a pergunta da votação.")
                elif len(opts_list) < 2:
                    st.error("Insira pelo menos 2 opções para votação.")
                else:
                    new_poll_obj = {
                        "id": str(uuid.uuid4())[:8],
                        "question": clean_question,
                        "options": [{"text": opt, "votes": 0} for opt in opts_list],
                        "active": True,
                        "created_at": date.today().strftime("%Y-%m-%d")
                    }
                    polls.append(new_poll_obj)
                    save_polls(polls)
                    st.success("Votação criada com sucesso!")
                    st.rerun()
