from transliterate import translit
from random import randint


def generate_login(first_name, last_name,
                   db_name="db_flask1.sqlite", sheet="user", column="login"):
    """Генерирует логин пользователя из его имени и фамилии.

    Если такой логин не уникален, то добавит случайное число в конец.
    Args:
        first_name (str): имя пользователя.
        last_name (str): фамилия пользователя.
        db_name (str): название базы данных, должна находиться в одном расположении с модулем;
            Значение по умолчанию 'db_flask1.sqlite'.
        sheet (str): название таблицы с пользователями в базе данных; по умолчанию 'user'.
        column (str): название столбца с логинами в таблице базы данных; по умолчанию 'login'.
    Returns:
        str: Уникальный логин.
    """

    login = translit(first_name, 'ru', reversed=True) + "_" + translit(last_name, 'ru', reversed=True)

    with sqlite3.connect(db_name) as con:
        while True:
            query = f"SELECT COUNT(*) FROM {sheet} WHERE {column} LIKE ?"
            entry_counter = (
                con.cursor()
                .execute(query, (f"{login}%",))
                .fetchone()
            )
            if entry_counter[0] == 0:   # entry_counter - кортеж, fetchone() возвращает кортеж
                return login    # Значит логин уникален
            else:
                login = f"{login}{randint(entry_counter[0], entry_counter[0] + 64)}"   # Модификация логина


# Менеджер контекста (без понятия зачем мы это делали)
class DB_local:  # менеджер контекста (без понятия зачем мы это делали)
    def __init__(self, file_name):
        self.con = sqlite3.connect(file_name)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()

    def __enter__(self):  # Когда видит with, то срабатывает и возвращает результат в as ...
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()
        self.con.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
