from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from ...models import Subscriber

class Command(BaseCommand):
    help = 'Lists all currently subscribed email addresses.'

    def handle(self, *args, **kwargs):
        subscribers = Subscriber.objects.order_by('email')
        for subscriber in subscribers:
            send_mail('Test',
                      subscriber.location,
                      'jeanruggiero@gmail.com',
                      [subscriber.email])
