from flask import Flask, request, render_template, redirect, url_for
from random import randint

app = Flask(__name__)


# Пример регистрации ресурса (корневой URL в данном случае)
@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")    # Рендер страницы index.html


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        return "POST"


# # Аналог кода выше, но другая запись
# # ! Шаблон для метода ГЕТ, не позволяет использовать любой другой метод
# @app.get("/login")
# def login():
#     return render_template("login.html")


# Пример другой функции для того же ресурса /login
# @app.route("/login", methods=["POST"])
# def login_post():
#     if request.method == "POST":
#         return "POST"


# # Разделение функций подобным образом (и как выше) имеет смысл, если логика ГЕТ и ПОСТ-функций сильно отличаются
# @app.post("/login")
# def login_post():
#     if request.method == "POST":
#         return "POST"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        return "POST"


@app.route("/logout", methods=["GET", "POST", "DELETE"])
def logout():
    if request.method == "GET":
        return render_template("logout.html")
    if request.method == "POST":
        return "POST"
    if request.method == "DELETE":
        return "DELETE"


@app.route("/profiles", methods=["GET", "PUT"])
def profiles():
    if request.method == "GET":
        return render_template("profiles.html")
    if request.method == "PUT":
        return "PUT"


@app.route("/profiles/me", methods=["GET", "PUT", "DELETE"])
def profile_me():
    if request.method == "GET":
        return render_template("profile_me.html")
    if request.method == "PUT":
        return "PUT"
    if request.method == "DELETE":
        return "DELETE"


# !!! Используется как заглушка для profile_user ввиду отсутствия БД
# TODO: Удалить после реализации profile_user
@app.route("/profiles/random_user", methods=["GET"])
def random_profile():
    random_user_id = randint(0, 999)
    return redirect(url_for('profile_user', user_id=random_user_id))


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
    return redirect(url_for('item_details', item_id=random_item))


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
    return redirect(url_for('leaser_details', leaser_id=leaser_id))


@app.route("/leasers/<leaser_id>", methods=["GET"])
def leaser_details(leaser_id):
    if request.method == "GET":
        return render_template("lease.html", leaser_id=leaser_id)


# !!! Используется как заглушка для contract_detail ввиду отсутствия БД
# TODO: Удалить после реализации contract_detail
@app.route("/contracts/random_contract", methods=["GET"])
def contracts():
    contract_id = randint(0, 999)
    return redirect(url_for('contract_detail', contract_id=contract_id))


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
    if request.method == "POST":    # TODO: Удалить после реализации остальных методов
        return render_template("complain.html")
    if request.method == "POST":
        return "POST"


@app.route("/compare", methods=["GET", "POST", "PUT"])
def compare():
    if request.method == "POST":    # TODO: Удалить после реализации остальных методов
        return render_template("compare.html")
    if request.method == "POST":
        return "POST"
    if request.method == "PUT":
        return "PUT"


if __name__ == "__main__":
    app.run()
