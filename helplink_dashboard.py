import streamlit as st
import pandas as pd
import plotly.express as px
import cx_Oracle
from datetime import datetime, timedelta

# ==============================
# CONFIGURAÇÃO DO LAYOUT
# ==============================
st.set_page_config(
    page_title="HelpLink – Dashboard de Dados",
    page_icon="❤️",
    layout="wide"
)

st.markdown(
    "<h1 style='font-size:40px;'>❤️ HelpLink – Dashboard de Dados</h1>"
    "<p>Monitoramento de doações, usuários, itens, impacto e instituições (Oracle Cloud)</p>",
    unsafe_allow_html=True
)

# ==============================
# LER SECRETS
# ==============================
if "oracle" not in st.secrets:
    st.error("Erro ao ler secrets.toml. Verifique se existe a sessão [oracle] com USER, PASSWORD e DSN.")
    st.stop()

USER = st.secrets["oracle"].get("USER")
PASSWORD = st.secrets["oracle"].get("PASSWORD")
DSN = st.secrets["oracle"].get("DSN")

if not USER or not PASSWORD or not DSN:
    st.error("As credenciais do banco não foram encontradas no secrets.toml.")
    st.stop()

# ==============================
# CONEXÃO COM ORACLE
# ==============================
def get_connection():
    try:
        return cx_Oracle.connect(user=USER, password=PASSWORD, dsn=DSN)
    except Exception as e:
        st.error(f"Erro ao conectar no Oracle: {e}")
        st.stop()


# ==============================
# CONSULTA GENÉRICA
# ==============================
def query(sql):
    try:
        conn = get_connection()
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao consultar o banco: {e}")
        return pd.DataFrame()


# ============================================
# CONSULTAS PRINCIPAIS (NÃO MEXI EM NADA)
# ============================================

sql_usuarios = "SELECT * FROM TB_HELPLINK_USUARIO"
sql_instituicoes = "SELECT * FROM TB_HELPLINK_INSTITUICAO"
sql_itens = "SELECT * FROM TB_HELPLINK_ITEM"

sql_doacoes = """
SELECT 
    d.ID_DOACAO,
    d.STATUS,
    d.DT_SOLICITACAO,
    d.DT_CONFIRMACAO,
    d.ID_USUARIO,
    d.ID_INSTITUICAO
FROM TB_HELPLINK_DOACAO d
"""

sql_itens_doacao = """
SELECT 
    di.ID_DOACAO_ITEM,
    di.QTDE,
    d.ID_DOACAO,
    it.NOME AS ITEM
FROM TB_HELPLINK_DOACAO_ITEM di
JOIN TB_HELPLINK_DOACAO d ON d.ID_DOACAO = di.ID_DOACAO
JOIN TB_HELPLINK_ITEM it ON it.ID_ITEM = di.ID_ITEM
"""

sql_impacto = """
SELECT 
    ID_IMPACTO,
    ID_DOACAO,
    PONTUACAO
FROM TB_HELPLINK_IMPACTO
"""

# ==============================
# CARREGAR DADOS
# ==============================
df_users = query(sql_usuarios)
df_inst = query(sql_instituicoes)
df_itens = query(sql_itens)
df_doacoes = query(sql_doacoes)
df_doacao_itens = query(sql_itens_doacao)
df_impacto = query(sql_impacto)

# ==============================
# FILTROS LATERAIS
# ==============================
st.sidebar.header("⚙️ Filtros")

min_date = df_doacoes["DT_SOLICITACAO"].min()
max_date = df_doacoes["DT_SOLICITACAO"].max()

periodo = st.sidebar.date_input(
    "Período das doações",
    (min_date, max_date)
)

statuses = st.sidebar.multiselect(
    "Status das doações",
    ["ABERTA", "AGENDADA", "CONCLUIDA"],
    default=["ABERTA", "AGENDADA", "CONCLUIDA"]
)

inst_list = ["Todas"] + sorted(df_inst["NOME"].tolist())
inst_filter = st.sidebar.selectbox("Filtrar por instituição (opcional)", inst_list)

df = df_doacoes.copy()
df = df[(df["DT_SOLICITACAO"] >= pd.to_datetime(periodo[0])) &
        (df["DT_SOLICITACAO"] <= pd.to_datetime(periodo[1]) + pd.Timedelta(days=1))]

df = df[df["STATUS"].isin(statuses)]

if inst_filter != "Todas":
    inst_id = df_inst[df_inst["NOME"] == inst_filter]["ID_INSTITUICAO"].values[0]
    df = df[df["ID_INSTITUICAO"] == inst_id]

# ==============================
# KPIS
# ==============================
st.markdown("## 📌 Indicadores Gerais")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Usuários cadastrados", df_users.shape[0])
col2.metric("Instituições", df_inst.shape[0])
col3.metric("Itens disponíveis", df_itens.shape[0])
col4.metric("Doações (período/filtradas)", df.shape[0])
col5.metric("Doações concluídas", df[df["STATUS"] == "CONCLUIDA"].shape[0])
col6.metric("Doações abertas", df[df["STATUS"] == "ABERTA"].shape[0])

