from flask import flash, redirect


def flash_and_redirect(field: str, message: str, route: str):
    """Отправляет сообщение об ошибке для указанного поля и перенаправляет на страницу регистрации."""
    flash({field: message})  # Сохраняем сообщение в словаре с ключом (названием) поля в HTML-шаблоне
    return redirect(route)


def get_data_for_item_card(items_manager, contracts_manager):
    item_fields = (
        "id",
        "photo",
        "name",
        "desc",
        "price_h",
        "price_d",
        "price_w",
        "price_m",
    )
    items_data = items_manager.get_items_data(item_fields)

    contract_fields = (
        "item_id",
        "is_available"
    )
    contracts_data = contracts_manager.get_contracts_data(contract_fields)

    contracts_dict = {}
    for contract in contracts_data:
        contracts_dict[contract["item_id"]] = contract["is_available"]

    items_with_contracts = []
    for item in items_data:
        is_available = contracts_dict.get(item["id"], False)
        item_data = {
            "id": item["id"],
            "photo": item["photo"],
            "name": item["name"],
            "desc": item["desc"],
            "price_h": item["price_h"],
            "price_d": item["price_d"],
            "price_w": item["price_w"],
            "price_m": item["price_m"],
            "is_available": is_available,
        }
        items_with_contracts.append(item_data)
    return items_with_contracts


def get_data_for_profile_card(users_manager, contracts_manager):

    flat_fields = "id, login, first_name, last_name, avatar, register_date"
    users_data = users_manager.get_users_data(flat_fields)

    owner_data = contracts_manager.get_rental_items_data("owner_id")
    renter_data = contracts_manager.get_rental_items_data("renter_id")

    users_contracts = {}
    for contract in owner_data:
        user_id = contract[0]
        items_rented = contract[1]
        users_contracts[user_id] = {"items_rented": items_rented, "items_borrowed": 0}

    for contract in renter_data:
        if contract[0] in users_contracts:
            users_contracts[contract[0]]["items_borrowed"] = contract[1]
        else:
            users_contracts[contract[0]] = {"items_rented": 0, "items_borrowed": contract[1]}

    users_with_contracts = []
    for user in users_data:
        user_data = {
            "id": user["id"],
            "login": user["login"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "avatar": user["avatar"],
            "register_date": user["register_date"],
            "contract": users_contracts.get(user["id"], {"items_rented": 0, "items_borrowed": 0}),
        }
        users_with_contracts.append(user_data)
    return users_with_contracts


def main():
    pass


if __name__ == "__main__":
    main()
