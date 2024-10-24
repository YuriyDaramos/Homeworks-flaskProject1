from flask import Flask, request, render_template

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
        return "GET"
    if request.method == "POST":
        return "POST"
    if request.method == "DELETE":
        return "DELETE"


@app.route("/profiles", methods=["GET", "PUT"])
def profiles():
    if request.method == "GET":
        return "GET"
    if request.method == "PUT":
        return "PUT"


@app.route("/profiles/my", methods=["GET", "PUT", "DELETE"])
def profiles_my():
    if request.method == "GET":
        return "GET"
    if request.method == "PUT":
        return "PUT"
    if request.method == "DELETE":
        return "DELETE"


@app.route("/profiles/<user_id>", methods=["GET"])
def profiles_user(user_id):
    if request.method == "GET":
        return f"GET {user_id}"


@app.route("/profiles/search_history", methods=["GET", "POST", "DELETE"])
def profiles_search_history():
    if request.method == "GET":
        return "GET"
    if request.method == "POST":
        return "POST"
    if request.method == "DELETE":
        return "DELETE"


@app.route("/profiles/favorites", methods=["GET", "POST"])
def profiles_favorites():
    if request.method == "GET":
        return "GET"
    if request.method == "POST":
        return "POST"


@app.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "GET":
        # TODO: Взять данные из базы
        # TODO: Отобразить на странице данные render_template("_____.html")
        return "GET"
    if request.method == "POST":
        # TODO: Получить данные из формы
        # TODO: Сохранить данные в базу
        return "POST"


@app.route("/items/<item_id>", methods=["GET", "DELETE"])
def item_details(item_id):
    if request.method == "GET":
        return f"GET {item_id}"
    if request.method == "DELETE":
        return f"DELETE {item_id}"


@app.route("/leasers", methods=["GET"])
def leasers():
    if request.method == "GET":
        return "GET"


@app.route("/leasers/<leaser_id>", methods=["GET"])
def leaser_details(leaser_id):
    if request.method == "GET":
        return f"GET {leaser_id}"


@app.route("/contracts", methods=["GET"])
def contracts():
    if request.method == "GET":
        return "GET"


@app.route("/contracts/<contract_id>", methods=["GET", "POST", "PUT"])
def contract_detail(contract_id):
    if request.method == "GET":
        return f"GET {contract_id}"
    if request.method == "POST":
        return f"POST {contract_id}"
    if request.method == "PUT":
        return f"PUT {contract_id}"


@app.route("/search", methods=["GET"])
def search():
    if request.method == "GET":
        return "GET"


@app.route("/complain", methods=["POST"])
def complain():
    if request.method == "POST":
        return "POST"


@app.route("/compare", methods=["POST", "PUT"])
def compare():
    if request.method == "POST":
        return "POST"
    if request.method == "PUT":
        return "PUT"


if __name__ == "__main__":
    app.run()
