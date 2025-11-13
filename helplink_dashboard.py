import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import oracledb
from datetime import datetime, timedelta
import random
import numpy as np

# =========================================================
# CONFIG BÁSICA DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="HelpLink – Dashboard de Dados",
    layout="wide",
    page_icon="❤️",
)

# ---------------------------------------------------------
# CSS – tema dark mais bonitinho
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #05070b;
        color: #f5f5f5;
    }
    .stMetric {
        background-color: #111827;
        padding: 15px;
        border-radius: 10px;
    }
    .css-1d391kg, .css-18e3th9 {
        background-color: #05070b !important;
    }
    [data-testid="stSidebar"] {
        background-color: #05070b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# MODO DEMO - DADOS SIMULADOS
# =========================================================
def gerar_dados_demo():
    """
    Gera dados de demonstração para quando o banco não estiver disponível
    """
    np.random.seed(42)  # Para dados consistentes
    
    # Gerar datas
    data_inicio = datetime.now() - timedelta(days=90)
    datas = pd.date_range(start=data_inicio, end=datetime.now(), freq='D')
    
    # --- Usuários Demo ---
    df_usuarios = pd.DataFrame({
        'ID_USUARIO': range(1, 151),
        'NOME': [f'Usuário {i}' for i in range(1, 151)],
        'SENHA': ['****' for _ in range(150)],
        'DT_CADASTRO': pd.to_datetime([data_inicio + timedelta(days=random.randint(0, 90)) for _ in range(150)]),
        'EMAIL': [f'usuario{i}@email.com' for i in range(1, 151)],
        'TELEFONE': [f'11-9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}' for _ in range(150)],
        'ID_ENDERECO': range(1, 151)
    })
    
    # --- Instituições Demo ---
    instituicoes_nomes = [
        'Casa de Apoio São Francisco', 'Instituto Esperança', 'ONG Mãos Solidárias',
        'Associação Vida Nova', 'Centro Comunitário Esperança', 'Instituto Recomeço',
        'Casa de Acolhimento Luz', 'ONG Futuro Melhor', 'Associação Amigos do Bem',
        'Centro Social Renascer', 'Instituto Solidário', 'Casa da Criança',
        'ONG Novo Horizonte', 'Associação Comunidade Viva', 'Centro de Apoio Familiar'
    ]
    
    df_instituicoes = pd.DataFrame({
        'ID_INSTITUICAO': range(1, len(instituicoes_nomes) + 1),
        'NOME': instituicoes_nomes,
        'EMAIL': [f'{nome.lower().replace(" ", "")[:10]}@ong.org.br' for nome in instituicoes_nomes],
        'TELEFONE': [f'11-{random.randint(2000, 5999)}-{random.randint(1000, 9999)}' for _ in instituicoes_nomes],
        'ID_ENDERECO': range(101, 101 + len(instituicoes_nomes)),
        'CATEGORIAS_ACEITAS': ['Roupas, Alimentos, Brinquedos' for _ in instituicoes_nomes],
        'CNPJ': [f'{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/0001-{random.randint(10, 99)}' for _ in instituicoes_nomes]
    })
    
    # --- Itens Demo ---
    itens_lista = [
        'Cesta Básica', 'Roupas Infantis', 'Cobertores', 'Brinquedos',
        'Material Escolar', 'Calçados', 'Agasalhos', 'Fraldas',
        'Leite em Pó', 'Produtos de Higiene', 'Livros', 'Móveis',
        'Eletrodomésticos', 'Colchões', 'Roupas de Cama'
    ]
    
    df_itens = pd.DataFrame({
        'ID_ITEM': range(1, 201),
        'TITULO': [random.choice(itens_lista) for _ in range(200)],
        'FOTO_URL': ['https://exemplo.com/foto.jpg' for _ in range(200)],
        'ESTADO_CONSERVACAO': [random.choice(['NOVO', 'BOM', 'REGULAR']) for _ in range(200)],
        'DT_REGISTRO': pd.to_datetime([data_inicio + timedelta(days=random.randint(0, 90)) for _ in range(200)]),
        'DESCRICAO': ['Item em bom estado para doação' for _ in range(200)],
        'ID_DOACAO': [random.randint(1, 300) for _ in range(200)],
        'ID_USUARIO': [random.randint(1, 150) for _ in range(200)],
        'ID_CATEGORIA': [random.randint(1, 10) for _ in range(200)]
    })
    
    # --- Doações Demo ---
    status_opcoes = ['ABERTA', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA']
    status_pesos = [0.25, 0.15, 0.50, 0.10]  # 50% concluídas
    
    doacoes_data = []
    for i in range(1, 301):
        dt_solicitacao = data_inicio + timedelta(days=random.randint(0, 90))
        status = np.random.choice(status_opcoes, p=status_pesos)
        dt_confirmacao = dt_solicitacao + timedelta(days=random.randint(1, 7)) if status == 'CONCLUIDA' else None
        
        doacoes_data.append({
            'ID_DOACAO': i,
            'STATUS': status,
            'DT_SOLICITACAO': dt_solicitacao,
            'DT_CONFIRMACAO': pd.to_datetime(dt_confirmacao) if dt_confirmacao else pd.NaT,
            'ID_USUARIO': random.randint(1, 150),
            'ID_INSTITUICAO': random.randint(1, len(instituicoes_nomes))
        })
    
    df_doacoes = pd.DataFrame(doacoes_data)
    
    # --- Impacto Demo ---
    df_impacto = pd.DataFrame({
        'ID_IMPACTO': range(1, 151),
        'ID_DOACAO': random.sample(range(1, 301), 150),
        'PONTUACAO': [random.randint(70, 100) for _ in range(150)],
        'OBSERVACAO': ['Impacto positivo na comunidade' for _ in range(150)]
    })
    
    # --- Doação Itens Demo ---
    doacao_itens_data = []
    for i in range(1, 501):
        doacao_itens_data.append({
            'ID_DOACAO_ITEM': i,
            'QTDE': random.randint(1, 10),
            'ID_DOACAO': random.randint(1, 300),
            'ITEM': random.choice(itens_lista)
        })
    
    df_doacao_itens = pd.DataFrame(doacao_itens_data)
    
    return df_usuarios, df_instituicoes, df_itens, df_doacoes, df_impacto, df_doacao_itens


# =========================================================
# FUNÇÕES DE BANCO
# =========================================================

@st.cache_resource(show_spinner=False, ttl=300)
def get_connection():
    """
    Cria conexão Oracle usando oracledb em modo thin.
    Usa as credenciais definidas em .streamlit/secrets.toml
    """
    try:
        cfg = st.secrets["oracle"]
        user = cfg.get("USER")
        password = cfg.get("PASSWORD")
        dsn = cfg.get("DSN")
        
        conn = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn,
            encoding="UTF-8",
            nencoding="UTF-8"
        )
        return conn
    except:
        return None


def carregar_dados():
    """
    Lê todas as tabelas necessárias e devolve como DataFrames.
    Se falhar, usa dados de demonstração.
    """
    
    # Tenta conectar ao banco real
    try:
        conn = get_connection()
        if conn is None:
            raise Exception("Conexão falhou")
            
        # --- Queries originais ---
        q_usuarios = """
            SELECT ID_USUARIO,
                   NOME,
                   SENHA,
                   DT_CADASTRO,
                   EMAIL,
                   TELEFONE,
                   ID_ENDERECO
              FROM TB_HELPLINK_USUARIO
        """
        
        q_instituicoes = """
            SELECT ID_INSTITUICAO,
                   NOME,
                   EMAIL,
                   TELEFONE,
                   ID_ENDERECO,
                   CATEGORIAS_ACEITAS,
                   CNPJ
              FROM TB_HELPLINK_INSTITUICAO
        """
        
        q_itens = """
            SELECT ID_ITEM,
                   TITULO,
                   FOTO_URL,
                   ESTADO_CONSERVACAO,
                   DT_REGISTRO,
                   DESCRICAO,
                   ID_DOACAO,
                   ID_USUARIO,
                   ID_CATEGORIA
              FROM TB_HELPLINK_ITEM
        """
        
        q_doacoes = """
            SELECT ID_DOACAO,
                   STATUS,
                   DT_SOLICITACAO,
                   DT_CONFIRMACAO,
                   ID_USUARIO,
                   ID_INSTITUICAO
              FROM TB_HELPLINK_DOACAO
        """
        
        q_impacto = """
            SELECT ID_IMPACTO,
                   ID_DOACAO,
                   PONTUACAO,
                   OBSERVACAO
              FROM TB_HELPLINK_IMPACTO
        """
        
        q_doacao_itens = """
            SELECT di.ID_DOACAO_ITEM,
                   di.QTDE,
                   d.ID_DOACAO,
                   it.TITULO AS ITEM
              FROM TB_HELPLINK_DOACAO_ITEM di
              JOIN TB_HELPLINK_DOACAO d
                ON d.ID_DOACAO = di.ID_DOACAO
              JOIN TB_HELPLINK_ITEM it
                ON it.ID_ITEM = di.ID_ITEM
        """
        
        df_usuarios = pd.read_sql(q_usuarios, conn)
        df_instituicoes = pd.read_sql(q_instituicoes, conn)
        df_itens = pd.read_sql(q_itens, conn)
        df_doacoes = pd.read_sql(q_doacoes, conn)
        df_impacto = pd.read_sql(q_impacto, conn)
        df_doacao_itens = pd.read_sql(q_doacao_itens, conn)
        
        conn.close()
        
        # Garantir datetime
        for col in ["DT_CADASTRO"]:
            if col in df_usuarios.columns:
                df_usuarios[col] = pd.to_datetime(df_usuarios[col], errors="coerce")
        
        for col in ["DT_REGISTRO"]:
            if col in df_itens.columns:
                df_itens[col] = pd.to_datetime(df_itens[col], errors="coerce")
        
        for col in ["DT_SOLICITACAO", "DT_CONFIRMACAO"]:
            if col in df_doacoes.columns:
                df_doacoes[col] = pd.to_datetime(df_doacoes[col], errors="coerce")
        
        # Indica que está usando dados reais
        st.sidebar.success("✅ Conectado ao banco Oracle")
        
        return df_usuarios, df_instituicoes, df_itens, df_doacoes, df_impacto, df_doacao_itens
        
    except Exception as e:
        # Se falhar, usa dados demo
        st.sidebar.warning("⚠️ Usando dados de demonstração")
        st.sidebar.caption("Banco Oracle indisponível")
        return gerar_dados_demo()


# =========================================================
# CARREGAMENTO DOS DADOS
# =========================================================
(
    df_usuarios,
    df_instituicoes,
    df_itens,
    df_doacoes,
    df_impacto,
    df_doacao_itens,
) = carregar_dados()

# =========================================================
# SIDEBAR – FILTROS
# =========================================================
st.sidebar.header("⚙️ Filtros")

# Período das doações
if not df_doacoes.empty:
    min_data = df_doacoes["DT_SOLICITACAO"].dt.date.min()
    max_data = df_doacoes["DT_SOLICITACAO"].dt.date.max()
else:
    hoje = datetime.today().date()
    min_data = hoje - timedelta(days=30)
    max_data = hoje

periodo = st.sidebar.date_input(
    "Período das doações",
    value=(min_data, max_data),
    min_value=min_data,
    max_value=max_data,
)

if isinstance(periodo, tuple):
    data_ini, data_fim = periodo
else:
    data_ini = periodo
    data_fim = periodo

# Status das doações
status_unicos = sorted(df_doacoes["STATUS"].dropna().unique())
status_default = status_unicos

status_selecionados = st.sidebar.multiselect(
    "Status das doações",
    options=status_unicos,
    default=status_default,
)

# Filtro por instituição
opcoes_inst = ["Todas"] + sorted(df_instituicoes["NOME"].tolist())
inst_escolhida = st.sidebar.selectbox(
    "Filtrar por instituição (opcional)", options=opcoes_inst
)

# =========================================================
# APLICAÇÃO DOS FILTROS
# =========================================================
df_doacoes_filtrado = df_doacoes.copy()

# Filtro de data
df_doacoes_filtrado = df_doacoes_filtrado[
    (df_doacoes_filtrado["DT_SOLICITACAO"].dt.date >= data_ini)
    & (df_doacoes_filtrado["DT_SOLICITACAO"].dt.date <= data_fim)
]

# Filtro de status
if status_selecionados:
    df_doacoes_filtrado = df_doacoes_filtrado[
        df_doacoes_filtrado["STATUS"].isin(status_selecionados)
    ]

# Filtro de instituição
if inst_escolhida != "Todas":
    id_inst = df_instituicoes.loc[
        df_instituicoes["NOME"] == inst_escolhida, "ID_INSTITUICAO"
    ]
    if not id_inst.empty:
        df_doacoes_filtrado = df_doacoes_filtrado[
            df_doacoes_filtrado["ID_INSTITUICAO"] == int(id_inst.iloc[0])
        ]

# IDs de doações filtradas
ids_doacoes_filtradas = df_doacoes_filtrado["ID_DOACAO"].tolist()

df_doacao_itens_filtrado = df_doacao_itens[
    df_doacao_itens["ID_DOACAO"].isin(ids_doacoes_filtradas)
].copy()

df_impacto_filtrado = df_impacto[
    df_impacto["ID_DOACAO"].isin(ids_doacoes_filtradas)
].copy()

# =========================================================
# TÍTULO PRINCIPAL
# =========================================================
st.title("❤️ HelpLink – Dashboard de Dados")
st.caption(
    "Monitoramento de doações, usuários, itens, impacto e instituições"
)

st.markdown("---")

# =========================================================
# INDICADORES GERAIS
# =========================================================
st.subheader("📌 Indicadores Gerais")

col1, col2, col3, col4, col5, col6 = st.columns(6)

total_usuarios = len(df_usuarios)
total_instituicoes = len(df_instituicoes)
total_itens = len(df_itens)
total_doacoes_periodo = len(df_doacoes_filtrado)
total_concluidas = (df_doacoes_filtrado["STATUS"] == "CONCLUIDA").sum()
total_abertas = (df_doacoes_filtrado["STATUS"] == "ABERTA").sum()

if not df_doacao_itens_filtrado.empty and total_doacoes_periodo > 0:
    itens_totais = df_doacao_itens_filtrado["QTDE"].sum()
    itens_medios = itens_totais / total_doacoes_periodo
else:
    itens_medios = 0

taxa_conclusao = (
    (total_concluidas / total_doacoes_periodo) * 100
    if total_doacoes_periodo > 0
    else 0
)

col1.metric("Usuários cadastrados", total_usuarios)
col2.metric("Instituições", total_instituicoes)
col3.metric("Itens disponíveis", total_itens)
col4.metric("Doações (período)", total_doacoes_periodo)
col5.metric("Doações concluídas", total_concluidas)
col6.metric("Taxa de conclusão", f"{taxa_conclusao:.1f}%")

st.markdown("---")

# =========================================================
# VISÃO GERAL DAS DOAÇÕES (status)
# =========================================================
st.subheader("📊 Visão Geral das Doações")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Doações por Status")
    
    if not df_doacoes_filtrado.empty:
        s = df_doacoes_filtrado["STATUS"].value_counts()
        df_status = s.reset_index()
        df_status.columns = ["STATUS", "QTD"]
        
        fig_bar_status = px.bar(
            df_status,
            x="STATUS",
            y="QTD",
            text="QTD",
            template="plotly_dark",
            labels={"STATUS": "Status", "QTD": "Quantidade"},
        )
        fig_bar_status.update_traces(textposition="outside")
        fig_bar_status.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_bar_status, use_container_width=True)
    else:
        st.info("Nenhuma doação encontrada com os filtros selecionados.")

