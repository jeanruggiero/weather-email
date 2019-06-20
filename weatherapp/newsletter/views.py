from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Subscriber, Location


def newsletter_signup(request):
    locations = Location.objects.order_by('city')
    if request.method == 'GET':
        return render(request, 'newsletter_signup.html', {'locations': locations, 'success': False})
    if request.method == 'POST':
        try:
            Subscriber.objects.get(email=request.POST['email'])
            #return HttpResponseRedirect(reverse(failure))

        except Subscriber.DoesNotExist:
            city = request.POST['location'].split(',')[0].strip()
            state = request.POST['location'].split(',')[1].strip()
            location = get_object_or_404(Location, city=city, state=state)

            subscriber = Subscriber(
                email=request.POST['email'],
                location=location
            )
            subscriber.save()

            return render(request, 'newsletter_signup.html', {'locations': locations, 'success': True})

def success(request):
    return render(request, 'success.html')


def failure(request):
    return render(request, 'failure.html')


