from datetime import datetime
from functools import wraps
from random import randint
from flask import render_template, url_for, session, request, redirect, flash, Flask, abort

import celery_tasks
from modules.utils import flash_and_redirect, parse_price
from database import DATABASE_URL, db_session, init_db
import models

# Инициализация и настройки Flask
app = Flask(__name__)
app.secret_key = "12345"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Инициализация базы данных
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
    # session.pop("user_id", None)
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


@app.route("/profile/<int:user_id>", methods=["GET"])
@login_required
def profile(user_id):
    if request.method == "GET":
        user = models.User.query.filter_by(id=user_id).first()
        if user is None:
            return "Пользователь не найден", 404

        user_items = models.Item.query.filter_by(owner_id=user.id).all()

        rented_items = models.Item.query.join(models.Contract).filter(
            (models.Contract.owner_id == user.id) | (models.Contract.renter_id == user.id)
        ).all()

        user_contracts = models.Contract.query.filter(
            (models.Contract.owner_id == user.id) | (models.Contract.renter_id == user.id)
        ).all()

        return render_template("profile.html",
                               user=user,
                               user_items=user_items,
                               rented_items=rented_items,
                               user_contracts=user_contracts)


@app.route("/profile/edit", methods=["GET", "POST", "DELETE"])
@login_required
def profile_edit():
    if request.method == "GET":
        user_id = session.get("user_id")
        user = models.User.query.filter_by(id=user_id).first()
        return render_template("profile_edit.html", user=user)

    if request.method == "POST":
        user_id = session.get("user_id")
        user = models.User.query.filter_by(id=user_id).first()

        if request.form.get('_method') == 'DELETE':
            user_items = models.Item.query.filter_by(owner_id=user.id).first()
            if user_items:
                flash("Необходимо удалить все арендуемые предметы, прежде чем удалить профиль.", "error")
                return render_template("profile_edit.html", user=user)

            user_contracts = models.Contract.query.filter(
                (models.Contract.owner_id == user_id) | (models.Contract.renter_id == user_id)
            ).all()
            if user_contracts:
                for contract in user_contracts:
                    date_now = datetime.utcnow().strftime("%Y-%m-%d")
                    if contract.date_end > date_now:
                        flash("Необходимо дождаться окончания всех активных контрактов, прежде чем удалить профиль.",
                              "error")
                        return render_template("profile_edit.html", user=user)

            # db_session.delete(user)
            # db_session.commit()
            print(f"{user_id} DELETED")
            session.pop("user_id", None)  # Причудливый способ разлогиниться специально для тестов

            return redirect(url_for("index"))
            # DELETE END

        # POST START
        form_data = dict(request.form)

        if form_data.get("avatar"):
            user.avatar = form_data.get("avatar")
        if form_data.get("email"):
            email = form_data.get("email")
            if "@" not in email or "." not in email:
                flash("Неверный формат почты", "error")
                return render_template("profile_edit.html", user=user)
            existing_user = models.User.query.filter_by(email=email).first()
            if existing_user and email != user.email:
                flash("Такой почтовый адрес уже используется", "error")
                return render_template("profile_edit.html", user=user)
            user.email = form_data.get("email")
        if form_data.get("new_password"):
            if not form_data.get("new_password") == form_data.get("confirm_password"):
                flash("Пароли не совпадают", "error")
                return render_template("profile_edit.html", user=user)
            user.password = form_data.get("new_password")
        if form_data.get("first_name"):
            user.first_name = form_data.get("first_name")
        if form_data.get("last_name"):
            user.last_name = form_data.get("last_name")
        if form_data.get("phone_number"):
            user.phone_number = form_data.get("phone_number")
        if form_data.get("ipn"):
            user.ipn = form_data.get("ipn")

        db_session.add(user)
        db_session.commit()

        flash("Профиль обновлён", "success")
        return render_template("profile_edit.html", user=user)


@app.route("/profiles/random_user", methods=["GET"])
def random_profile():
    users_total = models.User.query.count()
    random_user_id = randint(1, users_total)
    return redirect(url_for("profile", user_id=random_user_id))


@app.route("/favourites", methods=["GET", "POST"])
@login_required
def favourites():
    if request.method == "GET":
        user_id = session.get("user_id")
        favourite_items = db_session.query(models.Item).join(models.Favourite).filter(
            models.Favourite.user == user_id).all()
        return render_template("favourites.html", favourite_items=favourite_items)

    if request.method == "POST":
        item_id = request.form.get('item_id')
        user_id = session.get("user_id")
        existing_fav = db_session.query(models.Favourite).filter_by(user=user_id, item=item_id).first()

        if existing_fav:
            # Если товар в избранном, удаляем его
            db_session.delete(existing_fav)
            db_session.commit()
            flash("Товар удалён из избранного!", "success")
        else:
            # Если товара нет в избранном, добавляем его
            new_fav = models.Favourite(user=user_id, item=item_id)
            db_session.add(new_fav)
            db_session.commit()
            flash("Товар добавлен в избранное!", "success")

        # Перенаправляем обратно на страницу избранного
        return redirect(url_for("favourites"))


