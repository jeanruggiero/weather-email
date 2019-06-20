from django.core.management.base import BaseCommand
from ...models import Subscriber

class Command(BaseCommand):
    help = 'Lists all currently subscribed email addresses.'

    def handle(self, *args, **kwargs):
        subscribers = Subscriber.objects.order_by('email')
        for subscriber in subscribers:
            self.stdout.write(str(subscriber))
