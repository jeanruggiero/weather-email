from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Subscriber, Location


def newsletter_signup(request):
    locations = Location.objects.order_by('city')
    if request.method == 'GET':
        return render(request, 'newsletter_signup.html', {'locations': locations, 'status': None})
    if request.method == 'POST':
        try:
            # If the subscriber exists, don't update the database and display a message to user
            Subscriber.objects.get(email=request.POST['email'])
            return render(request, 'newsletter_signup.html', {'locations': locations, 'status': 'failure'})

        except Subscriber.DoesNotExist:
            # If the subscriber does not exist, add them to the database
            city = request.POST['location'].split(',')[0].strip()
            state = request.POST['location'].split(',')[1].strip()
            location = get_object_or_404(Location, city=city, state=state)

            subscriber = Subscriber(
                email=request.POST['email'],
                location=location
            )
            subscriber.save()

            return render(request, 'newsletter_signup.html', {'locations': locations, 'status': 'success'})
