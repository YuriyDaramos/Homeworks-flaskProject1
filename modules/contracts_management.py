from modules.data_management import DataManager
from modules.db_tools import DatabaseManager


class ContractsManager(DataManager):
    def __init__(self, database):
        self.database = database

    def get_rental_items_data(self, participant):
        query = f"SELECT {participant}, COUNT(item_id) AS rental_items FROM contracts GROUP BY {participant}"
        with DatabaseManager(self.database) as db:
            return db.execute(query).fetchall()

    def get_contracts_data(self, fields=None, size=None):
        if fields:
            fields = self.normalize_fields(fields)
        query = f"SELECT {fields} FROM contracts"
        with DatabaseManager(self.database) as db:
            if size:
                contracts_data = db.execute(query).fetchmany(size)
            else:
                contracts_data = db.execute(query).fetchall()

        return contracts_data

    def get_contract_data(self, item_id, fields=None):
        """Получает данные о контракте по ID товара.

        Args:
            item_id (int): ID товара.
            fields (str или tuple, optional): Поля, которые нужно получить. Если None, будут получены все поля.
        Returns:
            sqlite3.Row: Данные по контракту или None, если данные отсутствуют.
        """
        fields = self.normalize_fields(fields)
        query = f"SELECT {fields} FROM contracts WHERE item_id = ?"
        with DatabaseManager(self.database) as db:
            contract_data = db.execute(query, (item_id,)).fetchone()

        return contract_data


def main():
    pass


if __name__ == "__main__":
    main()
