import sqlite3

from datetime import datetime

from modules.data_management import DataManager
from modules.db_tools import DatabaseManager


class UserManager(DataManager):
    def __init__(self, database):
        self.database = database

    @staticmethod
    def is_email(email):
        if '@' in email and '.' in email:
            at_position = email.index('@')
            dot_position = email.rindex('.')

            if at_position > 0 and at_position + 1 < dot_position < len(email) - 1:
                return True

    def get_users_data(self, fields=None, size=None):
        if fields:
            fields = self.normalize_fields(fields)
        query = f"SELECT {fields} FROM users"
        with DatabaseManager(self.database) as db:
            if size:
                user_data = db.execute(query).fetchmany(size)
            else:
                user_data = db.execute(query).fetchall()

        return user_data

    def get_user_data(self, user_id, fields=None):
        """Получает данные пользователя по ID.

        Args:
            user_id (int): ID пользователя.
            fields (str или tuple, optional): Поля, которые нужно получить. Если None, будут получены все поля.
        Returns:
            sqlite3.Row: Данные пользователя или None, если пользователь не найден.
        """
        if fields:
            fields = self.normalize_fields(fields)
        query = f"SELECT {fields} FROM users WHERE id = ?"
        with DatabaseManager(self.database) as db:
            user_data = db.execute(query, (user_id,)).fetchone()

        return user_data

    def verify_user(self, request_form):
        if self.is_email(request_form["identifier"]):
            query = f"SELECT id FROM users WHERE email = ? and password = ?"
        else:
            query = f"SELECT id FROM users WHERE login = ? and password = ?"

        with DatabaseManager(self.database) as db:
            user_id = db.execute(query, (request_form["identifier"], request_form["password"])).fetchone()

        if user_id is not None:
            return user_id["id"]
        return None

    def register_new_user(self, request_form):
        if not self.is_email(request_form["email"]):
            return {"success": False, "template": "email", "message": "Неверный формат почты"}

        with DatabaseManager(self.database) as db:
            query = f"SELECT COUNT(*) FROM users WHERE email = ?"
            email_entries = db.execute(query, (request_form["email"],)).fetchone()[0]

            if email_entries:
                return {"success": False, "template": "email", "message": "Такой почтовый адрес уже используется"}

            query = f"SELECT COUNT(*) FROM users WHERE login = ?"
            login_entries = db.execute(query, (request_form["user_login"],)).fetchone()[0]
            print(login_entries)

            if login_entries:
                return {"success": False, "template": "login", "message": "Такой логин уже существует"}

            query = f"""INSERT INTO users (login, password, first_name, last_name, email, register_date)
            VALUES (?, ?, ?, ?, ?, ?)"""
            login, password, first_name, last_name, email = (
                request_form.get("user_login"),
                request_form.get("password"),
                request_form.get("first_name"),
                request_form.get("last_name", ),
                request_form.get("email")
            )
            register_date = datetime.now().strftime("%d-%m-%Y")
            user_data = login, password, first_name, last_name, email, register_date
            register_result = db.execute(query, user_data)
            if not register_result:
                return {"success": False, "template": "form",
                        "message": "Не удалось провести регистрацию, повторите позже"}

            return {"success": True, "user_id": register_result.lastrowid}

    # def update_user_data(self, user_id, new_data):
    #     with DatabaseManager(self.database) as db:
    #         db.execute("UPDATE users SET login = ?, email = ? WHERE id = ?",
    #                    (new_data['login'], new_data['email'], user_id))


def main():
    pass


if __name__ == "__main__":
    main()
