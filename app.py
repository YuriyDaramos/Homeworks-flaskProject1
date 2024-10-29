from datetime import date
from random import randint
from flask import Flask, render_template, url_for, session, g, request
import sqlite3
from utils import *

# Инициализация Flask
app = Flask(__name__)
app.secret_key = "12345"

# Список маршрутов, где сайдбар не отображается
exclude_sidebar_routes = ["index", "logout"]  # ! Указать имена _функций_ маршрутов

database_name = "db_flask1.sqlite"


# Этот декоратор регистрирует функцию, которая будет вызвана перед обработкой каждого запроса
@app.before_request
def before_request():
    # Получение имени запрошенного маршрута
    endpoint = request.endpoint
    g.show_sidebar = endpoint not in exclude_sidebar_routes


# Пример регистрации ресурса (корневой URL в данном случае)
@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html", show_sidebar=False)    # Рендер страницы index.html


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("profile_me"))
        return render_template("login.html")
    if request.method == "POST":
        # Рассовывание данных из формы по соответствующим переменным
        login_or_email, password = (
            request.form.get("login_or_email"),
            request.form.get("password")
        )

        with sqlite3.connect(database_name) as con:
            cur = con.cursor()
            # Проверка почты
            if is_valid_email(login_or_email):
                if cur.execute("SELECT COUNT(*) FROM user WHERE contact_email = ?", (login_or_email,)).fetchone()[0]:
                    user_id = get_user_id_with_pass(cur, password, contact_email=login_or_email)
                    if user_id:
                        session["user_id"] = user_id
                        return redirect(url_for("profile_me"))
                    else:
                        return flash_and_redirect("password", "Неверный пароль", "/login")
                else:
                    return flash_and_redirect("email", "Неверно указан email", "/login")

            # Проверка логина
            else:
                if cur.execute("SELECT COUNT(*) FROM user WHERE login = ?", (login_or_email,)).fetchone()[0]:
                    user_id = get_user_id_with_pass(cur, password, user_login=login_or_email)
                    if user_id:
                        session["user_id"] = user_id
                        return redirect(url_for("profile_me"))
                    else:
                        return flash_and_redirect("password", "Неверный пароль", "/login")
                else:
                    return flash_and_redirect("password", "Неверно указан логин", "/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Обрабатывает регистрацию пользователей.

    Данная функция связана с маршрутом "/register" и обрабатывает запросы GET и POST.
    - При получении запроса GET возвращает страницу регистрации `register.html`.
    - При получении запроса POST извлекает данные из формы и выполняет их проверку на валидность.
        - Если пароль пустой, возвращает сообщение об ошибке.
        - Если формат адреса электронной почты некорректный, возвращает сообщение об ошибке.
        - Проверяет уникальность адреса электронной почты и логина в базе данных.
            - Если адрес электронной почты уже используется, возвращает сообщение об ошибке.
            - Если логин уже существует, возвращает сообщение об ошибке.
        - Если все проверки пройдены, регистрирует пользователя, сохраняет дату регистрации и ID пользователя в сессии.

    Returns:
        Response: При успешной регистрации перенаправляет на страницу профиля пользователя.
        В случае ошибок возвращает сообщение и перенаправляет на страницу регистрации.
    """
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":

        # Рассовывание данных из формы по соответствующим переменным
        user_login, contact_email, password, first_name, last_name = (
            request.form.get("user_login"),
            request.form.get("email"),
            request.form.get("password"),
            request.form.get("first_name"),
            request.form.get("last_name"),
        )

        # Проверка пароля
        if not is_valid_password(password):
            return flash_and_redirect("password", "Пароль не должен быть пустым", "/register")

        # Проверка почты на формат
        if not is_valid_email(contact_email):
            return flash_and_redirect("email", "Неверный формат почты", "/register")

        with sqlite3.connect(database_name) as con:
            cur = con.cursor()
            # Проверка почты на уникальность
            if cur.execute("SELECT COUNT(*) FROM user WHERE contact_email = ?", (contact_email,)).fetchone()[0]:
                return flash_and_redirect("email", "Такой почтовый адрес уже используется", "/register")

            # Проверка логина на уникальность
            if cur.execute("SELECT COUNT(*) FROM user WHERE login = ?", (user_login,)).fetchone()[0]:
                return flash_and_redirect("user_login", "Такой логин уже существует", "/register")

            # Все проверки пройдены — регистрируем время, создаем новую запись и передаем ID пользователя дальше
            register_date = date.today().strftime("%d.%m.%Y")
            cur.execute("""INSERT INTO user (login, password, first_name, last_name, contact_email, register_date)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (user_login, password, first_name, last_name, contact_email, register_date))
            user_id = cur.lastrowid

            session["user_id"] = user_id

            return redirect(url_for("profile_me"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        return render_template("logout.html")
    if request.method == "POST":
        session.pop("user_id", None)
        flash("Вы успешно вышли из системы!", "success")
        return redirect(url_for("index"))
    # TODO: Выяснить зачем тут нужен был DELETE, если есть POST


@app.route("/profiles", methods=["GET", "PUT"])
def profiles():
    if request.method == "GET":
        return render_template("profiles.html")
    if request.method == "PUT":
        return "PUT"


@app.route("/profiles/me", methods=["GET", "PUT", "DELETE"])
def profile_me():
    if request.method == "GET":

        user_id = session.get("user_id")    # Получение ID пользователя из сессии
        if not user_id:
            return redirect(url_for("login"))  # Перенаправление на страницу входа, если пользователь не авторизован

        with sqlite3.connect(database_name) as con:
            cur = con.cursor()
            user_data = cur.execute("""SELECT login, first_name, last_name, register_date, contact_phone, contact_email 
                        FROM user WHERE id = ?""", (user_id,)).fetchone()

        # render_template требует словарь в именованном аргументе
        user = tuple_to_dict(user_data,
                             "login",
                             "first_name",
                             "last_name",
                             "register_date",
                             "contact_phone",
                             "contact_email")

        return render_template("profile.html", user=user)
    if request.method == "PUT":
        return "PUT"
    if request.method == "DELETE":
        return "DELETE"


# !!! Используется как заглушка для profile_user ввиду отсутствия БД
# TODO: Удалить после реализации profile_user
@app.route("/profiles/random_user", methods=["GET"])
def random_profile():
    random_user_id = randint(0, 999)
    return redirect(url_for("profile_user", user_id=random_user_id))


@app.route("/profiles/<user_id>", methods=["GET"])
def profile_user(user_id):
    return render_template("user_profile.html", user_id=user_id)


@app.route("/profiles/search_history", methods=["GET", "POST", "DELETE"])
def profile_search_history():
    if request.method == "GET":
        return render_template("search_history.html")
    if request.method == "POST":
        return "POST"
    if request.method == "DELETE":
        return "DELETE"


@app.route("/profiles/favorites", methods=["GET", "POST"])
def profiles_favorites():
    if request.method == "GET":
        return render_template("favorites.html")
    if request.method == "POST":
        return "POST"


@app.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "GET":
        # TODO: Взять данные из базы
        # TODO: Отобразить на странице данные render_template("_____.html")
        return render_template("items.html")
    if request.method == "POST":
        # TODO: Получить данные из формы
        # TODO: Сохранить данные в базу
        return "POST"


# !!! Используется как заглушка для item_details ввиду отсутствия БД
# TODO: Удалить после реализации item_details
@app.route("/items/random_item", methods=["GET"])
def random_items():
    random_item = randint(0, 999)
    return redirect(url_for("item_details", item_id=random_item))


@app.route("/items/<item_id>", methods=["GET", "DELETE"])
def item_details(item_id):
    if request.method == "GET":
        return render_template("item_details.html", item_id=item_id)
    if request.method == "DELETE":
        return f"DELETE {item_id}"


@app.route("/leasers", methods=["GET"])
def leasers():
    return render_template("leasers.html")


# !!! Используется как заглушка для leaser_details ввиду отсутствия БД
# TODO: Удалить после реализации leaser_details
@app.route("/leasers/random_leaser_details", methods=["GET"])
def random_item_details():
    leaser_id = randint(0, 999)
    return redirect(url_for("leaser_details", leaser_id=leaser_id))


@app.route("/leasers/<leaser_id>", methods=["GET"])
def leaser_details(leaser_id):
    if request.method == "GET":
        return render_template("lease.html", leaser_id=leaser_id)


# !!! Используется как заглушка для contract_detail ввиду отсутствия БД
# TODO: Удалить после реализации contract_detail
@app.route("/contracts/random_contract", methods=["GET"])
def contracts():
    contract_id = randint(0, 999)
    return redirect(url_for("contract_detail", contract_id=contract_id))


@app.route("/contracts/<contract_id>", methods=["GET", "POST", "PUT"])
def contract_detail(contract_id):
    if request.method == "GET":
        return render_template("contract.html", contract_id=contract_id)
    if request.method == "POST":
        return f"POST {contract_id}"
    if request.method == "PUT":
        return f"PUT {contract_id}"


@app.route("/search", methods=["GET"])
def search():
    return render_template("search.html")


@app.route("/complain", methods=["GET", "POST"])
def complain():
    if request.method == "POST":  # TODO: Удалить после реализации остальных методов
        return render_template("complain.html")
    if request.method == "POST":
        return "POST"


@app.route("/compare", methods=["GET", "POST", "PUT"])
def compare():
    if request.method == "POST":  # TODO: Удалить после реализации остальных методов
        return render_template("compare.html")
    if request.method == "POST":
        return "POST"
    if request.method == "PUT":
        return "PUT"


if __name__ == "__main__":
    app.run()
