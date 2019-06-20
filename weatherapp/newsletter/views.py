from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .models import Subscriber


def newsletter_signup(request):
    if request.method == 'GET':
        return render(request, 'newsletter_signup.html')
    if request.method == 'POST':
        try:
            Subscriber.objects.get(email=request.POST['email'])
            success_ = False
            return HttpResponseRedirect(reverse(failure))

        except Subscriber.DoesNotExist:
            subscriber = Subscriber(
                email=request.POST['email'],
                location=request.POST['location']
            )
            subscriber.save()
            success_ = True

            return HttpResponseRedirect(reverse(success))

def success(request):
    return render(request, 'success.html')


def failure(request):
    return render(request, 'failure.html')


