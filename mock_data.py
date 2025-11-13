import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# ==========================
# USUÁRIOS
# ==========================
df_usuarios = pd.DataFrame({
    "ID_USUARIO": range(1, 19),
    "NOME": [f"Usuário {i}" for i in range(1, 19)],
    "SENHA": [f"hash{i}" for i in range(1, 19)],
    "DT_CADASTRO": [datetime(2025, 11, 10, 15, 0, 0)] * 18,
    "EMAIL": [f"user{i}@mail.com" for i in range(1, 19)],
    "TELEFONE": [f"119910{i:02d}" for i in range(1, 19)],
    "ID_ENDERECO": range(1, 19)
})

# ==========================
# INSTITUIÇÕES
# ==========================
df_instituicoes = pd.DataFrame({
    "ID_INSTITUICAO": range(1, 16),
    "NOME": [f"ONG {i}" for i in range(1, 16)],
    "EMAIL": [f"ong{i}@mail.com" for i in range(1, 16)],
    "TELEFONE": [f"11333344{i:02d}" for i in range(1, 16)],
    "ID_ENDERECO": range(1, 16),
    "CATEGORIAS_ACEITAS": ["Roupas, Alimentos"] * 15,
    "CNPJ": [f"00.000.000/000{i:02d}" for i in range(1, 16)]
})

# ==========================
# ITENS
# ==========================
df_itens = pd.DataFrame({
    "ID_ITEM": range(1, 15),
    "TITULO": [f"Item {i}" for i in range(1, 15)],
    "FOTO_URL": ["" for _ in range(1, 15)],
    "ESTADO_CONSERVACAO": ["NOVO"] * 14,
    "DT_REGISTRO": [datetime(2025, 11, 10, 12, 0, 0)] * 14,
    "DESCRICAO": ["Item para doação"] * 14,
    "ID_DOACAO": [np.nan] * 14,
    "ID_USUARIO": np.random.choice(range(1, 19), 14),
    "ID_CATEGORIA": np.random.choice(range(1, 6), 14),
})

# ==========================
# DOAÇÕES
# ==========================
datas = [
    datetime(2025, 11, 10, 15, 0),
    datetime(2025, 11, 11, 0, 0),
    datetime(2025, 11, 12, 1, 0)
] * 5

df_doacoes = pd.DataFrame({
    "ID_DOACAO": range(1, 16),
    "STATUS": ["CONCLUIDA", "AGENDADA", "ABERTA"] * 5,
    "DT_SOLICITACAO": datas[:15],
    "DT_CONFIRMACAO": [None] * 15,
    "ID_USUARIO": np.random.choice(range(1, 19), 15),
    "ID_INSTITUICAO": np.random.choice(range(1, 16), 15),
})

# ==========================
# DOAÇÃO-ITENS
# ==========================
df_doacao_itens = pd.DataFrame({
    "ID_DOACAO_ITEM": range(1, 16),
    "QTDE": np.random.randint(1, 3, 15),
    "ID_DOACAO": np.random.choice(range(1, 16), 15),
    "ITEM": np.random.choice(df_itens["TITULO"], 15)
})

# ==========================
# IMPACTO
# ==========================
df_impacto = pd.DataFrame({
    "ID_IMPACTO": range(1, 16),
    "ID_DOACAO": range(1, 16),
    "PONTUACAO": np.random.choice([10, 15], 15),
    "OBSERVACAO": [""] * 15
})
