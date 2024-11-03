import sqlite3
from itertools import chain
from pathlib import Path


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


def get_data_from_db(*fields, database="", sheet="", search_field="", value="", query="", dictionary=False, debug=False):
    """Ищет данные по указанным параметрам в базе данных.

    Если база данных не указана, совершает поиск по всем файлам баз данных
    в директории проекта. Возвращает кортеж найденных значений или None, если ничего не найдено.
    Если установлен флаг dictionary=True, возвращает словарь.

    Args:
        *fields (Union[str, Tuple[str]]): Поля, которые необходимо получить из базы данных.
        database (str): Имя базы данных для поиска. Если не указано, поиск идет по всем БД в директории проекта.
        sheet (str): Название таблицы для поиска.
        search_field (str): Поле для условия WHERE.
        value (str): Значение для поиска в поле search_field.
        query (str): Пользовательский SQL-запрос. Если указан, переопределяет `sheet`, `search_field` и `value`.
        dictionary (bool): Если True, возвращает данные в виде словаря.
        debug (bool): Если True, выводит отладочные сообщения и вызывает ошибки при отсутствии записей.
    Returns:
        tuple or dict or None: Кортеж значений, если запись найдена; словарь, если dictionary=True;
            или None, если запись не найдена.
    Raises:
        ValueError: Если количество полей и значений не совпадает при создании словаря.
        LookupError: Если запись не найдена и debug=True.
    """
    if not database:
        database = get_database_list()

    if isinstance(database, str):
        database = [database]

    for db in database:
        result = _lookup_data(*fields, query=query, database=db, sheet=sheet, search_field=search_field, value=value,
                              debug=debug)
        if dictionary and result:
            return tuple_to_dict(result, *fields)
        if result:
            return result
    return None


def _lookup_data(*fields, database="", sheet="", search_field="", value="", query="", debug=False):
    """Совершает поиск в базе данных с указанными параметрами.

    Выполняет SQL-запрос и возвращает кортеж найденных значений. Если запись не найдена
    и debug=True, вызывает ошибку LookupError.

    Args:
        *fields (str): Поля для выборки из базы данных.
        database (str): Имя базы данных для подключения.
        sheet (str): Название таблицы для поиска.
        search_field (str): Поле для условия WHERE.
        value (str): Значение для поиска в поле search_field.
        query (str): Пользовательский SQL-запрос. Если указан, переопределяет `sheet`, `search_field` и `value`.
        debug (bool): Если True, вызывает ошибку при отсутствии записей.
    Returns:
        tuple: Кортеж найденных значений.
    Raises:
        LookupError: Если запись не найдена и debug=True.
    """
    with sqlite3.connect(database) as con:
        cur = con.cursor()
        if not query:
            if isinstance(fields[0], tuple):
                flat_fields = list(chain.from_iterable(fields))
            else:
                flat_fields = list(fields)
            query = f"SELECT {', '.join(flat_fields)} FROM {sheet} WHERE {search_field} = ?"
        result = cur.execute(query, (value,)).fetchone()
        if result:
            return result
        if debug and not result:
            raise LookupError(f"Не найдены записи в таблице '{sheet}' по {search_field} = {value}")
        return ()


def get_database_list(debug=False):
    """Ищет файлы баз данных в директории проекта.

    Находит все файлы с расширением *.sqlite в директории проекта и возвращает их как список.
    Если файлы не найдены и debug=True, вызывает ошибку FileNotFoundError.

    Args:
        debug (bool): Если True, вызывает ошибку при отсутствии файлов баз данных.
    Returns:
        list: Список найденных файлов баз данных с расширением *.sqlite.
    Raises:
        FileNotFoundError: Если файлы баз данных не найдены и debug=True.
    """
    directory = Path(Path(__file__).parent)
    sqlite_files = list(directory.glob("*.sqlite"))
    if debug and not sqlite_files:
        raise FileNotFoundError("Не найдены файлы баз данных с расширением *.sqlite")
    return sqlite_files


def main():
    pass


if __name__ == "__main__":
    main()