# ==============================
# GRÁFICO POR STATUS
# ==============================
st.markdown("## 📊 Visão Geral das Doações")

colA, colB = st.columns(2)

with colA:
    st.write("### Doações por Status")
    df_status = df["STATUS"].value_counts().reset_index()
    df_status.columns = ["STATUS", "QTD"]

    fig = px.bar(df_status, x="STATUS", y="QTD", color="STATUS")
    st.plotly_chart(fig, use_container_width=True)

with colB:
    st.write("### Distribuição de Doações por Status")
    fig2 = px.pie(df_status, names="STATUS", values="QTD")
    st.plotly_chart(fig2, use_container_width=True)

# ==============================
# EVOLUÇÃO NO TEMPO
# ==============================
st.markdown("## 📈 Evolução das Doações ao Longo do Tempo")

df_tempo = df.copy()
df_tempo["DATA"] = df_tempo["DT_SOLICITACAO"].dt.date
df_tempo_count = df_tempo.groupby("DATA").size().reset_index(name="QTD")

fig3 = px.line(df_tempo_count, x="DATA", y="QTD", markers=True)
st.plotly_chart(fig3, use_container_width=True)

# ==============================
# INSTITUIÇÕES / ITENS / IMPACTO
# ==============================
st.markdown("## 🏢 Instituições, 🎁 Itens e 🌱 Impacto")

colI1, colI2, colI3 = st.columns(3)

# -----------------
# Top Instituições
# -----------------
df_inst_count = df.groupby("ID_INSTITUICAO").size().reset_index(name="QTD_DOACOES")
df_inst_count = df_inst_count.merge(df_inst, left_on="ID_INSTITUICAO", right_on="ID_INSTITUICAO", how="left")

fig4 = px.bar(
    df_inst_count.sort_values("QTD_DOACOES", ascending=False),
    x="QTD_DOACOES",
    y="NOME",
    orientation="h"
)

colI1.write("### Top Instituições por Doações")
colI1.plotly_chart(fig4, use_container_width=True)

# -----------------
# Itens Mais Doados
# -----------------
df_items_count = df_doacao_itens.groupby("ITEM").size().reset_index(name="QTDE")
fig5 = px.bar(
    df_items_count.sort_values("QTDE", ascending=False),
    x="QTDE",
    y="ITEM",
    orientation="h"
)
colI2.write("### Itens mais doados")
colI2.plotly_chart(fig5, use_container_width=True)

# -----------------
# Impacto
# -----------------
df_imp = df_impacto.merge(df_doacoes, on="ID_DOACAO", how="left")
fig6 = px.bar(df_imp, x="ID_DOACAO", y="PONTUACAO")
colI3.write("### Pontuação de Impacto por Doação")
colI3.plotly_chart(fig6, use_container_width=True)

# ========================================================
# 🔥 HEATMAP — CORRIGIDO PARA FUNCIONAR NO DEPLOY
# ========================================================
st.markdown("## 🔥 Heatmap – Horários de Pico de Doações")

df_heat = df.copy()

# Dicionário para converter nomes dos dias
dias_semana_pt = {
    "Monday": "Segunda",
    "Tuesday": "Terça",
    "Wednesday": "Quarta",
    "Thursday": "Quinta",
    "Friday": "Sexta",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

df_heat["DIA_SEMANA"] = df_heat["DT_SOLICITACAO"].dt.day_name().map(dias_semana_pt)
df_heat["HORA"] = df_heat["DT_SOLICITACAO"].dt.hour

df_heatmap = df_heat.groupby(["DIA_SEMANA","HORA"]).size().reset_index(name="CONTAGEM")

fig7 = px.density_heatmap(
    df_heatmap,
    x="HORA",
    y="DIA_SEMANA",
    z="CONTAGEM",
    color_continuous_scale="RdBu"
)

st.plotly_chart(fig7, use_container_width=True)

# ==============================
# TABELAS DETALHADAS
# ==============================
st.markdown("## 📋 Dados Detalhados")

tabs = st.tabs(["Usuários", "Instituições", "Itens", "Doações", "Itens das Doações", "Impacto"])

with tabs[0]:
    st.subheader("👤 Usuários")
    st.dataframe(df_users)

with tabs[1]:
    st.subheader("🏢 Instituições")
    st.dataframe(df_inst)

with tabs[2]:
    st.subheader("🎁 Itens")
    st.dataframe(df_itens)

with tabs[3]:
    st.subheader("📦 Doações")
    st.dataframe(df_doacoes)

with tabs[4]:
    st.subheader("📦 Itens das Doações")
    st.dataframe(df_doacao_itens)

with tabs[5]:
    st.subheader("🌱 Impacto das Doações")
    st.dataframe(df_impacto)

st.markdown("---")
st.caption("Dashboard Helplink - FIAP 2025")
