import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import oracledb
from datetime import datetime

# =========================================================
# CONFIG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="HelpLink – Dashboard de Dados",
    layout="wide",
    page_icon="❤️",
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("❤️ HelpLink – Dashboard de Dados")
st.caption("Monitoramento de doações, usuários, itens, impacto e instituições (Oracle Cloud)")

st.markdown("---")

# =========================================================
# FUNÇÕES DE BANCO
# =========================================================
@st.cache_resource
def get_connection():
    try:
        user = st.secrets["oracle"]["USER"]
        password = st.secrets["oracle"]["PASSWORD"]
        dsn = st.secrets["oracle"]["DSN"]
    except Exception:
        st.error(
            "❌ Erro ao ler secrets.toml. Verifique se existe a sessão `[oracle]` "
            "com `USER`, `PASSWORD` e `DSN`."
        )
        st.stop()

    try:
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        return conn
    except Exception as e:
        st.error(f"❌ Erro ao conectar no Oracle: {e}")
        st.stop()


@st.cache_data(ttl=60)
def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(query, conn)
    return df


# =========================================================
# CARREGAMENTO DOS DADOS
# (ajuste o schema se precisar: ex: RM556099.TB_HELPLINK_USUARIO)
# =========================================================
def carregar_dados():
    erros = []

    try:
        usuarios = run_query("SELECT * FROM TB_HELPLINK_USUARIO")
    except Exception as e:
        erros.append(f"Usuários: {e}")
        usuarios = pd.DataFrame()

    try:
        instituicoes = run_query("SELECT * FROM TB_HELPLINK_INSTITUICAO")
    except Exception as e:
        erros.append(f"Instituições: {e}")
        instituicoes = pd.DataFrame()

    try:
        itens = run_query("SELECT * FROM TB_HELPLINK_ITEM")
    except Exception as e:
        erros.append(f"Itens: {e}")
        itens = pd.DataFrame()

    try:
        categorias = run_query("SELECT * FROM TB_HELPLINK_CATEGORIA")
    except Exception as e:
        erros.append(f"Categorias: {e}")
        categorias = pd.DataFrame()

    try:
        doacoes = run_query("SELECT * FROM TB_HELPLINK_DOACAO")
    except Exception as e:
        erros.append(f"Doações: {e}")
        doacoes = pd.DataFrame()

    # Itens das doações (corrigido: IT.TITULO em vez de IT.NOME)
    try:
        doacao_itens = run_query(
            """
            SELECT di.ID_DOACAO_ITEM,
                   di.QTDE,
                   d.ID_DOACAO,
                   d.STATUS,
                   d.DT_SOLICITACAO,
                   it.ID_ITEM,
                   it.TITULO   AS NOME_ITEM
            FROM TB_HELPLINK_DOACAO_ITEM di
            JOIN TB_HELPLINK_DOACAO d ON d.ID_DOACAO = di.ID_DOACAO
            JOIN TB_HELPLINK_ITEM it  ON it.ID_ITEM = di.ID_ITEM
            """
        )
    except Exception as e:
        erros.append(f"Itens das Doações: {e}")
        doacao_itens = pd.DataFrame()

    try:
        impacto = run_query("SELECT * FROM TB_HELPLINK_IMPACTO")
    except Exception as e:
        erros.append(f"Impacto: {e}")
        impacto = pd.DataFrame()

    return {
        "erros": erros,
        "usuarios": usuarios,
        "instituicoes": instituicoes,
        "itens": itens,
        "categorias": categorias,
        "doacoes": doacoes,
        "doacao_itens": doacao_itens,
        "impacto": impacto,
    }


dados = carregar_dados()

# =========================================================
# MENSAGENS DE ERRO (SE HOUVER)
# =========================================================
if dados["erros"]:
    st.error("Erro ao consultar o banco:")
    for e in dados["erros"]:
        st.write("•", e)

usuarios = dados["usuarios"]
instituicoes = dados["instituicoes"]
itens = dados["itens"]
categorias = dados["categorias"]
doacoes = dados["doacoes"]
doacao_itens = dados["doacao_itens"]
impacto = dados["impacto"]

