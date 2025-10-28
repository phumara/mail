from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
import datetime


def home(request):
    """Home page view with dashboard data"""
    if request.user.is_authenticated:
        # Get some basic stats for the dashboard
        try:
            from campaigns.models import Campaign, SMTPProvider, EmailLog
            from subscribers.models import Subscriber, Segment

            total_lists = Segment.objects.count()
            total_subscribers = Subscriber.objects.count()
            total_campaigns = Campaign.objects.count()
            messages_sent = EmailLog.objects.count()
        except:
            total_lists = 0
            total_subscribers = 0
            total_campaigns = 0
            messages_sent = 0

        context = {
            'total_lists': total_lists,
            'total_subscribers': total_subscribers,
            'total_campaigns': total_campaigns,
            'messages_sent': messages_sent,
            'now': datetime.datetime.now(),
        }
        return render(request, 'home.html', context)
    else:
        return redirect('login')


def custom_logout(request):
    """Custom logout view that handles both GET and POST requests"""
    if request.method in ['POST', 'GET']:
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('login')  # Redirect to login page instead of logout template
    return redirect('home')
