import logging
import random

import colorlog

from faker import Faker
from database.models import Contact
from database.connect import get_database
from brocker.connect import connect

color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)


console_handler = logging.StreamHandler()
console_handler.setFormatter(color_formatter)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

def make_contacts(amount: int) -> list:
    fake = Faker()
    Faker.seed(1234) 
    contacts = []
    for _ in range(amount):
        username = fake.user_name()
        domain = fake.domain_name()  
        email = username.lower() + "@" + domain 
        contact = Contact(
            username=username,
            email=email,
            phone_number=fake.phone_number(),
            preferred_contact_method=random.choice(["email", "sms"])
        )
        contacts.append(contact)
    return contacts

if __name__ == "__main__":
    db = get_database().client
    channel = connect()

    # Очищення бази 
    Contact.objects().delete()

    # Наовнення бази
    for contact in make_contacts(100):
        contact.save()

    logger.info("<== Database filled with contacts. ==>")

    # Створення черг в брокері
    channel.queue_declare(queue='email_queue')
    channel.queue_declare(queue='sms_queue')


    # Очищення черг перед наповненням
    channel.queue_purge(queue='email_queue')
    channel.queue_purge(queue='sms_queue')


    # Отримання даних з mongo
    contacts = Contact.objects.all()


    for contact in contacts:
        match contact.preferred_contact_method:
            case "email":
                channel.basic_publish(exchange='',
                                    routing_key='email_queue', 
                                    body=str(contact.id).encode())
            case "sms":
                channel.basic_publish(exchange='', 
                                    routing_key='sms_queue', 
                                    body=str(contact.id).encode())


    logger.info("<== Messages sent to the appropriate queues. ==>")
    channel.close()
    db.close()
