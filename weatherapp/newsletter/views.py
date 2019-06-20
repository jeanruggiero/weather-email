from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Subscriber, Location


def newsletter_signup(request):
    if request.method == 'GET':
        locations = Location.objects.order_by('city')
        return render(request, 'newsletter_signup.html', {'locations': locations})
    if request.method == 'POST':
        try:
            Subscriber.objects.get(email=request.POST['email'])

            success_ = False
            return HttpResponseRedirect(reverse(failure))

        except Subscriber.DoesNotExist:
            city = request.POST['location'].split(',')[0].strip()
            state = request.POST['location'].split(',')[1].strip()
            location = get_object_or_404(Location, city=city, state=state)

            subscriber = Subscriber(
                email=request.POST['email'],
                location=location
            )
            subscriber.save()
            success_ = True

            return HttpResponseRedirect(reverse(success))

def success(request):
    return render(request, 'success.html')


def failure(request):
    return render(request, 'failure.html')