with col_right:
    st.markdown("#### Distribuição de Doações por Status")
    
    if not df_doacoes_filtrado.empty:
        fig_pie_status = px.pie(
            df_status,
            names="STATUS",
            values="QTD",
            hole=0.4,
            template="plotly_dark",
        )
        fig_pie_status.update_layout(height=400)
        st.plotly_chart(fig_pie_status, use_container_width=True)
    else:
        st.info("Nenhuma doação encontrada com os filtros selecionados.")

st.markdown("---")

# =========================================================
# EVOLUÇÃO DAS DOAÇÕES AO LONGO DO TEMPO
# =========================================================
st.subheader("📈 Evolução das Doações ao Longo do Tempo")

if not df_doacoes_filtrado.empty:
    df_tempo = df_doacoes_filtrado.copy()
    df_tempo["DATA"] = df_tempo["DT_SOLICITACAO"].dt.date
    df_tempo = (
        df_tempo.groupby("DATA")["ID_DOACAO"]
        .count()
        .reset_index(name="QTD_DOACOES")
    )
    
    fig_line_tempo = px.line(
        df_tempo,
        x="DATA",
        y="QTD_DOACOES",
        markers=True,
        template="plotly_dark",
        labels={"DATA": "Data", "QTD_DOACOES": "Qtd de Doações"},
    )
    fig_line_tempo.update_layout(height=450)
    st.plotly_chart(fig_line_tempo, use_container_width=True)
