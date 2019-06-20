from django.db import models

class Subscriber(models.Model):
    email = models.EmailField()
    #location = models.CharField(max_length=128)


# class Location(models.Model):
#     name = models.CharField(max_length=128)

