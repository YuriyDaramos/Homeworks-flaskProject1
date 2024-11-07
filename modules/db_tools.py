import sqlite3


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def execute(self, query, query_args=None):
        if query_args is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, query_args)
        return self.cursor


def main():
    pass


if __name__ == "__main__":
    main()
