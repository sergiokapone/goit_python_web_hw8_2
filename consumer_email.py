import sys
import time
import traceback


from logger.project_logger import logger
from database.models import Contact
from brocker.connect import connect
from database.connect import get_database
from bson import ObjectId

def send_email(ch, method, properties, body):

    contact_id = body.decode()
    contact = Contact.objects.get(id=ObjectId(contact_id))
    if not contact.sent:
        contact.sent = True
        logger.info(f"email => {contact.username}")
        contact.save()
        
        # Код для відправки
        # ...
        time.sleep(1) # Моделювання відправики
        # ...

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    get_database().client
    channel = connect()
    channel.basic_qos(prefetch_count=1)
    channel.queue_declare(queue='email_queue')
    channel.basic_consume(queue='email_queue', on_message_callback=send_email)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except Exception:
        channel.stop_consuming()
        traceback.print_exc(file=sys.stdout)