# Normalizações básicas
if "STATUS" in doacoes.columns:
    doacoes["STATUS"] = doacoes["STATUS"].astype(str).str.upper()

if "DT_SOLICITACAO" in doacoes.columns:
    doacoes["DT_SOLICITACAO"] = pd.to_datetime(doacoes["DT_SOLICITACAO"])

if "DT_CADASTRO" in usuarios.columns:
    usuarios["DT_CADASTRO"] = pd.to_datetime(usuarios["DT_CADASTRO"])

if "DT_REGISTRO" in itens.columns:
    try:
        itens["DT_REGISTRO"] = pd.to_datetime(itens["DT_REGISTRO"])
    except Exception:
        pass  # se a coluna não existir, ignora

# =========================================================
# SIDEBAR – FILTROS GERAIS
# =========================================================
st.sidebar.header("⚙️ Filtros")

# Filtro de período (por DT_SOLICITACAO)
if not doacoes.empty and "DT_SOLICITACAO" in doacoes.columns:
    min_data = doacoes["DT_SOLICITACAO"].min().date()
    max_data = doacoes["DT_SOLICITACAO"].max().date()

    periodo = st.sidebar.date_input(
        "Período das doações",
        value=(min_data, max_data),
        min_value=min_data,
        max_value=max_data,
    )

    if isinstance(periodo, tuple) and len(periodo) == 2:
        inicio, fim = periodo
        mask_data = (doacoes["DT_SOLICITACAO"].dt.date >= inicio) & (
            doacoes["DT_SOLICITACAO"].dt.date <= fim
        )
        doacoes_filtradas = doacoes[mask_data].copy()
    else:
        doacoes_filtradas = doacoes.copy()
else:
    doacoes_filtradas = doacoes.copy()

# Filtro de status
lista_status = sorted(doacoes_filtradas["STATUS"].unique()) if not doacoes_filtradas.empty else []
status_sel = st.sidebar.multiselect(
    "Status das doações",
    options=lista_status,
    default=lista_status,
)

if status_sel:
    doacoes_filtradas = doacoes_filtradas[doacoes_filtradas["STATUS"].isin(status_sel)]

# Filtro de instituição (para algumas visões)
if not instituicoes.empty:
    inst_map = dict(zip(instituicoes["ID_INSTITUICAO"], instituicoes["NOME"]))
    st.sidebar.markdown("---")
    inst_sel_nome = st.sidebar.selectbox(
        "Filtrar por instituição (opcional)",
        options=["Todas"] + sorted(inst_map.values()),
        index=0,
    )
else:
    inst_sel_nome = "Todas"

# =========================================================
# KPIs PRINCIPAIS
# =========================================================
st.subheader("📌 Indicadores Gerais")

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

total_usuarios = len(usuarios)
total_inst = len(instituicoes)
total_itens = len(itens)
total_doacoes = len(doacoes_filtradas)

col1.metric("Usuários cadastrados", total_usuarios)
col2.metric("Instituições", total_inst)
col3.metric("Itens disponíveis", total_itens)
col4.metric("Doações (período/filtradas)", total_doacoes)

# Doações por status
if not doacoes_filtradas.empty:
    df_status = (
        doacoes_filtradas.groupby("STATUS")
        .size()
        .reset_index(name="QTD")
        .sort_values("QTD", ascending=False)
    )
    concluidas = int(df_status.loc[df_status["STATUS"] == "CONCLUIDA", "QTD"].sum())
    abertas = int(df_status.loc[df_status["STATUS"] == "ABERTA", "QTD"].sum())
    canceladas = int(df_status.loc[df_status["STATUS"] == "CANCELADA", "QTD"].sum())
else:
    concluidas = abertas = canceladas = 0

# Itens por doação (média)
if not doacao_itens.empty:
    itens_por_doacao = (
        doacao_itens.groupby("ID_DOACAO")["QTDE"].sum().mean()
        if "QTDE" in doacao_itens.columns
        else None
    )
else:
    itens_por_doacao = None

# Impacto total e médio
if not impacto.empty and "PONTUACAO" in impacto.columns:
    impacto_total = impacto["PONTUACAO"].sum()
    impacto_medio = impacto["PONTUACAO"].mean()