@app.route("/items/add", methods=["GET", "POST"])
@login_required
def add_item():
    if request.method == "GET":
        return render_template("add_item.html")

    if request.method == "POST":

        # Проверка обязательных полей
        required_fields = {"name": "Название предмета не должно быть пустым",
                           "photo": "Фото предмета не должно быть пустым",
                           "desc": "Описание предмета не должно быть пустым"}
        for field, error_message in required_fields.items():
            if not request.form.get(field):
                return flash_and_redirect(field, error_message, "/items")

        owner_id = session.get("user_id")

        price_h = parse_price(request.form.get('price_h', ''))
        price_d = parse_price(request.form.get('price_d', ''))
        price_w = parse_price(request.form.get('price_w', ''))
        price_m = parse_price(request.form.get('price_m', ''))

        new_item = models.Item(name=request.form["name"],
                               photo=request.form["photo"],
                               desc=request.form.get("desc"),
                               price_h=price_h,
                               price_d=price_d,
                               price_w=price_w,
                               price_m=price_m,
                               owner_id=owner_id)
        db_session.add(new_item)
        db_session.commit()

        item_id = new_item.id

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

        # Данные владельца
        owner = models.User.query.filter_by(id=item.owner_id).first()

        # Данные контракта
        contract = models.Contract.query.filter_by(item_id=item_id).first()

        # Данные арендатора, если контракт существует
        renter = None
        if contract:
            renter = models.User.query.filter_by(id=contract.renter_id).first()

        # Список для сравнения
        user_id = session.get("user_id")
        user = models.User.query.filter_by(id=user_id).first()
        compare_list = user.compare_items or []

        favourite_items = db_session.query(models.Favourite.item).filter(models.Favourite.user == user.id).all()
        favourite_items = [item[0] for item in favourite_items]

        return render_template("item_details.html",
                               item_id=item_id,
                               item=item,
                               contract=contract,
                               item_owner=owner,
                               item_renter=renter,
                               compare_list=compare_list,
                               user=user,
                               favourite_items=favourite_items)


@app.route("/item/<int:item_id>/edit", methods=["GET", "POST", "DELETE"])
@login_required
def item_edit(item_id):
    if request.method == "GET":

        active_contracts = models.Contract.query.filter(
            models.Contract.item_id == item_id,
            models.Contract.date_end > datetime.utcnow().strftime("%Y-%m-%d")
        ).all()

        # Если есть активные контракты, блокируем редактирование товара
        if active_contracts:
            flash("Невозможно редактировать товар, так как для него есть активные контракты.", "error")
            return redirect(url_for('item_details', item_id=item_id))

        item = models.Item.query.filter_by(id=item_id).first()
        return render_template("item_edit.html", item=item)

    if request.method == "POST":
        item = models.Item.query.filter_by(id=item_id).first()

        if request.form.get('_method') == "DELETE":
            models.Contract.query.filter_by(item_id=item_id).delete()
            models.Favourite.query.filter_by(item=item_id).delete()
            db_session.delete(item)
            db_session.commit()
            return redirect(url_for("profile", user_id=session['user_id']))
            # DELETE END

        # POST START
        form_data = dict(request.form)
        if form_data.get("name"):
            item.name = form_data.get("name")
        if form_data.get("description"):
            item.desc = form_data.get("description")
        if form_data.get("price_h"):
            item.price_h = form_data.get("price_h")
        if form_data.get("price_d"):
            item.price_d = form_data.get("price_d")
        if form_data.get("price_w"):
            item.price_w = form_data.get("price_w")
        if form_data.get("price_m"):
            item.price_m = form_data.get("price_m")

        db_session.add(item)
        db_session.commit()

        flash("Товар обновлён", "success")
        return redirect(url_for('item_details', item_id=item.id))


@app.route("/contracts/new", methods=["GET", "POST"])
@login_required
def create_contract():
    if request.method == "GET":
        item_id = request.args.get('item_id')

        item = models.Item.query.get(item_id)
        owner = models.User.query.get(item.owner_id)
        renter = models.User.query.get(session.get("user_id"))

        return render_template("contract_form.html",
                               item=item,
                               owner=owner,
                               renter=renter,
                               user=session.get("user_id"))
    if request.method == "POST":

        item_id = request.form.get('item_id')  # Получаем item_id из скрытого поля
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        contract_text = request.form.get('contract_text')

        item = models.Item.query.get(item_id)
        user_id = session.get("user_id")

        existing_contract = models.Contract.query.filter_by(item_id=item_id).first()

        if existing_contract:
            existing_contract.date_start = start_date
            existing_contract.date_end = end_date
            existing_contract.text = contract_text
            existing_contract.renter_id = user_id
            existing_contract.is_available = False
            db_session.commit()
            message = celery_tasks.send_contract_notification(existing_contract.item_id)
        else:
            new_contract = models.Contract(
                item_id=item_id,
                owner_id=item.owner_id,
                renter_id=user_id,
                date_start=start_date,
                date_end=end_date,
                text=contract_text,
                is_available=0
            )
            db_session.add(new_contract)
            db_session.commit()
            message = celery_tasks.send_contract_notification.apply_async(item_id)

        flash(message, "success")
        return redirect(url_for('item_details', item_id=item_id))


