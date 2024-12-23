from flask import flash, redirect


def flash_and_redirect(field: str, message: str, route: str):
    """Отправляет сообщение об ошибке для указанного поля и перенаправляет по указанному маршруту."""
    flash({field: message})  # Сообщение в словаре с ключом (названием) поля в HTML-шаблоне
    return redirect(route)


def parse_price(price):
    return float(price) if price else None


def main():
    pass


if __name__ == "__main__":
    main()
