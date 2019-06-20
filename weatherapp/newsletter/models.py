from django.db import models


class Location(models.Model):
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128)

    def __repr__(self):
        return self.city + ', ' + self.state

    def __str__(self):
        return self.city + ', ' + self.state


class Subscriber(models.Model):
    email = models.EmailField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

    def __repr__(self):
        return self.email

    def __str__(self):
        return 'Subscriber: ' + self.email + ' | ' + str(self.location)