else:
    st.info("Nenhuma doação encontrada para montar a série temporal.")

st.markdown("---")

# =========================================================
# INSTITUIÇÕES, ITENS E IMPACTO
# =========================================================
st.subheader("🏢 Instituições, 🎁 Itens e 🌱 Impacto")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("#### Top Instituições por Doações")
    if not df_doacoes_filtrado.empty:
        df_inst_count = (
            df_doacoes_filtrado.groupby("ID_INSTITUICAO")["ID_DOACAO"]
            .count()
            .reset_index(name="QTD_DOACOES")
        )
        df_inst_count = df_inst_count.merge(
            df_instituicoes[["ID_INSTITUICAO", "NOME"]],
            on="ID_INSTITUICAO",
            how="left",
        )
        df_inst_count = df_inst_count.sort_values(
            "QTD_DOACOES", ascending=False
        ).head(10)
        
        fig_inst = px.bar(
            df_inst_count,
            x="QTD_DOACOES",
            y="NOME",
            orientation="h",
            template="plotly_dark",
            labels={"NOME": "Instituição", "QTD_DOACOES": "Qtd Doações"},
        )
        fig_inst.update_layout(height=450)
        st.plotly_chart(fig_inst, use_container_width=True)
    else:
        st.info("Sem doações filtradas para exibir instituições.")

