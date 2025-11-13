import oracledb
import pandas as pd
import streamlit as st

class HelpLinkDB:
    def __init__(self):
        # carrega credenciais do .streamlit/secrets.toml
        secrets = st.secrets["oracle"]

        self.username = secrets["USER"]
        self.password = secrets["PASSWORD"]
        self.dsn = secrets["DSN"]

    def connect(self):
        return oracledb.connect(
            user=self.username,
            password=self.password,
            dsn=self.dsn
        )

    # Função genérica
    def query(self, sql, params=None):
        try:
            with self.connect() as conn:
                df = pd.read_sql(sql, conn, params=params)
            return df
        except Exception as e:
            st.error(f"Erro ao consultar o banco: {e}")
            return pd.DataFrame()

    # ============================
    # TABELAS DO HELPLINK
    # ============================

    def get_usuarios(self):
        return self.query("SELECT * FROM TB_HELPLINK_USUARIO")

    def get_instituicoes(self):
        return self.query("SELECT * FROM TB_HELPLINK_INSTITUICAO")

    def get_categorias(self):
        return self.query("SELECT * FROM TB_HELPLINK_CATEGORIA")

    def get_itens(self):
        return self.query("SELECT * FROM TB_HELPLINK_ITEM")

    def get_doacoes(self):
        return self.query("""
            SELECT 
                d.ID_DOACAO,
                d.STATUS,
                d.DT_SOLICITACAO,
                d.DT_CONFIRMACAO,
                u.NOME AS USUARIO,
                i.NOME AS INSTITUICAO
            FROM TB_HELPLINK_DOACAO d
            JOIN TB_HELPLINK_USUARIO u ON u.ID_USUARIO = d.ID_USUARIO
            JOIN TB_HELPLINK_INSTITUICAO i ON i.ID_INSTITUICAO = d.ID_INSTITUICAO
            ORDER BY d.ID_DOACAO DESC
        """)

    def get_doacao_itens(self):
        return self.query("""
            SELECT 
                di.ID_DOACAO_ITEM,
                di.QTDE,
                d.ID_DOACAO,
                it.NOME AS ITEM
            FROM TB_HELPLINK_DOACAO_ITEM di
            JOIN TB_HELPLINK_DOACAO d ON d.ID_DOACAO = di.ID_DOACAO
            JOIN TB_HELPLINK_ITEM it ON it.ID_ITEM = di.ID_ITEM
        """)

    def get_impactos(self):
        return self.query("""
            SELECT 
                im.ID_IMPACTO,
                im.PONTUACAO,
                im.OBSERVACAO,
                d.ID_DOACAO
            FROM TB_HELPLINK_IMPACTO im
            JOIN TB_HELPLINK_DOACAO d ON d.ID_DOACAO = im.ID_DOACAO
        """)