@app.route("/contracts/random_contract", methods=["GET"])
@login_required
def contracts():
    item_id = randint(1, 20)
    return redirect(url_for("contract_details", item_id=item_id))


@app.route("/contracts/<item_id>", methods=["GET", "POST"])
@login_required
def contract_details(item_id):
    if request.method == "GET":
        if not session.get("user_id"):
            return redirect(url_for("login"))

        contract = models.Contract.query.get(item_id)

        if not contract:
            flash("Контракт не найден", "error-message")
            abort(404)

        owner_id = contract.owner_id
        renter_id = contract.renter_id

        item_owner = models.User.query.get(owner_id)
        item_renter = models.User.query.get(renter_id)

        item = models.Item.query.get(contract.item_id)
        return render_template("contract_details.html",
                               contract=contract,
                               item=item,
                               item_owner=item_owner,
                               item_renter=item_renter,
                               user=True)

    if request.method == "POST":
        return f"POST {item_id}"


@app.route("/search", methods=["GET"])
def search():
    search_query = request.args.get("q", "").lower()
    if search_query:
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

        # Сохранение в истории поиска, если пользователь авторизован
        user_id = session.get("user_id")
        if user_id:
            if search_query:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                existing_record = models.SearchHistory.query.filter_by(user=user_id).first()
                if existing_record:
                    existing_record.search_text += f", {search_query}"
                    existing_record.timestamp += f", {timestamp}"
                else:
                    new_search = models.SearchHistory(
                        user=user_id,
                        search_text=search_query,
                        timestamp=timestamp
                    )
                    db_session.add(new_search)

                db_session.commit()

        return render_template("search.html", users=profile_card_data, items=item_card_data)


@app.route("/search_history", methods=["GET"])
@login_required
def search_history():
    user_id = session.get("user_id")

    # Получаем последние 10 записей истории поиска для текущего пользователя
    search_history = models.SearchHistory.query.filter_by(user=user_id).order_by(
        models.SearchHistory.timestamp.desc()).all()

    # Инициализируем списки для запросов и временных меток
    search_queries = []
    timestamps = []

    # Обрабатываем каждую запись истории поиска
    for record in search_history:
        # Разделяем строки по запятой и добавляем в соответствующие списки
        queries = record.search_text.split(',')  # Разделяем по запятой
        time_stamps = record.timestamp.split(',')  # Разделяем по запятой

        # Добавляем результаты в списки
        search_queries.extend(queries)  # Добавляем все запросы
        timestamps.extend(time_stamps)  # Добавляем все временные метки

    # Удаляем лишние пробелы и очищаем списки
    search_queries = [query.strip() for query in search_queries]
    timestamps = [timestamp.strip() for timestamp in timestamps]

    # Печатаем для отладки
    print(search_queries)
    print(timestamps)

    return render_template("search_history.html", search_queries=search_queries, timestamps=timestamps)


@app.route("/complain", methods=["GET", "POST"])
@login_required
def complain():
    if request.method == "GET":
        return render_template("complain.html")
    if request.method == "POST":
        return "POST"


@app.route("/compare/add", methods=["GET"])
@login_required
def add_to_compare():
    MAX_ITEMS_TO_COMPARE = 5

    # item_id из текущего URL предмета
    item_id = request.args.get("item_id")

    user_id = session.get("user_id")
    user = models.User.query.filter_by(id=user_id).first()

    compare_list = user.compare_items or []

    # Добавляем или удаляем item_id из списка по той же кнопке
    if item_id in compare_list:
        compare_list.remove(item_id)
    else:
        compare_list.append(item_id)
        if len(compare_list) > MAX_ITEMS_TO_COMPARE:
            flash(f"Нельзя сравнивать одновременно более {MAX_ITEMS_TO_COMPARE} товаров", "result")
            return redirect(request.referrer)

    models.User.query.filter_by(id=user_id).update({"compare_items": compare_list})  # Особенности работы с JSON
    db_session.commit()

    flash("Список для сравнения обновлен.", "result")
    return redirect(url_for("item_details", item_id=item_id, items=",".join(compare_list)))


@app.route("/compare", methods=["GET", "POST", "PUT"])
@login_required
def compare():
    if request.method == "GET":
        user_id = session.get("user_id")
        user = models.User.query.filter_by(id=user_id).first()

        compare_list = user.compare_items or []

        # Все товары по одному запросу
        items_data_to_compare = models.Item.query.filter(models.Item.id.in_(compare_list)).all()

        return render_template("compare.html", items=items_data_to_compare)

    if request.method == "POST":
        user_id = session.get("user_id")
        user = models.User.query.get(user_id)
        if user:
            compare_list = []
            models.User.query.filter_by(id=user_id).update({"compare_items": compare_list})
            db_session.commit()
            flash("Список очищен", "result")
        return render_template("compare.html")
    if request.method == "PUT":
        return "PUT"


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
