from modules.utils import flash_and_redirect
from modules.db_tools import get_data_from_db


def is_valid_email(email: str) -> bool:
    """Проверяет, содержит ли адрес электронной почты символ `@` и точку `.`,
    а также их взаимное корректное расположение.
    """
    # Проверяем наличие символа @ и точки
    if '@' in email and '.' in email:
        # Позиции символа @ и точки
        at_position = email.index('@')
        dot_position = email.rindex('.')

        # Проверяем, чтобы символ @ не был в начале или конце и чтобы точка была после символа @
        if at_position > 0 and at_position + 1 < dot_position < len(email) - 1:
            return True


def verify_and_get_user_id(database: str, identifier: str, password: str, sheet: str, search_field: str = ""):
    """Возвращает user_id из базы данных по логину или почте, если пароль указан верно.
    search_field может быть предварительно указан как 'email' или 'login'"""

    if not search_field:
        if is_valid_email(identifier) and password:
            search_field = "email"
        elif identifier and password:
            search_field = "login"
        else:
            return flash_and_redirect("form", "Заполните поля формы", "/login")

    # .execute("SELECT {', '.join(fields)} FROM {sheet} WHERE {search_field} = ?", (value,)).fetchone()
    result = get_data_from_db(("id", "password"), database=database, sheet=sheet,
                              search_field=search_field, value=identifier)
    if result and result[1] == password:
        return result[0]
    elif search_field == "email":
        return flash_and_redirect("identifier", "Неверно указан email", "/login")
    elif search_field == "login":
        return flash_and_redirect("identifier", "Неверно указан логин", "/login")


def main():
    pass


if __name__ == "__main__":
    main()
