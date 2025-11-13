import pandas as pd
import numpy as np

# ================ MOCK DATA =================

usuarios = pd.DataFrame({
    "ID_USUARIO": range(1, 11),
    "NOME": [f"Usuário {i}" for i in range(1, 11)],
    "EMAIL": [f"user{i}@email.com" for i in range(1, 11)],
})

instituicoes = pd.DataFrame({
    "ID_INSTITUICAO": range(1, 6),
    "NOME": ["Cruz Vermelha", "Lar Solidário", "Amigos do Bem", "Vida Nova", "Ajuda Brasil"],
})

itens = pd.DataFrame({
    "ID_ITEM": range(1, 11),
    "TITULO": ["Roupa", "Cobertor", "Alimento", "Brinquedo", "Sapato",
               "Livro", "Mochila", "Toalha", "Casaco", "Material Escolar"],
    "DT_REGISTRO": pd.date_range(start="2025-01-01", periods=10)
})

doacoes = pd.DataFrame({
    "ID_DOACAO": range(1, 11),
    "STATUS": ["CONCLUIDA", "ABERTA", "CONCLUIDA", "ABERTA", "ABERTA",
               "CONCLUIDA", "ABERTA", "CONCLUIDA", "ABERTA", "ABERTA"],
    "DT_SOLICITACAO": pd.date_range("2025-01-05", periods=10, freq="2D"),
    "ID_USUARIO": np.random.randint(1, 10, 10),
    "ID_INSTITUICAO": np.random.randint(1, 5, 10),
})

doacao_itens = pd.DataFrame({
    "ID_DOACAO": np.random.randint(1, 10, 25),
    "ITEM": np.random.choice(itens["TITULO"], 25),
    "QTDE": np.random.randint(1, 5, 25),
})

impacto = pd.DataFrame({
    "ID_IMPACTO": range(1, 11),
    "ID_DOACAO": range(1, 11),
    "PONTUACAO": np.random.randint(5, 15, 10),
    "OBSERVACAO": ["Impacto positivo"] * 10
})
