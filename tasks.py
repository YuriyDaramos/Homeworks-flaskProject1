from app import celery
import models


@celery.task
def send_contract_notification_task(item_id):
    # Имитируем отправку сообщения
    contract = models.Contract.query.get(item_id)
    print(f"Уведомление отправлено владельцу предмета {item_id}")
    return f"Уведомление отправлено владельцу предмета {item_id}"