else:
    impacto_total = impacto_medio = 0

# Taxa de conclusão
taxa_conclusao = (concluidas / total_doacoes * 100) if total_doacoes > 0 else 0

col5.metric("Doações concluídas", concluidas)
col6.metric("Doações abertas", abertas)
col7.metric("Itens médios por doação", f"{itens_por_doacao:.2f}" if itens_por_doacao else "-")
col8.metric("Taxa de conclusão", f"{taxa_conclusao:.1f}%")

st.markdown("---")

# =========================================================
# GRÁFICOS PRINCIPAIS
# =========================================================
st.subheader("📊 Visão Geral das Doações")

g1, g2 = st.columns(2)

# 1) Barras - Doações por status
if not doacoes_filtradas.empty:
    fig_status = px.bar(
        df_status,
        x="STATUS",
        y="QTD",
        title="Doações por Status",
        text="QTD",
    )
    fig_status.update_layout(height=400)
    g1.plotly_chart(fig_status, use_container_width=True)
else:
    g1.info("Sem dados de doações para exibir por status.")

# 2) Pizza - Distribuição de status
if not doacoes_filtradas.empty:
    fig_pizza = px.pie(
        df_status,
        names="STATUS",
        values="QTD",
        title="Distribuição de Doações por Status",
        hole=0.4,
    )
    fig_pizza.update_traces(textposition="inside", textinfo="percent+label")
    fig_pizza.update_layout(height=400)
    g2.plotly_chart(fig_pizza, use_container_width=True)
else:
    g2.info("Sem dados de doações para exibir na pizza.")

# 3) Série temporal de doações
st.subheader("📈 Evolução das Doações ao Longo do Tempo")

if not doacoes_filtradas.empty and "DT_SOLICITACAO" in doacoes_filtradas.columns:
    df_tempo = (
        doacoes_filtradas
        .set_index("DT_SOLICITACAO")
        .resample("D")
        .size()
        .reset_index(name="QTD")
    )
    fig_tempo = px.line(
        df_tempo,
        x="DT_SOLICITACAO",
        y="QTD",
        markers=True,
        title="Doações por Dia",
    )
    fig_tempo.update_layout(height=400)
    st.plotly_chart(fig_tempo, use_container_width=True)
else:
    st.info("Sem datas de solicitação suficientes para montar a série temporal.")

st.markdown("---")

# =========================================================
# VISÕES AVANÇADAS (INSTITUIÇÕES, ITENS, IMPACTO)
# =========================================================
st.subheader("🏥 Instituições, 🎁 Itens e 🌱 Impacto")

c1, c2, c3 = st.columns(3)

# Ranking de instituições por quantidade de doações
if not doacoes_filtradas.empty and not instituicoes.empty:
    df_do_inst = doacoes_filtradas.merge(
        instituicoes[["ID_INSTITUICAO", "NOME"]],
        on="ID_INSTITUICAO",
        how="left",
    )
    df_inst_rank = (
        df_do_inst.groupby("NOME")
        .size()
        .reset_index(name="QTD_DOACOES")
        .sort_values("QTD_DOACOES", ascending=False)
        .head(10)
    )

    if inst_sel_nome != "Todas":
        df_inst_rank = df_inst_rank[df_inst_rank["NOME"] == inst_sel_nome]

    fig_inst = px.bar(
        df_inst_rank,
        x="QTD_DOACOES",
        y="NOME",
        orientation="h",
        title="Top Instituições por Doações",
        text="QTD_DOACOES",
    )
    fig_inst.update_layout(height=400, yaxis_title="")
    c1.plotly_chart(fig_inst, use_container_width=True)
else:
    c1.info("Sem dados suficientes para o ranking de instituições.")

# Ranking de itens mais doados
if not doacao_itens.empty:
    df_item_rank = (
        doacao_itens.groupby("NOME_ITEM")["QTDE"]
        .sum()
        .reset_index()
        .sort_values("QTDE", ascending=False)
        .head(10)
    )
    fig_item = px.bar(
        df_item_rank,
        x="QTDE",
        y="NOME_ITEM",
        orientation="h",
        title="Itens mais doados",
        text="QTDE",
    )
    fig_item.update_layout(height=400, yaxis_title="")
    c2.plotly_chart(fig_item, use_container_width=True)
