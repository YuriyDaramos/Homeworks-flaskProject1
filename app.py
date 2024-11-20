from datetime import datetime
from functools import wraps
from random import randint

from flask import render_template, url_for, session, request, redirect, flash, Flask

from modules.utils import flash_and_redirect

from database import DATABASE_URL, db_session, init_db
import models

app = Flask(__name__)
app.secret_key = "12345"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


@app.teardown_request
def teardown_request(exceptions=None):
    db_session.remove()


@app.context_processor
def stats_data():
    session_id = session.get("user_id")
    users_total = models.User.query.count()
    items_total = models.Item.query.count()
    contracts_total = models.Contract.query.count()
    stats = {"users_total": users_total,
             "items_total": items_total,
             "contracts_total": contracts_total,
             "session_id": session_id}
    return dict(stats=stats)


@app.context_processor
def inject_user():
    user_id = session.get("user_id")
    # session["user_id"] = None
    user_data = {"id": None, "login": "Guest"}

    if user_id:
        try:
            user_id = int(user_id)
            user = models.User.query.filter_by(id=user_id).first()
            if user:
                user_data = {"id": user.id, "login": user.login}
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
        identifier = request.form["identifier"]
        password = request.form["password"]

        # Email или login
        if "@" in identifier and "." in identifier:
            user = models.User.query.filter_by(email=identifier, password=password).first()
        else:
            user = models.User.query.filter_by(login=identifier, password=password).first()

        if user:
            session["user_id"] = user.id
            return redirect(url_for("profile", user_id=user.id))

        flash_and_redirect("error-message", "Неверный логин или пароль", "/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        user_id = session.get("user_id")
        if user_id:
            return redirect(url_for("profile", user_id=user_id))
        return render_template("register.html")

    if request.method == "POST":
        form_data = dict(request.form)

        email = form_data.get("email")
        if "@" not in email or "." not in email:
            return flash_and_redirect("email", "Неверный формат почты", "/register")

        existing_user = models.User.query.filter_by(email=email).first()
        if existing_user:
            return flash_and_redirect("email", "Такой почтовый адрес уже используется", "/register")

        user_login = form_data.get("user_login")
        existing_user = models.User.query.filter_by(login=user_login).first()
        if existing_user:
            return flash_and_redirect("login", "Такой логин уже существует", "/register")

        user = models.User(login=form_data.get("user_login"),
                           password=form_data.get("password"),
                           first_name=form_data.get("first_name"),
                           last_name=form_data.get("last_name"),
                           email=form_data.get("email"),
                           register_date=datetime.now().strftime("%d-%m-%Y"))

        db_session.add(user)
        db_session.commit()

        session["user_id"] = user.id

        return redirect(url_for("profile", user_id=user.id))


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
    users = models.User.query.all()

    profile_card_data = []
    for user in users:
        items_rented = models.Contract.query.filter_by(owner_id=user.id).count()
        items_borrowed = models.Contract.query.filter_by(renter_id=user.id).count()

        profile_card_data.append({"id": user.id,
                                  "login": user.login,
                                  "first_name": user.first_name,
                                  "last_name": user.last_name,
                                  "avatar": user.avatar,
                                  "register_date": user.register_date,
                                  "items_rented": items_rented,
                                  "items_borrowed": items_borrowed})

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

        # Если не авторизован
        if not session.get("user_id"):
            user_data = {field: "*" * 10 for field in profile_fields}
            return render_template("profile.html", user=user_data)

        # Если авторизован
        user = models.User.query.filter_by(id=user_id).first()
        user_data = {field: getattr(user, field) for field in profile_fields}
        return render_template("profile.html", user=user_data)

    if request.method == "PUT":
        return "PUT"

    if request.method == "DELETE":
        return "DELETE"


@app.route("/profiles/random_user", methods=["GET"])
def random_profile():
    users_total = models.User.query.count()
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

        item = models.Item(name=request.form["name"],
                           photo=request.form["photo"],
                           desc=request.form.get("desc"),
                           price_h=request.form.get("price_h"),
                           price_d=request.form.get("price_d"),
                           price_w=request.form.get("price_w"),
                           price_m=request.form.get("price_m"),
                           owner_id=owner_id)

        db_session.add(item)
        db_session.commit()

        item_id = item.id

        # Параметр, чтобы показать кнопку добавления фото
        show_add_photo_button = False

        return redirect(url_for("item_details", item_id=item_id,
                                show_add_photo_button=show_add_photo_button))


@app.route("/items/", methods=["GET"])
def items():
    items_list = models.Item.query.all()

    item_card_data = []
    for item in items_list:
        contract = models.Contract.query.filter_by(item_id=item.id).first()
        is_available = contract.is_available if contract else None

        item_card_data.append({"id": item.id,
                               "name": item.name,
                               "photo": item.photo,
                               "desc": item.desc,
                               "price_h": item.price_h,
                               "price_d": item.price_d,
                               "price_w": item.price_w,
                               "price_m": item.price_m,
                               "owner_id": item.owner_id,
                               "is_available": is_available})

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

        # Данные о предмете
        item = models.Item.query.filter_by(id=item_id).first()
        if not item:
            return "Item not found", 404

        item_data = {"photo": item.photo,
                     "name": item.name,
                     "desc": item.desc,
                     "price_h": item.price_h,
                     "price_d": item.price_d,
                     "price_w": item.price_w,
                     "price_m": item.price_m,
                     "owner_id": item.owner_id}

        # Данные владельца
        owner = models.User.query.filter_by(id=item.owner_id).first()
        item_owner_data = {
            "first_name": owner.first_name,
            "last_name": owner.last_name,
            "login": owner.login,
        } if owner else None

        # Данные контракта
        contract = models.Contract.query.filter_by(item_id=item_id).first()
        contract_data = {
            "renter_id": contract.renter_id,
            "date_end": contract.date_end,
            "is_available": contract.is_available,
        } if contract else None

        # Данные арендатора, если контракт существует
        item_renter_data = None
        if contract and contract.renter_id:
            renter = models.User.query.filter_by(id=contract.renter_id).first()
            item_renter_data = {
                "first_name": renter.first_name,
                "last_name": renter.last_name,
                "login": renter.login,
            } if renter else None

        return render_template("item_details.html",
                               item_id=item_id,
                               item=item_data,
                               contract=contract_data,
                               item_owner=item_owner_data,
                               item_renter=item_renter_data,
                               user=True)
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

        # Получаем контракт по contract_id
        contract = models.Contract.query.get(contract_id)

        if not contract:
            return flash_and_redirect("error-message", "Контракт не найден", "/contracts")

        owner_id = contract.owner_id
        renter_id = contract.renter_id

        item_owner = models.User.query.get(owner_id)
        item_renter = models.User.query.get(renter_id)

        item = models.Item.query.get(contract.item_id)

        # Данные контракта
        contract_data = {"id": contract.id,
                         "start_date": contract.start_date,
                         "end_date": contract.end_date,
                         "is_available": contract.is_available,
                         "owner_id": contract.owner_id,
                         "renter_id": contract.renter_id,
                         "item_id": contract.item_id}

        # Данные владельца
        item_owner_data = {"first_name": item_owner.first_name,
                           "last_name": item_owner.last_name,
                           "login": item_owner.login}

        # Данные арендатора
        item_renter_data = {"first_name": item_renter.first_name,
                            "last_name": item_renter.last_name,
                            "login": item_renter.login}

        item_data = {"name": item.name}

        return render_template("contract_details.html",
                               contract=contract_data,
                               item=item_data,
                               item_owner=item_owner_data,
                               item_renter=item_renter_data,
                               user=True)

    if request.method == "POST":
        return f"POST {contract_id}"
    if request.method == "PUT":
        return f"PUT {contract_id}"


@app.route("/search", methods=["GET"])
def search():
    search_query = request.args.get("q", "").lower()

    # Подходящие профили
    founded_profiles = models.User.query.filter(
        models.User.login.ilike(f"%{search_query}%") |
        models.User.first_name.ilike(f"%{search_query}%") |
        models.User.last_name.ilike(f"%{search_query}%")
    ).all()

    # Подходящие предметы
    founded_items = models.Item.query.filter(
        models.Item.name.ilike(f"%{search_query}%") |
        models.Item.desc.ilike(f"%{search_query}%")
    ).all()

    # Данные для профилей
    profile_card_data = [
        {
            "id": user.id,
            "login": user.login,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar": user.avatar,
            "register_date": user.register_date,
            "owner_contracts": models.Contract.query.filter_by(owner_id=user.id).count(),
            "renter_contracts": models.Contract.query.filter_by(renter_id=user.id).count(),
        }
        for user in founded_profiles
    ]

    # Данные для предметов
    item_card_data = [
        {
            "id": item.id,
            "photo": item.photo,
            "name": item.name,
            "desc": item.desc,
            "price_h": item.price_h,
            "price_d": item.price_d,
            "price_w": item.price_w,
            "price_m": item.price_m,
            "owner_id": item.owner_id,
            "owner_name": item.owner.first_name + " " + item.owner.last_name,
        }
        for item in founded_items
    ]

    return render_template("search.html", users=profile_card_data, items=item_card_data)


@app.route("/complain", methods=["GET", "POST"])
@login_required
def complain():
    if request.method == "POST":
        return render_template("complain.html")
    if request.method == "POST":
        return "POST"


@app.route("/compare/add", methods=["GET"])
def add_to_compare():
    item_id = request.args.get("item_id")
    compare_list = request.args.get("items", "")
    next_url = request.args.get("next", url_for("item_details", item_id=item_id))

    if compare_list:
        compare_list = compare_list.split(",")
    else:
        compare_list = []

    if item_id in compare_list:
        compare_list.remove(item_id)
    else:
        compare_list.append(item_id)

    return redirect(url_for("compare", item_id=item_id, items=",".join(compare_list), next=next_url))


@app.route("/compare", methods=["GET", "POST", "PUT"])
def compare():
    if request.method == "GET":
        compare_list = request.args.get("items", "")
        items_to_compare = []

        # if compare_list:
        #     for item_id in compare_list.split(","):
        #         item_data = # TODO
        #         items_to_compare.append(item_data)
        return render_template("compare.html", items=items_to_compare)

    if request.method == "POST":
        return "POST"
    if request.method == "PUT":
        return "PUT"


if __name__ == "__main__":
    app.run()
