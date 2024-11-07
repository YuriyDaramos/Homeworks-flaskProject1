from flask import flash, redirect


def flash_and_redirect(field: str, message: str, route: str):
    """Отправляет сообщение об ошибке для указанного поля и перенаправляет на страницу регистрации."""
    flash({field: message})  # Сохраняем сообщение в словаре с ключом (названием) поля в HTML-шаблоне
    return redirect(route)


def main():
    pass


if __name__ == "__main__":
    main()
