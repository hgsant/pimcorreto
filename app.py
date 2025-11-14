# ======================================================================
#   AcadIA – Sistema Acadêmico Inteligente (Versão para Streamlit)
#   Conversão completa do seu código Tkinter → Aplicação Web
#   Login padrão: admin / 123
# ======================================================================

import streamlit as st
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor

def conectar():
    return sqlite3.connect("acadIA.db", check_same_thread=False)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            turma TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER,
            n1 REAL,
            n2 REAL,
            n3 REAL,
            media REAL,
            FOREIGN KEY(aluno_id) REFERENCES alunos(id)
        );
    """)

    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                       ("admin", "123"))
    except:
        pass

    conn.commit()

inicializar_banco()

def validar_login(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
    return cursor.fetchone() is not None

def cadastrar_aluno(nome, turma):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alunos (nome, turma) VALUES (?, ?)",
                   (nome, turma))
    conn.commit()

def listar_alunos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alunos")
    return cursor.fetchall()

def salvar_notas(aluno_id, n1, n2, n3, media):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notas (aluno_id, n1, n2, n3, media) VALUES (?, ?, ?, ?, ?)",
        (aluno_id, n1, n2, n3, media)
    )
    conn.commit()

def listar_notas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT alunos.nome, notas.n1, notas.n2, notas.n3, notas.media
        FROM notas
        JOIN alunos ON alunos.id = notas.aluno_id
    """)
    return cursor.fetchall()

def treinar_ia():
    X = np.array([
        [5,6,7],[7,8,9],[3,4,5],[9,9,10],
        [6,6,7],[8,7,6],[4,5,6],[2,3,4]
    ])
    y = np.array([6.0,8.0,4.0,9.3,6.3,7.0,5.0,3.0])

    reg = LinearRegression()
    reg.fit(X, y)

    nn = MLPRegressor(hidden_layer_sizes=(10,10), max_iter=1000)
    nn.fit(X, y)

    return reg, nn

regressor, rede_neural = treinar_ia()

def prever_media(n1, n2, n3):
    entrada = np.array([[n1, n2, n3]])
    p1 = regressor.predict(entrada)[0]
    p2 = rede_neural.predict(entrada)[0]
    return (p1 + p2) / 2

st.set_page_config(page_title="AcadIA", layout="centered")

if "logado" not in st.session_state:
    st.session_state.logado = False

def tela_login():
    st.title("🔐 AcadIA – Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if validar_login(usuario, senha):
            st.session_state.logado = True
            st.success("Login realizado!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")

def cadastrar_aluno_ui():
    st.header("📘 Cadastrar Aluno")

    nome = st.text_input("Nome")
    turma = st.text_input("Turma")

    if st.button("Salvar"):
        if nome == "" or turma == "":
            st.error("Preencha todos os campos.")
        else:
            cadastrar_aluno(nome, turma)
            st.success("Aluno cadastrado!")

def lancar_notas_ui():
    st.header("🧮 Lançar Notas + IA")

    alunos = listar_alunos()
    lista = {f"{a[1]} ({a[2]})": a[0] for a in alunos}

    escolha = st.selectbox("Selecione o aluno:", list(lista.keys()))
    aluno_id = lista[escolha]

    n1 = st.number_input("Nota 1", 0.0, 10.0)
    n2 = st.number_input("Nota 2", 0.0, 10.0)
    n3 = st.number_input("Nota 3", 0.0, 10.0)

    if st.button("Calcular Média + IA"):
        media = prever_media(n1, n2, n3)
        salvar_notas(aluno_id, n1, n2, n3, media)
        st.success(f"Média prevista pela IA: **{media:.2f}**")

def dashboard_ui():
    st.header("📊 Dashboard AcadIA")

    dados = listar_notas()
    if not dados:
        st.warning("Nenhum dado encontrado!")
        return

    st.subheader("Tabela de notas")
    st.table(dados)

    medias = [d[4] for d in dados]

    aprovados = sum(1 for m in medias if m >= 6)
    reprovados = len(medias) - aprovados

    st.subheader("Resumo")
    st.write(f"✔ Aprovados: **{aprovados}**")
    st.write(f"❌ Reprovados: **{reprovados}**")
    st.write(f"🔥 Maior Média: **{max(medias):.2f}**")
    st.write(f"🧊 Menor Média: **{min(medias):.2f}**")

    st.subheader("Gráfico de Médias")
    fig, ax = plt.subplots()
    ax.bar([d[0] for d in dados], medias)
    st.pyplot(fig)

    st.subheader("Gráfico Pizza")
    fig2, ax2 = plt.subplots()
    ax2.pie([aprovados, reprovados], labels=["Aprovados", "Reprovados"], autopct="%1.1f%%")
    st.pyplot(fig2)

if not st.session_state.logado:
    tela_login()
else:
    st.sidebar.title("📌 Menu")
    opcao = st.sidebar.radio("Escolha:", [
        "Cadastrar Aluno",
        "Lançar Notas + IA",
        "Dashboard"
    ])

    if opcao == "Cadastrar Aluno":
        cadastrar_aluno_ui()
    elif opcao == "Lançar Notas + IA":
        lancar_notas_ui()
    elif opcao == "Dashboard":
        dashboard_ui()