with c2:
    st.markdown("#### Itens mais doados")
    if not df_doacao_itens_filtrado.empty:
        df_items_count = (
            df_doacao_itens_filtrado.groupby("ITEM")["QTDE"]
            .sum()
            .reset_index()
            .sort_values("QTDE", ascending=False)
            .head(10)
        )
        
        fig_itens = px.bar(
            df_items_count,
            x="QTDE",
            y="ITEM",
            orientation="h",
            template="plotly_dark",
            labels={"ITEM": "Item", "QTDE": "Quantidade"},
        )
        fig_itens.update_layout(height=450)
        st.plotly_chart(fig_itens, use_container_width=True)
    else:
        st.info("Sem itens de doação para exibir.")

with c3:
    st.markdown("#### Pontuação de Impacto por Doação")
    if not df_impacto_filtrado.empty:
        df_imp = df_impacto_filtrado.copy()
        df_imp = df_imp.sort_values("ID_DOACAO")
        
        fig_imp = px.bar(
            df_imp,
            x="ID_DOACAO",
            y="PONTUACAO",
            template="plotly_dark",
            labels={"ID_DOACAO": "Id Doação", "PONTUACAO": "Pontuação"},
        )
        fig_imp.update_layout(height=450)
        st.plotly_chart(fig_imp, use_container_width=True)
    else:
        st.info("Sem dados de impacto para as doações filtradas.")

