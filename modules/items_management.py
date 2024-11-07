import sqlite3

from modules.data_management import DataManager
from modules.db_tools import DatabaseManager


class ItemManager(DataManager):
    def __init__(self, database):
        self.database = database

    def get_items_data(self, fields=None, size=None):
        if fields:
            fields = self.normalize_fields(fields)
        query = f"SELECT {fields} FROM items"
        with DatabaseManager(self.database) as db:
            if size:
                item_data = db.execute(query).fetchmany(size)
            else:
                item_data = db.execute(query).fetchall()

        return item_data

    def get_item_data(self, item_id, fields=None):
        """Получает данные пользователя по ID.

        Args:
            item_id (int): ID товара.
            fields (str или tuple, optional): Поля, которые нужно получить. Если None, будут получены все поля.
        Returns:
            sqlite3.Row: Данные товара или None, если товар не найден.
        """
        if fields:
            fields = self.normalize_fields(fields)
        query = f"SELECT {fields} FROM items WHERE id = ?"
        with DatabaseManager(self.database) as db:
            item_data = db.execute(query, (item_id,)).fetchone()

        return item_data

    def register_new_item(self, request_form, owner_id):
        with DatabaseManager(self.database) as db:
            query = f"""INSERT INTO items (name, photo, desc, price_h, price_d, price_w, price_m, owner_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

            name, photo, desc, price_h, price_d, price_w, price_m = (
                request_form.get("name"),
                request_form.get("photo"),
                request_form.get("desc"),
                request_form.get("price_h"),
                request_form.get("price_d"),
                request_form.get("price_m"),
                request_form.get("price_m"),

            )

            new_item_data = name, photo, desc, price_h, price_d, price_w, price_m, owner_id

            register_result = db.execute(query, new_item_data)
            if not register_result:
                return {"success": False, "template": "form",
                        "message": "Не удалось провести добавление, повторите позже"}

            return {"success": True, "item_id": register_result.lastrowid}
