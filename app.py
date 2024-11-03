from datetime import date
from random import randint
from flask import Flask, render_template, url_for, session, g, request
from modules.utils import *
from modules.user_management import *

# Инициализация Flask
app = Flask(__name__)
app.secret_key = "12345"

database_name = "db_flask1.sqlite"


@app.context_processor
def inject_user():
    user_id: str = session.get("user_id")
    if user_id:
        user_name = get_data_from_db("login", database=database_name, sheet="users", search_field="id", value=user_id,
                                     debug=True)
        return {"user_name": user_name[0]}
    return {"user_name": "Гость"}


@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html", show_sidebar=False)  # Рендер страницы index.html


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("profile_me"))
        return render_template("login.html")
    if request.method == "POST":

        identifier, password = (
            request.form.get("identifier"),
            request.form.get("password")
        )

        user_id = verify_and_get_user_id(database_name, identifier, password, sheet="users", search_field="email")
        if user_id:
            session["user_id"] = user_id
            return redirect(url_for("profile_me"))
        return flash_and_redirect("form", "Упс, что-то пошло не так! Пишите в Спортлото", "/login")


# МОЯ РЕАЛИЗАЦИЯ
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
        - Если все проверки пройдены, регистрирует пользователя, сохраняет дату регистрации
          и ID пользователя в сессии.

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


@app.route("/profiles", methods=["GET", "PUT"])
def profiles():
    if request.method == "GET":
        return render_template("profiles.html")
    if request.method == "PUT":
        return "PUT"


@app.route("/profiles/me", methods=["GET", "PUT", "DELETE"])
def profile_me():
    if request.method == "GET":

        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))

        profile_fields = ("login",
                          "first_name",
                          "last_name",
                          "register_date",
                          "phone_number",
                          "email")
        user_data = get_data_from_db(*profile_fields, database=database_name, sheet="users", search_field="id",
                                     value=user_id, dictionary=True)

        return render_template("profile.html", user=user_data)
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
        # with DB_local(database_name) as db_cur:
        #     db_cur.execute("SELECT * FROM item")
        #     items = db_cur.fetchall()   # что-то тут н работает. передается лист из-за fetchALL.
        # что-то не так с контекстным менеджером, надо починить фабрику словарей

        # TODO: Отобразить на странице данные render_template("_____.html")
        return render_template("items.html", items=items)
    if request.method == "POST":
        # TODO: Получить данные из формы
        # TODO: Сохранить данные в базу
        return "POST"


@app.route("/user", methods=["GET", "POST"])
def user():
    if request.method == "GET":
        # with DB_local(database_name) as db_cur:
        #     db_cur.execute("SELECT * FROM item")
        #     items = db_cur.fetchall()   # что-то тут н работает. передается лист из-за fetchALL.
        # что-то не так с контекстным менеджером, надо починить фабрику словарей

        # TODO: Отобразить на странице данные render_template("_____.html")
        return render_template("user.html", items=items)
    if request.method == "POST":
        # TODO: Получить данные из формы
        photo, name, desc, price_h, price_d, price_w, price_m = (
            request.form.get("photo"),
            request.form.get("name"),
            request.form.get("desc"),
            request.form.get("price_h"),
            request.form.get("price_d"),
            request.form.get("price_w"),
            request.form.get("price_m"),
        )

        user_id = session["user_id"]

        # TODO: Сохранить данные в базу
        # with DB_local(database_name) as db_cur:
        #     db_cur.execute("""INSERT INTO item (photo, name, desc, price_h, price_d, price_w, price_m, user)
        #     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (photo, name, desc, price_h, price_d, price_w, price_m, user_id))
        #     item_id = cur.lastrowid
        return redirect(url_for("item_details", item_id=item_id))


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
