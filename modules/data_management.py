class DataManager:
    @staticmethod
    def check_fields_type(fields):
        if fields is None:
            return "*"
        elif isinstance(fields, str):
            return fields
        elif isinstance(fields, tuple):
            return ", ".join(fields)
        else:
            raise ValueError("fields должен быть строкой, кортежем или None.")

    @staticmethod
    def normalize_fields(fields):
        if fields is None:
            return "*"
        elif isinstance(fields, str):
            return fields
        elif isinstance(fields, tuple):
            return ", ".join(fields)
        else:
            raise ValueError("fields должен быть строкой, кортежем или None.")