st.markdown("---")

# =========================================================
# HEATMAP – HORÁRIOS DE PICO
# =========================================================
st.subheader("🔥 Heatmap – Horários de Pico de Doações")

if not df_doacoes_filtrado.empty:
    df_heat = df_doacoes_filtrado.copy()
    df_heat = df_heat.dropna(subset=["DT_SOLICITACAO"])
    df_heat["HORA"] = df_heat["DT_SOLICITACAO"].dt.hour
    df_heat["DIA_SEMANA_IDX"] = df_heat["DT_SOLICITACAO"].dt.dayofweek
    
    mapa_dias = {
        0: "Segunda",
        1: "Terça",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sábado",
        6: "Domingo",
    }
    df_heat["DIA_SEMANA"] = df_heat["DIA_SEMANA_IDX"].map(mapa_dias)
    
    # Escala de cores personalizada para tema dark
    custom_colorscale = [
        [0.0, '#0a0a0a'],
        [0.2, '#1a1a2e'],
        [0.4, '#16213e'],
        [0.6, '#0f3460'],
        [0.8, '#1e5f8e'],
        [1.0, '#4a9eda']
    ]
    
    fig_heat = px.density_heatmap(
        df_heat,
        x="HORA",
        y="DIA_SEMANA",
        nbinsx=24,
        template="plotly_dark",
        labels={"HORA": "Hora do Dia", "DIA_SEMANA": "Dia da Semana"},
        color_continuous_scale=custom_colorscale,
    )
    fig_heat.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
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

