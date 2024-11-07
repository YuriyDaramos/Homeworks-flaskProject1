from functools import wraps
from random import randint
from flask import Flask, render_template, url_for, session, request, redirect, flash

from modules.users_management import UserManager
from modules.contracts_management import ContractsManager
from modules.items_management import ItemManager
from modules.utils import flash_and_redirect, get_data_for_profile_card, get_data_for_item_card

app = Flask(__name__)
app.secret_key = "12345"

DATABASE = "db_flask1.sqlite"
users_manager = UserManager(DATABASE)
contracts_manager = ContractsManager(DATABASE)
items_manager = ItemManager(DATABASE)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.context_processor
def stats_data():
    session_id = session.get("user_id")
    users_total = users_manager.get_users_data("COUNT(*)")[0][0]
    items_total = items_manager.get_items_data("COUNT(*)")[0][0]
    contracts_total = contracts_manager.get_contracts_data("COUNT(*)")[0][0]
    stats = {
        "users_total": users_total,
        "items_total": items_total,
        "contracts_total": contracts_total,
        "session_id": session_id
    }
    return dict(stats=stats)


@app.context_processor
def inject_user():
    user_id = session.get("user_id")
    # session["user_id"] = None
    user_data = {"id": None, "login": "Guest"}

    if user_id:
        try:
            user_id = int(user_id)
            user_login = users_manager.get_user_data(user_id, "login")
            if user_login:
                user_data = {"id": user_id, "login": user_login[0]}
        except (TypeError, ValueError):
            print(f"Пользователь с ID неверного типа: {type(user_id)}")
            user_data["id"] = None
            session["user_id"] = None

    return {"current_user": user_data}