else:
    c2.info("Sem dados de itens das doações para exibir ranking.")

# Impacto por doação
if not impacto.empty:
    fig_imp = px.bar(
        impacto.sort_values("ID_DOACAO"),
        x="ID_DOACAO",
        y="PONTUACAO",
        title="Pontuação de Impacto por Doação",
        text="PONTUACAO",
    )
    fig_imp.update_layout(height=400, xaxis_title="ID_DOACAO")
    c3.plotly_chart(fig_imp, use_container_width=True)
else:
    c3.info("Sem dados de impacto cadastrados.")

st.markdown("---")

# =========================================================
# HEATMAP – Doações por Dia da Semana x Hora
# =========================================================
st.subheader("🔥 Heatmap – Horários de Pico de Doações")

if not doacoes_filtradas.empty and "DT_SOLICITACAO" in doacoes_filtradas.columns:
    df_heat = doacoes_filtradas.copy()
    df_heat["DIA_SEMANA"] = df_heat["DT_SOLICITACAO"].dt.day_name(locale="pt_BR")
    df_heat["HORA"] = df_heat["DT_SOLICITACAO"].dt.hour

    tabela_heat = (
        df_heat.pivot_table(
            index="DIA_SEMANA",
            columns="HORA",
            values="ID_DOACAO",
            aggfunc="count",
            fill_value=0,
        )
        .reindex(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            axis=0,
        )
    )

    # Tradução simples dos dias (se quiser algo mais caprichado pode mapear)
    mapa_dias = {
        "Monday": "Segunda",
        "Tuesday": "Terça",
        "Wednesday": "Quarta",
        "Thursday": "Quinta",
        "Friday": "Sexta",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }
    tabela_heat.index = [mapa_dias.get(d, d) for d in tabela_heat.index]

    fig_heat = px.imshow(
        tabela_heat,
        aspect="auto",
        title="Volume de Doações por Dia da Semana e Hora",
        labels=dict(x="Hora do Dia", y="Dia da Semana", color="Qtde"),
    )
    fig_heat.update_layout(height=450)
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("Sem dados de data/hora suficientes para gerar o heatmap.")

st.markdown("---")

# =========================================================
# TABELAS DETALHADAS COM ABAS
# =========================================================
st.subheader("📚 Dados Detalhados")

tabs = st.tabs(
    ["Usuários", "Instituições", "Itens", "Doações", "Itens das Doações", "Impacto"]
)

with tabs[0]:
    st.markdown("### 👤 Usuários")
    if not usuarios.empty:
        st.dataframe(usuarios, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum usuário encontrado.")

with tabs[1]:
    st.markdown("### 🏥 Instituições")
    if not instituicoes.empty:
        st.dataframe(instituicoes, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma instituição encontrada.")

with tabs[2]:
    st.markdown("### 🎁 Itens")
    if not itens.empty:
        # Se tiver categoria ligada, faz JOIN pra ficar mais bonito
        if not categorias.empty and "ID_CATEGORIA" in itens.columns:
            itens_exibe = itens.merge(
                categorias[["ID_CATEGORIA", "NOME"]],
                on="ID_CATEGORIA",
                how="left",
                suffixes=("", "_CATEGORIA"),
            )
        else:
            itens_exibe = itens.copy()

        st.dataframe(itens_exibe, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum item cadastrado.")

with tabs[3]:
    st.markdown("### 📦 Doações")
    if not doacoes.empty:
        st.dataframe(doacoes, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma doação cadastrada.")

with tabs[4]:
    st.markdown("### 📦 Itens das Doações")
    if not doacao_itens.empty:
        st.dataframe(doacao_itens, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum item de doação encontrado.")

with tabs[5]:
    st.markdown("### 🌱 Impacto")
    if not impacto.empty:
        st.dataframe(impacto, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum registro de impacto encontrado.")

st.markdown("---")
st.caption("Dashboard Helplink - FIAP 2025")
