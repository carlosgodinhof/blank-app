import streamlit as st
from datetime import date, time, datetime
import uuid
import pandas as pd
from data_manager import load_events, save_events, load_polls, save_polls

# -------------------------------------------------------------
# 1. Configuração da Página
# -------------------------------------------------------------
st.set_page_config(
    page_title="Godinho RUN",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# 2. Esconder Menus Padrão do Streamlit & Estilos Profissionais
# -------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Esconder o menu de 3 pontos superior e rodapé da plataforma */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden; height: 0px;}
    div[data-testid="stDecoration"] {visibility: hidden; height: 0px;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    
    /* Tipografia e espaçamento elegante */
    .hero-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: #F8FAFC;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
    }
    .metric-badge {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 10px 16px;
        text-align: center;
    }
    .metric-val {
        font-size: 1.4rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .metric-lbl {
        font-size: 0.75rem;
        color: #CBD5E1;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .card-badge {
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 6px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. Gestão de Segurança & Acesso Admin
# -------------------------------------------------------------
# Obter PIN configurado via Secrets ou valor padrão
try:
    DEFAULT_ADMIN_PIN = str(st.secrets.get("ADMIN_PIN", "1234"))
except Exception:
    DEFAULT_ADMIN_PIN = "1234"

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Sidebar para Autenticação / Modo Admin
with st.sidebar:
    st.markdown("### 🔐 Acesso à Gestão")
    if not st.session_state["is_admin"]:
        st.caption("Área reservada aos organizadores para criação/edição de treinos e votações.")
        pin_input = st.text_input("PIN de Administrador:", type="password", key="admin_pin_input")
        if st.button("Entrar como Organizador", use_container_width=True, type="primary"):
            if pin_input.strip() == DEFAULT_ADMIN_PIN:
                st.session_state["is_admin"] = True
                st.success("Acesso de Organizador concedido!")
                st.rerun()
            else:
                st.error("PIN incorreto.")
    else:
        st.success("🟢 Modo Organizador Ativo")
        if st.button("Sair da Administração", use_container_width=True):
            st.session_state["is_admin"] = False
            st.session_state.pop("editing_event_id", None)
            st.rerun()
    st.divider()
    st.caption("Godinho RUN • Comunidade de Treinos")

# -------------------------------------------------------------
# 4. Carregamento de Dados
# -------------------------------------------------------------
events = load_events()
polls = load_polls()

# -------------------------------------------------------------
# 5. Topo / Hero Banner
# -------------------------------------------------------------
total_events = len(events)
total_polls = len(polls)
today_str = date.today().strftime("%Y-%m-%d")
upcoming_events = [e for e in events if e.get("date", "") >= today_str]

hero_html = f"""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <div>
            <div class="hero-title">🏃 Godinho RUN</div>
            <div class="hero-subtitle">Plataforma Oficial de Treinos Semanais, Eventos e Decisões de Grupo</div>
        </div>
        <div style="display: flex; gap: 12px;">
            <div class="metric-badge">
                <div class="metric-val">{len(upcoming_events)}</div>
                <div class="metric-lbl">Próximos Treinos</div>
            </div>
            <div class="metric-badge">
                <div class="metric-val">{total_polls}</div>
                <div class="metric-lbl">Votações</div>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

if st.session_state["is_admin"]:
    st.info("🛠️ **Modo Organizador Ativo**: Pode adicionar, editar ou remover eventos e gerir votações.")

# -------------------------------------------------------------
# 6. Abas Principais
# -------------------------------------------------------------
tab_events, tab_polls = st.tabs(["📅 Eventos & Treinos", "🗳️ Votações"])

# =============================================================
# ABA 1: EVENTOS & TREINOS
# =============================================================
with tab_events:
    # Se for admin, dividimos o ecrã para mostrar formulário de gestão
    if st.session_state["is_admin"]:
        col_list, col_form = st.columns([1.5, 1.1], gap="large")
    else:
        col_list = st.container()
        col_form = None

    with col_list:
        sub_col1, sub_col2 = st.columns([2, 1])
        with sub_col1:
            st.subheader("📋 Calendário de Treinos")
        with sub_col2:
            filter_type = st.selectbox(
                "Filtrar:",
                ["Todos", "Treino Semanal", "Treino Longo", "Prova / Competição", "Convívio"],
                key="filter_type_select",
                label_visibility="collapsed"
            )

        filtered_events = events
        if filter_type != "Todos":
            filtered_events = [e for e in events if e.get("type") == filter_type]

        # Ordenar cronologicamente
        filtered_events = sorted(filtered_events, key=lambda x: (x.get("date", ""), x.get("time", "")))

        if not filtered_events:
            st.info("Não existem treinos agendados para este filtro.")
        else:
            for ev in filtered_events:
                with st.container(border=True):
                    head_col, action_col = st.columns([3, 1] if st.session_state["is_admin"] else [1, 0.01])
                    
                    # Definir cores do crachá
                    ev_type = ev.get("type", "Treino Semanal")
                    bg_color, text_color = "#E0F2FE", "#0369A1"
                    if ev_type == "Treino Longo":
                        bg_color, text_color = "#FFEDD5", "#C2410C"
                    elif ev_type == "Prova / Competição":
                        bg_color, text_color = "#FEE2E2", "#B91C1C"
                    elif ev_type == "Convívio":
                        bg_color, text_color = "#DCFCE7", "#15803D"

                    with head_col:
                        st.markdown(
                            f'<span class="card-badge" style="background-color: {bg_color}; color: {text_color};">{ev_type}</span>',
                            unsafe_allow_html=True
                        )
                        st.markdown(f"### {ev.get('title', 'Treino')}")

                    # Ações apenas visíveis para o Administrador
                    if st.session_state["is_admin"]:
                        with action_col:
                            b_edit, b_del = st.columns(2)
                            with b_edit:
                                if st.button("✏️", key=f"edit_ev_{ev['id']}", help="Editar treino"):
                                    st.session_state["editing_event_id"] = ev["id"]
                                    st.rerun()
                            with b_del:
                                if st.button("🗑️", key=f"del_ev_{ev['id']}", help="Eliminar treino"):
                                    events = [e for e in events if e["id"] != ev["id"]]
                                    save_events(events)
                                    if st.session_state.get("editing_event_id") == ev["id"]:
                                        st.session_state.pop("editing_event_id", None)
                                    st.success("Evento removido.")
                                    st.rerun()

                    # Informações do treino em colunas organizadas
                    info_col1, info_col2, info_col3 = st.columns(3)
                    with info_col1:
                        st.markdown(f"📅 **Data & Hora:**\n{ev.get('date')} às {ev.get('time')}")
                    with info_col2:
                        location = ev.get("location") or "A definir"
                        st.markdown(f"📍 **Local de Encontro:**\n{location}")
                    with info_col3:
                        dist = ev.get("distance") or "Livre"
                        st.markdown(f"📏 **Distância Estimada:**\n{dist}")

                    if ev.get("description"):
                        st.divider()
                        st.markdown(f"ℹ️ **Notas:** {ev['description']}")

    # Formulário de Criação/Edição (exibido apenas se Admin)
    if col_form:
        with col_form:
            editing_id = st.session_state.get("editing_event_id")
            event_to_edit = next((e for e in events if e["id"] == editing_id), None) if editing_id else None

            with st.container(border=True):
                if event_to_edit:
                    st.subheader("✏️ Editar Evento")
                    st.caption(f"A modificar: **{event_to_edit['title']}**")
                else:
                    st.subheader("➕ Criar Novo Treino / Evento")

                with st.form("admin_event_form", clear_on_submit=False):
                    title = st.text_input("Nome do Evento / Treino:", value=event_to_edit["title"] if event_to_edit else "")
                    
                    types_list = ["Treino Semanal", "Treino Longo", "Prova / Competição", "Convívio"]
                    type_idx = types_list.index(event_to_edit["type"]) if event_to_edit and event_to_edit.get("type") in types_list else 0
                    selected_type = st.selectbox("Categoria:", types_list, index=type_idx)

                    # Datas
                    try:
                        def_date = datetime.strptime(event_to_edit["date"], "%Y-%m-%d").date() if event_to_edit else date.today()
                    except Exception:
                        def_date = date.today()

                    try:
                        def_time = datetime.strptime(event_to_edit["time"], "%H:%M").time() if event_to_edit else time(19, 30)
                    except Exception:
                        def_time = time(19, 30)

                    c_d, c_t = st.columns(2)
                    with c_d:
                        ev_date = st.date_input("Data:", value=def_date)
                    with c_t:
                        ev_time = st.time_input("Hora:", value=def_time)

                    location = st.text_input("Local de Encontro:", value=event_to_edit.get("location", "") if event_to_edit else "")
                    distance = st.text_input("Distância / Ritmo (ex: 12 km - 5:30/km):", value=event_to_edit.get("distance", "") if event_to_edit else "")
                    description = st.text_area("Observações importantes:", value=event_to_edit.get("description", "") if event_to_edit else "")

                    btn_text = "💾 Salvar Alterações" if event_to_edit else "🚀 Publicar Evento"
                    submitted = st.form_submit_button(btn_text, use_container_width=True, type="primary")

                    if submitted:
                        if not title.strip():
                            st.error("O título do evento é obrigatório.")
                        else:
                            updated_item = {
                                "id": event_to_edit["id"] if event_to_edit else str(uuid.uuid4())[:8],
                                "title": title.strip(),
                                "type": selected_type,
                                "date": ev_date.strftime("%Y-%m-%d"),
                                "time": ev_time.strftime("%H:%M"),
                                "location": location.strip(),
                                "distance": distance.strip(),
                                "description": description.strip()
                            }
                            if event_to_edit:
                                events = [updated_item if e["id"] == event_to_edit["id"] else e for e in events]
                                st.session_state.pop("editing_event_id", None)
                            else:
                                events.append(updated_item)
                            
                            save_events(events)
                            st.success("Guardado com sucesso!")
                            st.rerun()

                if event_to_edit:
                    if st.button("Cancelar Edição", use_container_width=True):
                        st.session_state.pop("editing_event_id", None)
                        st.rerun()


# =============================================================
# ABA 2: VOTAÇÕES
# =============================================================
with tab_polls:
    if st.session_state["is_admin"]:
        col_poll_list, col_poll_form = st.columns([1.5, 1.1], gap="large")
    else:
        col_poll_list = st.container()
        col_poll_form = None

    with col_poll_list:
        st.subheader("🗳️ Decisões & Votações em Curso")

        if not polls:
            st.info("Nenhuma votação ativa de momento.")
        else:
            for poll in polls:
                with st.container(border=True):
                    p_head, p_del = st.columns([3, 1] if st.session_state["is_admin"] else [1, 0.01])
                    with p_head:
                        st.markdown(f"#### ❓ {poll.get('question')}")
                        st.caption(f"Aberta em: {poll.get('created_at', 'N/D')}")
                    
                    if st.session_state["is_admin"]:
                        with p_del:
                            if st.button("🗑️ Fechar", key=f"del_poll_btn_{poll['id']}", help="Remover votação"):
                                polls = [p for p in polls if p["id"] != poll["id"]]
                                save_polls(polls)
                                st.success("Votação encerrada.")
                                st.rerun()

                    options = poll.get("options", [])
                    total_votes = sum(opt.get("votes", 0) for opt in options)

                    st.markdown("**Escolha a sua opção:**")
                    sel_idx = st.radio(
                        "Opções:",
                        options=range(len(options)),
                        format_func=lambda i: options[i]["text"],
                        key=f"vote_radio_{poll['id']}",
                        label_visibility="collapsed"
                    )

                    if st.button("Confirmar Voto", key=f"submit_vote_{poll['id']}", type="primary"):
                        options[sel_idx]["votes"] = options[sel_idx].get("votes", 0) + 1
                        save_polls(polls)
                        st.success("Obrigado! O seu voto foi contabilizado.")
                        st.rerun()

                    st.divider()
                    st.caption(f"📊 **Resultados em Tempo Real** ({total_votes} votos registados)")

                    if total_votes > 0:
                        df_chart = pd.DataFrame([
                            {"Opção": o["text"], "Votos": o.get("votes", 0)}
                            for o in options
                        ])
                        st.bar_chart(df_chart.set_index("Opção"))
                    else:
                        for opt in options:
                            st.write(f"- {opt['text']}: 0 votos")

    # Criação de Novas Votações (apenas Admin)
    if col_poll_form:
        with col_poll_form:
            with st.container(border=True):
                st.subheader("➕ Lançar Nova Votação")
                st.caption("Crie uma sondagem para o grupo escolher horários, percursos ou pontos de encontro.")

                with st.form("admin_new_poll_form", clear_on_submit=True):
                    poll_q = st.text_input("Pergunta da Votação:", placeholder="ex: Onde fazemos o treino de Sábado?")
                    poll_opts_raw = st.text_area(
                        "Opções de resposta (uma por linha):",
                        placeholder="Marginal\nParque da Cidade\nFoz do Douro",
                        height=120
                    )
                    submit_poll = st.form_submit_button("🚀 Abrir Votação", use_container_width=True, type="primary")

                    if submit_poll:
                        clean_q = poll_q.strip()
                        opts_list = [line.strip() for line in poll_opts_raw.splitlines() if line.strip()]

                        if not clean_q:
                            st.error("Insira a pergunta.")
                        elif len(opts_list) < 2:
                            st.error("Forneça pelo menos 2 opções de resposta.")
                        else:
                            new_poll = {
                                "id": str(uuid.uuid4())[:8],
                                "question": clean_q,
                                "options": [{"text": op, "votes": 0} for op in opts_list],
                                "active": True,
                                "created_at": date.today().strftime("%Y-%m-%d")
                            }
                            polls.append(new_poll)
                            save_polls(polls)
                            st.success("Votação publicada com sucesso!")
                            st.rerun()
