import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

# importar dados fake
from mock_data import (
    df_usuarios,
    df_instituicoes,
    df_itens,
    df_doacoes,
    df_impacto,
    df_doacao_itens
)

# =========================================================
# CONFIG BÁSICA
# =========================================================
st.set_page_config(
    page_title="HelpLink – Dashboard de Dados",
    layout="wide",
    page_icon="❤️",
)

# CSS
st.markdown("""
<style>
.main { background-color: #05070b; color: #f5f5f5; }
[data-testid="stSidebar"] { background-color: #05070b; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# FILTROS
# =========================================================
st.sidebar.header("⚙️ Filtros")

min_data = df_doacoes["DT_SOLICITACAO"].dt.date.min()
max_data = df_doacoes["DT_SOLICITACAO"].dt.date.max()

periodo = st.sidebar.date_input(
    "Período das doações",
    value=(min_data, max_data),
    min_value=min_data,
    max_value=max_data,
)

data_ini, data_fim = periodo

status_unicos = sorted(df_doacoes["STATUS"].unique())
status_selecionados = st.sidebar.multiselect(
    "Status",
    options=status_unicos,
    default=status_unicos
)

opcoes_inst = ["Todas"] + sorted(df_instituicoes["NOME"])
inst_escolhida = st.sidebar.selectbox(
    "Filtrar por instituição",
    opcoes_inst
)

# =========================================================
# APLICA FILTROS
# =========================================================
df_doacoes_filtrado = df_doacoes[
    (df_doacoes["DT_SOLICITACAO"].dt.date >= data_ini) &
    (df_doacoes["DT_SOLICITACAO"].dt.date <= data_fim) &
    (df_doacoes["STATUS"].isin(status_selecionados))
]

if inst_escolhida != "Todas":
    id_inst = df_instituicoes.loc[
        df_instituicoes["NOME"] == inst_escolhida, "ID_INSTITUICAO"
    ].iloc[0]
    df_doacoes_filtrado = df_doacoes_filtrado[
        df_doacoes_filtrado["ID_INSTITUICAO"] == id_inst
    ]

ids_doacoes = df_doacoes_filtrado["ID_DOACAO"].tolist()
df_doacao_itens_filtrado = df_doacao_itens[df_doacao_itens["ID_DOACAO"].isin(ids_doacoes)]
df_impacto_filtrado = df_impacto[df_impacto["ID_DOACAO"].isin(ids_doacoes)]

# =========================================================
# TÍTULO
# =========================================================
st.title("❤️ HelpLink – Dashboard de Dados")
st.caption("Versão demonstrativa sem banco de dados (dados mock)")

st.markdown("---")

# =========================================================
# MÉTRICAS
# =========================================================
st.subheader("📌 Indicadores Gerais")
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_doacoes = len(df_doacoes_filtrado)
total_concluidas = (df_doacoes_filtrado["STATUS"] == "CONCLUIDA").sum()
total_abertas = (df_doacoes_filtrado["STATUS"] == "ABERTA").sum()
taxa = (total_concluidas / total_doacoes * 100) if total_doacoes > 0 else 0

col1.metric("Usuários", len(df_usuarios))
col2.metric("Instituições", len(df_instituicoes))
col3.metric("Itens", len(df_itens))
col4.metric("Doações", total_doacoes)
col5.metric("Concluídas", total_concluidas)
col6.metric("Taxa conclusão", f"{taxa:.1f}%")

st.markdown("---")

# =========================================================
# STATUS
# =========================================================
st.subheader("📊 Visão Geral das Doações")

col_left, col_right = st.columns(2)

with col_left:
    df_status = df_doacoes_filtrado["STATUS"].value_counts().reset_index()
    df_status.columns = ["STATUS", "QTD"]
    fig = px.bar(df_status, x="STATUS", y="QTD", text="QTD", template="plotly_dark")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    fig = px.pie(df_status, names="STATUS", values="QTD", template="plotly_dark", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# LINHA DO TEMPO
# =========================================================
st.subheader("📈 Evolução das Doações")

df_tempo = df_doacoes_filtrado.copy()
df_tempo["DATA"] = df_tempo["DT_SOLICITACAO"].dt.date
df_tempo = df_tempo.groupby("DATA").size().reset_index(name="QTD")

fig = px.line(df_tempo, x="DATA", y="QTD", markers=True, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# HEATMAP – HORÁRIOS DE PICO DE DOAÇÕES
# =========================================================
st.subheader("🔥 Heatmap – Horários de Pico de Doações")

if not df_doacoes_filtrado.empty:
    df_heat = df_doacoes_filtrado.copy()
    df_heat = df_heat.dropna(subset=["DT_SOLICITACAO"])
    df_heat["HORA"] = df_heat["DT_SOLICITACAO"].dt.hour
    df_heat["DIA_IDX"] = df_heat["DT_SOLICITACAO"].dt.dayofweek

    ordem_dias = {
        0: "Segunda",
        1: "Terça",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sábado",
        6: "Domingo",
    }

    df_heat["DIA"] = df_heat["DIA_IDX"].map(ordem_dias)

    custom_colorscale = [
        [0.0, '#0a0a0a'],
        [0.2, '#102030'],
        [0.4, '#123456'],
        [0.6, '#1e5f8e'],
        [0.8, '#2d8fcb'],
        [1.0, '#4aa8ff'],
    ]

    fig_heat = px.density_heatmap(
        df_heat,
        x="HORA",
        y="DIA",
        template="plotly_dark",
        nbinsx=24,
        color_continuous_scale=custom_colorscale,
        labels={"HORA": "Hora do Dia", "DIA": "Dia da Semana"},
    )

    fig_heat.update_layout(
        height=420,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False,
            tickmode="linear",
            dtick=1
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=[
                "Segunda",
                "Terça",
                "Quarta",
                "Quinta",
                "Sexta",
                "Sábado",
                "Domingo",
            ],
            showgrid=False
        )
    )

    st.plotly_chart(fig_heat, use_container_width=True)

else:
    st.info("Nenhuma doação encontrada para montar o heatmap.")

st.markdown("---")

# =========================================================
# DADOS DETALHADOS
# =========================================================
st.subheader("📑 Dados Detalhados")

tabs = st.tabs(
    ["Usuários", "Instituições", "Itens", "Doações", "Itens das Doações", "Impacto"]
)

with tabs[0]:
    st.markdown("### 👤 Usuários")
    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

with tabs[1]:
    st.markdown("### 🏢 Instituições")
    st.dataframe(df_instituicoes, use_container_width=True, hide_index=True)

with tabs[2]:
    st.markdown("### 🎁 Itens")
    st.dataframe(df_itens, use_container_width=True, hide_index=True)

with tabs[3]:
    st.markdown("### 📦 Doações (filtradas)")
    st.dataframe(df_doacoes_filtrado, use_container_width=True, hide_index=True)

with tabs[4]:
    st.markdown("### 🎁 Itens das Doações (filtradas)")
    st.dataframe(df_doacao_itens_filtrado, use_container_width=True, hide_index=True)

with tabs[5]:
    st.markdown("### 🌱 Impacto (filtrado)")
    st.dataframe(df_impacto_filtrado, use_container_width=True, hide_index=True)

st.caption("Dashboard demonstrativo – FIAP 2025")
