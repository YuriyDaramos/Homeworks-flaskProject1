from flask import flash, redirect


def tuple_to_dict(values_tuple, *keys, **kwkeys):
    """Генерирует словарь из кортежа значений и ключей.

    Если требуется изменить какое-либо значение перед упаковкой в словарь, его можно указать как именованный аргумент.
    Функция предназначена для использования с запросами SQL и Flask, где кортеж значений получен из SQL-запроса,
    а словарь необходим для render_template.

    Args:
        values_tuple (tuple): кортеж значений, полученный из SQL-запроса.
        *keys (str): Неограниченное количество ключей для словаря.
        **kwkeys (dict): Неограниченное количество пар ключ-значение для изменения значений в конечном словаре.
    Returns:
        dict: Словарь, где *keys являются ключами, а значения из values_tuple являются значениями.
        Если были переданы именованные аргументы, они заменят значения по соответствующим ключам.
    Raises:
        ValueError: Если количество полученных значений и ключей не совпадает.
    """

    dictionary = {}
    if len(values_tuple) != len(keys):
        raise ValueError("Количество значений и ключей не совпадает")

    for key, value in zip(keys, values_tuple):
        dictionary[key] = value

    if kwkeys:
        for key in kwkeys:
            if key in dictionary:
                dictionary[key] = kwkeys[key]

    return dictionary


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


def is_valid_password(password: str) -> bool:
    """В данный момент только проверка, что пароль не пустой."""
    return bool(password)


def flash_and_redirect(field: str, message: str, route: str):
    """Отправляет сообщение об ошибке для указанного поля и перенаправляет на страницу регистрации."""
    flash({field: message})  # Сохраняем сообщение в словаре с ключом (названием) поля в HTML-шаблоне
    return redirect(route)


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
