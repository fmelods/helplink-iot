import streamlit as st
import pandas as pd
import cx_Oracle

# =========================================================
# CONFIGURAÇÕES DO STREAMLIT
# =========================================================
st.set_page_config(
    page_title="HelpLink – Dashboard de Dados",
    layout="wide",
    page_icon="❤️"
)

st.title("❤️ HelpLink – Dashboard de Dados")
st.caption("Monitoramento de doações, usuários e instituições")

# =========================================================
# CONEXÃO COM BANCO (USANDO SECRETS)
# =========================================================
USER = st.secrets["oracle"]["USER"]
PASSWORD = st.secrets["oracle"]["PASSWORD"]
DSN = st.secrets["oracle"]["DSN"]

def conectar():
    try:
        conn = cx_Oracle.connect(USER, PASSWORD, DSN)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar no banco: {e}")
        return None


conn = conectar()
if not conn:
    st.stop()

# =========================================================
# FUNÇÃO AUXILIAR PARA CONSULTAR
# =========================================================
def query(sql):
    try:
        df = pd.read_sql(sql, conn)
        return df
    except Exception as e:
        st.error(
            f"Erro ao consultar o banco: {e}\nSQL: {sql}"
        )
        return pd.DataFrame()

# =========================================================
# CONSULTAS PRINCIPAIS
# =========================================================
sql_usuarios = "SELECT * FROM TB_HELPLINK_USUARIO"
sql_instituicoes = "SELECT * FROM TB_HELPLINK_INSTITUICAO"
sql_itens = "SELECT * FROM TB_HELPLINK_ITEM"
sql_doacoes = "SELECT * FROM TB_HELPLINK_DOACAO"
sql_itens_doacoes = """
    SELECT 
        di.ID_DOACAO_ITEM,
        di.QTDE,
        d.ID_DOACAO,
        it.TITULO AS ITEM
    FROM TB_HELPLINK_DOACAO_ITEM di
    JOIN TB_HELPLINK_DOACAO d   ON d.ID_DOACAO = di.ID_DOACAO
    JOIN TB_HELPLINK_ITEM it    ON it.ID_ITEM = di.ID_ITEM
"""

sql_impactos = "SELECT * FROM TB_HELPLINK_IMPACTO"

usuarios = query(sql_usuarios)
instituicoes = query(sql_instituicoes)
itens = query(sql_itens)
doacoes = query(sql_doacoes)
itens_doacoes = query(sql_itens_doacoes)
impactos = query(sql_impactos)

# =========================================================
# MÉTRICAS SUPERIORES
# =========================================================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Usuários cadastrados", len(usuarios))
col2.metric("Instituições", len(instituicoes))
col3.metric("Itens disponíveis", len(itens))
col4.metric("Doações totais", len(doacoes))

# =========================================================
# DOAÇÕES POR STATUS
# =========================================================
st.markdown("### 📊 Doações por Status")

if not doacoes.empty:
    chart_status = (
        doacoes.groupby("STATUS")
        .size()
        .reset_index(name="count")
    )
    st.bar_chart(chart_status, x="STATUS", y="count")
else:
    st.info("Sem dados de doações.")

# =========================================================
# PONTUAÇÃO DE IMPACTO
# =========================================================
st.markdown("### 🌱 Pontuação de Impacto")

if not impactos.empty:
    st.bar_chart(impactos, x="ID_DOACAO", y="PONTUACAO")
else:
    st.info("Sem dados de impacto.")

# =========================================================
# ABA DE DADOS DETALHADOS
# =========================================================
st.markdown("### 📋 Dados Detalhados")

abas = st.tabs(["Usuários", "Instituições", "Itens", "Doações", "Itens das Doações"])

with abas[0]:
    st.dataframe(usuarios)

with abas[1]:
    st.dataframe(instituicoes)

with abas[2]:
    st.dataframe(itens)

with abas[3]:
    st.dataframe(doacoes)

with abas[4]:
    st.dataframe(itens_doacoes)

# Rodapé
st.markdown("---")
st.caption("Dashboard Helplink - FIAP 2025")