st.markdown("---")
st.caption("Dashboard Helplink - FIAP 2025")

# =========================================================
# IA – CLASSIFICAÇÃO DE ESTADO DE CONSERVAÇÃO (Zero-Shot)
# =========================================================

import requests

# Token do Hugging Face vindo do secrets.toml
HF_TOKEN = st.secrets["HF_TOKEN"]

# Modelo de classificação de imagem
HF_MODEL = "google/vit-base-patch16-224"
API_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"


def classify_condition(image_bytes: bytes, mime_type: str = "image/png"):
    """
    Envia a imagem crua para o Hugging Face Inference Router
    usando Content-Type de imagem (image/png, image/jpeg, etc).

    Retorna:
        ("BOM" | "REGULAR" | "RUIM", score) em caso de sucesso
        (None, mensagem_erro) em caso de erro
    """

    # Garante um MIME válido, caso venha vazio
    if not mime_type:
        mime_type = "image/png"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": mime_type,
    }

    try:
        # Envia os bytes crus da imagem
        response = requests.post(API_URL, headers=headers, data=image_bytes)

        if response.status_code != 200:
            return None, f"Erro da IA: {response.text}"

        result = response.json()
        # Resposta esperada:
        # [ {"label": "alguma_coisa", "score": 0.98}, {...}, ... ]

        if not isinstance(result, list) or not result:
            return None, f"Resposta inesperada da IA: {result}"

        best = max(result, key=lambda x: x.get("score", 0))
        score = float(best.get("score", 0.0))

        # Regra simples pra condição:
        # > 0.75 = BOM
        # 0.45–0.75 = REGULAR
        # < 0.45 = RUIM
        if score >= 0.75:
            cond = "BOM"
        elif score >= 0.45:
            cond = "REGULAR"
        else:
            cond = "RUIM"

        return cond, score

    except Exception as e:
        return None, f"Erro ao chamar IA: {str(e)}"

# =========================================================
# INTERFACE STREAMLIT – IA
# =========================================================

st.markdown("## 🤖 IA – Análise do Estado de Conservação de Itens")
st.caption(
    "Envie uma imagem de um item e a IA irá classificar automaticamente como "
    "**BOM**, **REGULAR** ou **RUIM**."
)

uploaded = st.file_uploader(
    "Envie uma imagem para análise",
    type=["jpg", "jpeg", "png"]
)

if uploaded:
    # Mostrar imagem
    st.image(uploaded, use_container_width=True)  # se quiser depois troca por width="stretch"

    st.info("🔍 Analisando imagem com IA...")

    # Pega bytes e mime type correto (image/jpeg, image/png, etc)
    img_bytes = uploaded.getvalue()
    mime_type = uploaded.type  # Streamlit já manda certinho

    condicao, resultado = classify_condition(img_bytes, mime_type)

    if condicao is None:
        st.error(resultado)
    else:
        if condicao == "BOM":
            st.success(f"🟢 Estado de Conservação: **BOM** (confiança {resultado:.4f})")
        elif condicao == "REGULAR":
            st.warning(f"🟡 Estado de Conservação: **REGULAR** (confiança {resultado:.4f})")
        else:
            st.error(f"🔴 Estado de Conservação: **RUIM** (confiança {resultado:.4f})")

