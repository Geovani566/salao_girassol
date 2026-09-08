# aqui eu vou fazer o crud do agendamento.
from datetime import datetime

from database import fazer_conexao


def _time_to_minutes(value):
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def _minutes_to_time(value):
    return f"{value // 60:02d}:{value % 60:02d}"


def _date_to_weekday_index(value):
    parsed = datetime.strptime(value, "%Y-%m-%d").date()
    return (parsed.weekday() + 1) % 7


class CrudApi:
    def __init__(self):
        pass

    @staticmethod
    def criar_agendamento(nome, servico, telefone, data, hora):
        if not CrudApi.horario_esta_disponivel(data, servico, hora):
            raise ValueError("Horario indisponivel para este servico")

        conexao = fazer_conexao()
        try:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO agendamento(nome,servico,telefone,data,hora)
                VALUES(?,?,?,?,?)
            """, (nome, servico, telefone, data, hora))
            conexao.commit()
        finally:
            conexao.close()

    @staticmethod
    def listar_agendamentos():
        conexao = fazer_conexao()
        try:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, nome, telefone, servico, data, hora
                FROM agendamento
                ORDER BY data, hora
            """)
            return [
                {
                    "id": row[0],
                    "nome": row[1],
                    "telefone": row[2],
                    "servico": row[3],
                    "data": row[4],
                    "hora": row[5],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conexao.close()

    @staticmethod
    def buscar_agendamento(id):
        conexao = fazer_conexao()
        try:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, nome, telefone, servico, data, hora
                FROM agendamento
                WHERE id = ?
            """, (id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return {
                "id": row[0],
                "nome": row[1],
                "telefone": row[2],
                "servico": row[3],
                "data": row[4],
                "hora": row[5],
            }
        finally:
            conexao.close()

    @staticmethod
    def deletar_agendamento(id):
        conexao = fazer_conexao()
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM agendamento WHERE id = ?", (id,))
            conexao.commit()
        finally:
            conexao.close()

    @staticmethod
    def editar_agendamento(_id, _nome):
        conexao = fazer_conexao()
        try:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE agendamento
                SET nome = ?
                WHERE id = ?
            """, (_nome, _id))
            conexao.commit()
        finally:
            conexao.close()
        return {"status": "Agendamento atualizado com sucesso!"}

    @staticmethod
    def mostrar_servicos():
        conn = fazer_conexao()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, descricao, cor, duracao, preco FROM servicos")
            servicos = cursor.fetchall()
            return [
                {
                    "id": servico[0],
                    "nome": servico[1],
                    "descricao": servico[2],
                    "cor": servico[3],
                    "duracao": servico[4],
                    "preco": servico[5],
                }
                for servico in servicos
            ]
        finally:
            conn.close()

    @staticmethod
    def criar_servico(nome, descricao, cor, duracao, preco):
        conn = fazer_conexao()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO servicos(nome,descricao,cor,duracao,preco)
                VALUES(?,?,?,?,?)
            """, (nome, descricao, cor, duracao, preco))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def listar_horarios_trabalho():
        conn = fazer_conexao()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dia_semana, ativo, hora_inicio, hora_fim, intervalo
                FROM horarios_trabalho
                ORDER BY dia_semana
            """)
            return [
                {
                    "dia_semana": row[0],
                    "ativo": bool(row[1]),
                    "hora_inicio": row[2],
                    "hora_fim": row[3],
                    "intervalo": row[4],
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    @staticmethod
    def salvar_horarios_trabalho(horarios):
        conn = fazer_conexao()
        try:
            cursor = conn.cursor()
            for horario in horarios:
                cursor.execute("""
                    INSERT INTO horarios_trabalho(dia_semana, ativo, hora_inicio, hora_fim, intervalo)
                    VALUES(?,?,?,?,?)
                    ON CONFLICT(dia_semana) DO UPDATE SET
                        ativo = excluded.ativo,
                        hora_inicio = excluded.hora_inicio,
                        hora_fim = excluded.hora_fim,
                        intervalo = excluded.intervalo
                """, (
                    horario["dia_semana"],
                    int(horario["ativo"]),
                    horario["hora_inicio"],
                    horario["hora_fim"],
                    horario["intervalo"],
                ))
            conn.commit()
            return CrudApi.listar_horarios_trabalho()
        finally:
            conn.close()

    @staticmethod
    def buscar_duracao_servico(servico):
        conn = fazer_conexao()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT duracao FROM servicos WHERE nome = ?", (servico,))
            row = cursor.fetchone()
            return int(row[0]) if row else None
        finally:
            conn.close()

    @staticmethod
    def listar_horarios_disponiveis(data, servico):
        duracao = CrudApi.buscar_duracao_servico(servico)
        if duracao is None:
            return []

        dia_semana = _date_to_weekday_index(data)
        conn = fazer_conexao()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ativo, hora_inicio, hora_fim, intervalo
                FROM horarios_trabalho
                WHERE dia_semana = ?
            """, (dia_semana,))
            regra = cursor.fetchone()
            if regra is None or not regra[0]:
                return []

            inicio = _time_to_minutes(regra[1])
            fim = _time_to_minutes(regra[2])
            intervalo = int(regra[3])
            if intervalo <= 0 or inicio >= fim or inicio + duracao > fim:
                return []

            cursor.execute("""
                SELECT a.hora, COALESCE(s.duracao, 30)
                FROM agendamento a
                LEFT JOIN servicos s ON s.nome = a.servico
                WHERE a.data = ?
            """, (data,))
            ocupados = [
                (_time_to_minutes(row[0]), _time_to_minutes(row[0]) + int(row[1]))
                for row in cursor.fetchall()
            ]

            horarios = []
            candidato = inicio
            while candidato + duracao <= fim:
                candidato_fim = candidato + duracao
                tem_colisao = any(
                    candidato < ocupado_fim and candidato_fim > ocupado_inicio
                    for ocupado_inicio, ocupado_fim in ocupados
                )
                if not tem_colisao:
                    horarios.append(_minutes_to_time(candidato))
                candidato += intervalo

            return horarios
        finally:
            conn.close()

    @staticmethod
    def horario_esta_disponivel(data, servico, hora):
        return hora in CrudApi.listar_horarios_disponiveis(data, servico)
