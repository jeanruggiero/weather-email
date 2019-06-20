from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .models import Subscriber


def newsletter_signup(request):
    if request.method == 'GET':
        return render(request, 'newsletter_signup.html')
    if request.method == 'POST':
        subscriber = Subscriber(
            email=request.POST['email'],
        )
        subscriber.save()
        return HttpResponseRedirect(reverse(newsletter_signup))


