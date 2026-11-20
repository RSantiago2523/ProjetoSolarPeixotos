from django.db import connection


class ConsultaPaginada:
    """Para usar com o Paginator do Django: em vez de trazer todas as linhas para memória
    (cursor.fetchall()), só vai à BD buscar a página pedida.
    O SQL tem de terminar com ORDER BY (de preferência numa coluna única, para a ordem ser estável)."""

    def __init__(self, sql, params=None):
        self.sql = sql
        self.params = list(params or [])

    def __len__(self):
        # O ORDER BY final não é preciso para contar
        sql_sem_ordem = self.sql.rsplit('ORDER BY', 1)[0]
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM ({sql_sem_ordem}) AS q", self.params)
            return cursor.fetchone()[0]

    def __getitem__(self, fatia):
        with connection.cursor() as cursor:
            cursor.execute(f"{self.sql} LIMIT %s OFFSET %s", self.params + [fatia.stop - fatia.start, fatia.start])
            return cursor.fetchall()
