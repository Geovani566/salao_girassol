from pathlib import Path
import sqlite3


#essa parte vai ficar responsável por criar a conexão com o banco de dados
#e criar as tabelas necessárias
DB_NAME = Path(__file__).with_name('agendamentos.db')

def fazer_conexao():
    conexao = sqlite3.connect(DB_NAME)
    return conexao 


def tabela_servico():
    conexao = fazer_conexao()
    cursor = conexao.cursor()
    cursor.execute('''
CREATE TABLE IF NOT EXISTS servicos (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT NOT NULL,
descricao TEXT NOT NULL DEFAULT '',
cor TEXT NOT NULL DEFAULT '#C97B58',
duracao INTEGER NOT NULL,
preco REAL NOT NULL
)
''')
    conexao.commit()
    conexao.close()

def garantir_colunas_servicos():
    conexao = fazer_conexao()
    cursor = conexao.cursor()
    cursor.execute("PRAGMA table_info(servicos)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]

    if "descricao" not in colunas:
        cursor.execute("ALTER TABLE servicos ADD COLUMN descricao TEXT NOT NULL DEFAULT ''")
        conexao.commit()

    if "cor" not in colunas:
        cursor.execute("ALTER TABLE servicos ADD COLUMN cor TEXT NOT NULL DEFAULT '#C97B58'")
        conexao.commit()

    conexao.close()

def popular_servicos_iniciais():
    conexao = fazer_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) FROM servicos")
    total = cursor.fetchone()[0]

    if total == 0:
        cursor.executemany(
            """
            INSERT INTO servicos(nome, descricao, cor, duracao, preco)
            VALUES(?,?,?,?,?)
            """,
            [
                ("Alongamento", "Tecnica para realcar o olhar com acabamento natural.", "#C97B58", 120, 120.00),
                ("Manicure", "Cuidado completo para as unhas das maos.", "#94A584", 60, 45.00),
                ("Pedicure", "Cuidado completo para os pes e acabamento delicado.", "#4F2F3D", 60, 50.00),
            ],
        )
        conexao.commit()
    else:
        servicos_padrao = [
            ("Tecnica para realcar o olhar com acabamento natural.", "#C97B58", "Alongamento"),
            ("Cuidado completo para as unhas das maos.", "#94A584", "Manicure"),
            ("Cuidado completo para os pes e acabamento delicado.", "#4F2F3D", "Pedicure"),
        ]
        cursor.executemany(
            """
            UPDATE servicos
            SET
                descricao = CASE WHEN descricao = '' THEN ? ELSE descricao END,
                cor = CASE WHEN cor = '' OR cor = '#C97B58' THEN ? ELSE cor END
            WHERE nome = ?
            """,
            servicos_padrao,
        )
        conexao.commit()

    conexao.close()

def tabela_agendamento():
    conexao = fazer_conexao()
    cursor = conexao.cursor()

    cursor.execute('''
    
        CREATE TABLE IF NOT EXISTS agendamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            servico TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL
        )
    ''')

    conexao.commit()
    conexao.close()

def tabela_horarios_trabalho():
    conexao = fazer_conexao()
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS horarios_trabalho (
            dia_semana INTEGER PRIMARY KEY,
            ativo INTEGER NOT NULL DEFAULT 1,
            hora_inicio TEXT NOT NULL DEFAULT '09:00',
            hora_fim TEXT NOT NULL DEFAULT '19:00',
            intervalo INTEGER NOT NULL DEFAULT 30
        )
    ''')
    conexao.commit()
    conexao.close()

def popular_horarios_trabalho():
    conexao = fazer_conexao()
    cursor = conexao.cursor()
    horarios_padrao = [
        (0, 0, "09:00", "19:00", 30),
        (1, 1, "09:00", "19:00", 30),
        (2, 1, "09:00", "19:00", 30),
        (3, 1, "09:00", "19:00", 30),
        (4, 1, "09:00", "19:00", 30),
        (5, 1, "09:00", "19:00", 30),
        (6, 1, "09:00", "19:00", 30),
    ]
    cursor.executemany(
        """
        INSERT OR IGNORE INTO horarios_trabalho(dia_semana, ativo, hora_inicio, hora_fim, intervalo)
        VALUES(?,?,?,?,?)
        """,
        horarios_padrao,
    )
    conexao.commit()
    conexao.close()

def inicializar_banco():
    tabela_servico()
    garantir_colunas_servicos()
    tabela_agendamento()
    tabela_horarios_trabalho()
    popular_servicos_iniciais()
    popular_horarios_trabalho()

if __name__=="__main__":
    inicializar_banco()

