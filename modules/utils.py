from flask import flash, redirect


def get_user_name(database_name, user_id):
    # Тут должен быть запрос к базе данных
    if not database_name:
        database_name = "db_flask1.sqlite"
    query = ""
    user = database_name.session.query(User).filter_by(id=user_id).first()
    return user.name if user else None


def is_valid_password(password: str) -> bool:
    """В данный момент только проверка, что пароль не пустой."""
    return bool(password)


def flash_and_redirect(field: str, message: str, route: str):
    """Отправляет сообщение об ошибке для указанного поля и перенаправляет на страницу регистрации."""
    flash({field: message})  # Сохраняем сообщение в словаре с ключом (названием) поля в HTML-шаблоне
    return redirect(route)


def get_database_name(database_name):
    if not database_name:
        return "db_flask1.sqlite"
    return database_name


def get_user_id(cur, password, contact_email="", user_login=""):
    if contact_email:
        if cur.execute("SELECT COUNT(*) FROM user WHERE contact_email = ?", (contact_email,)).fetchone()[0]:
            return get_user_id_with_pass(cur, password, contact_email=contact_email)

    if user_login:
        if cur.execute("SELECT COUNT(*) FROM user WHERE login = ?", (user_login,)).fetchone()[0]:
            return get_user_id_with_pass(cur, password, user_login=user_login)


def get_user_id_with_pass(cur, password, user_login="", contact_email=""):
    """Получает ID пользователя по его логину или адресу электронной почты и проверяет пароль.

    Функция ищет пользователя по логину или адресу электронной почты, проверяя, что переданный пароль
    соответствует хранимому в базе данных. При совпадении пароля возвращается ID пользователя.

    Args:
        cur (sqlite3.Cursor): Курсор для выполнения SQL-запросов.
        password (str): Пароль, введенный пользователем для проверки.
        user_login (str, optional): Логин пользователя. Используется, если передан.
        contact_email (str, optional): Электронная почта пользователя. Используется, если передана.
    Returns:
        int: ID пользователя, если пользователь найден и пароль совпадает.
        None: Если пользователь не найден или пароль не совпадает
    """
    result = None  # Инициализация result для предотвращения ошибки неопределенной переменной
    if user_login:
        result = cur.execute("SELECT id, password FROM user WHERE login = ?", (user_login,)).fetchone()
    elif contact_email:
        result = cur.execute("SELECT id, password FROM user WHERE contact_email = ?", (contact_email,)).fetchone()

    # Проверка, что пользователь найден и пароль совпадает
    if result and (result[1] == password):
        return result[0]  # Возвращает id пользователя


def main():
    pass


if __name__ == "__main__":
    main()