@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        user_id = session.get("user_id")
        if user_id:
            return redirect(url_for("profile", user_id=user_id))
        return render_template("login.html")

    if request.method == "POST":
        user_id = users_manager.verify_user(request.form)
        if user_id is not None:
            session["user_id"] = user_id
            return redirect(url_for("profile", user_id=user_id))
        return flash_and_redirect("error-message", "Неверный логин или пароль", "/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        user_id = session.get("user_id")
        if user_id:
            return redirect(url_for("profile", user_id=user_id))
        return render_template("register.html")

    if request.method == "POST":
        register_result = users_manager.register_new_user(request.form)
        if not register_result["success"]:
            message = register_result["message"]
            template = register_result["template"]
            return flash_and_redirect(template, message, "/register")
        if register_result["success"]:
            session["user_id"] = register_result.get("user_id", None)

        return redirect(url_for("profile", user_id=session["user_id"]))


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "GET":
        return render_template("logout.html")

    if request.method == "POST":
        session.pop("user_id", None)
        flash("Вы успешно вышли из системы!", "success")
        return redirect(url_for("index"))


@app.route("/profiles", methods=["GET"])
def profiles():
    profile_card_data = get_data_for_profile_card(users_manager, contracts_manager)

    return render_template("profiles.html", users=profile_card_data)


@app.route("/profile/<user_id>", methods=["GET", "PUT", "DELETE"])
def profile(user_id):
    if request.method == "GET":
        profile_fields = ("login",
                          "first_name",
                          "last_name",
                          "register_date",
                          "phone_number",
                          "email")

        if user_id == session.get("user_id"):
            user_data = users_manager.get_user_data(user_id, profile_fields)
            return render_template("profile.html", user=user_data)

        user_data = users_manager.get_user_data(user_id, profile_fields)
        if not session.get("user_id"):
            if user_id == "me":
                return redirect(url_for("login"))
            user_data = dict(user_data)
            for key in user_data.keys():
                user_data[key] = "*" * 10
            return render_template("profile.html", user=user_data)
        return render_template("profile.html", user=user_data)
    if request.method == "PUT":
        return "PUT"
    if request.method == "DELETE":
        return "DELETE"


@app.route("/profiles/random_user", methods=["GET"])
def random_profile():
    users_total = users_manager.get_users_data("COUNT(*)")[0][0]
    random_user_id = randint(1, users_total)
    return redirect(url_for("profile", user_id=random_user_id))


@app.route("/profiles/search_history", methods=["GET", "POST", "DELETE"])
@login_required
def profile_search_history():
    if request.method == "GET":
        return render_template("search_history.html")
    if request.method == "POST":
        return "POST"
    if request.method == "DELETE":
        return "DELETE"


@app.route("/profiles/favorites", methods=["GET", "POST"])
@login_required
def profiles_favorites():
    if request.method == "GET":
        return render_template("favorites.html")
    if request.method == "POST":
        return "POST"


@app.route("/items/add", methods=["GET", "POST"])
@login_required
def add_item():
    if request.method == "GET":
        return render_template("add_item.html")

    if request.method == "POST":

        if not request.form["name"]:
            return flash_and_redirect("name", "Название предмета не должно быть пустым", "/items")
        if not request.form["photo"]:
            return flash_and_redirect("photo", "Фото предмета не должно быть пустым", "/items")
        if not request.form["desc"]:
            return flash_and_redirect("desc", "Описание предмета не должно быть пустым", "/items")

        owner_id = session.get("user_id")
        item_id = None
        register_result = items_manager.register_new_item(request.form, owner_id)
        if not register_result["success"]:
            message = register_result["message"]
            template = register_result["template"]
            return flash_and_redirect(template, message, "/register")
        if register_result["success"]:
            item_id = register_result.get("item_id")

        show_add_photo_button = False

        return redirect(url_for("item_details", item_id=item_id,
                                show_add_photo_button=show_add_photo_button))


@app.route("/items/", methods=["GET"])
def items():
    item_card_data = get_data_for_item_card(items_manager, contracts_manager)

    return render_template("items.html", items=item_card_data)


@app.route("/items/random_item_details", methods=["GET"])
def random_item_details():
    item_id = randint(1, 14)
    return redirect(url_for("item_details", item_id=item_id))


@app.route("/items/<item_id>", methods=["GET", "POST", "DELETE"])
def item_details(item_id):
    if request.method == "GET":
        if not session.get("user_id"):
            return redirect(url_for("login"))

        item_fields = (
            "photo",
            "name",
            "desc",
            "price_h",
            "price_d",
            "price_w",
            "price_m",
            "owner_id"
        )
        item_data = items_manager.get_item_data(item_id, item_fields)

        owner_id = item_data["owner_id"]
        participant_fields = (
            "first_name",
            "last_name",
            "login"
        )
        item_owner_data = users_manager.get_user_data(owner_id, participant_fields)

        contract_fields = (
            "renter_id",
            "date_end",
            "is_available"
        )
        contract_data = contracts_manager.get_contract_data(item_id, contract_fields)
        renter_id = contract_data["renter_id"]
        item_renter_data = users_manager.get_user_data(renter_id, participant_fields)

        return render_template(
            "item_details.html",
            item=item_data,
            contract=contract_data,
            item_owner=item_owner_data,
            item_renter=item_renter_data,
            user=True
        )
    if request.method == "POST":
        return "POST"
    if request.method == "DELETE":
        return f"DELETE {item_id}"


@app.route("/contracts/random_contract", methods=["GET"])
@login_required
def contracts():
    contract_id = randint(1, 20)
    return redirect(url_for("contract_details", contract_id=contract_id))


@app.route("/contracts/<contract_id>", methods=["GET", "POST", "PUT"])
@login_required
def contract_details(contract_id):
    if request.method == "GET":
        if not session.get("user_id"):
            return redirect(url_for("login"))
        print(contract_id)
        contract_data = contracts_manager.get_contract_data(contract_id)

        owner_id = contract_data["owner_id"]
        renter_id = contract_data["renter_id"]
        participant_fields = (
            "first_name",
            "last_name",
            "login"
        )
        item_owner_data = users_manager.get_user_data(owner_id, participant_fields)
        item_renter_data = users_manager.get_user_data(renter_id, participant_fields)

        item_id = contract_data["item_id"]
        print(item_id)
        item_data = items_manager.get_item_data(item_id, "name")

        return render_template(
            "contract_details.html",
            contract=contract_data,
            item=item_data,
            item_owner=item_owner_data,
            item_renter=item_renter_data,
            user=True
        )

    if request.method == "POST":
        return f"POST {contract_id}"
    if request.method == "PUT":
        return f"PUT {contract_id}"


@app.route("/search", methods=["GET"])
def search():
    profile_card_data = get_data_for_profile_card(users_manager, contracts_manager)
    item_card_data = get_data_for_item_card(items_manager, contracts_manager)

    # Получаем поисковый запрос из URL
    search_query = request.args.get("q", "").lower()  # Получаем запрос из строки запроса

    # Ищем подходящие профили
    founded_profiles = [
        profile for profile in profile_card_data
        if search_query in profile["login"].lower() or
           search_query in profile["first_name"].lower() or
           search_query in profile["last_name"].lower()
    ]

    # Ищем подходящие предметы
    founded_items = [
        item for item in item_card_data
        if search_query in item["name"].lower() or
           search_query in item["desc"].lower()
    ]

    return render_template("search.html", profiles=founded_profiles, items=founded_items)


@app.route("/complain", methods=["GET", "POST"])
@login_required
def complain():
    if request.method == "POST":
        return render_template("complain.html")
    if request.method == "POST":
        return "POST"


@app.route("/compare", methods=["GET", "POST", "PUT"])
def compare():
    if request.method == "POST":
        return render_template("compare.html")
    if request.method == "POST":
        return "POST"
    if request.method == "PUT":
        return "PUT"


if __name__ == "__main__":
    app.run()
