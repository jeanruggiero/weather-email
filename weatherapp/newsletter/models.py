from django.db import models

class Subscriber(models.Model):
    email = models.EmailField(primary_key=True)
    #location = models.CharField(max_length=128)

    def __repr__(self):
        return self.email


# class Location(models.Model):
#     name = models.CharField(max_length=128)

