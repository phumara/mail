from django.shortcuts import render

from django.utils import timezone

from subscribers.models import Subscriber, Segment

from campaigns.models import Campaign

def home(request):

    total_lists = Segment.objects.count()

    public_lists = 1

    private_lists = total_lists - public_lists

    single_optin = total_lists - 1

    double_optin = total_lists

    total_subscribers = Subscriber.objects.count()

    blocklisted = Subscriber.objects.filter(status='blocklisted').count()

    orphans = 0

    total_campaigns = Campaign.objects.count()

    draft_campaigns = Campaign.objects.filter(status='draft').count()

    finished_campaigns = Campaign.objects.filter(status='finished').count()

    messages_sent = 637

    context = {

        'total_lists': total_lists,

        'public_lists': public_lists,

        'private_lists': private_lists,

        'single_optin': single_optin,

        'double_optin': double_optin,

        'total_subscribers': total_subscribers,

        'blocklisted': blocklisted,

        'orphans': orphans,

        'total_campaigns': total_campaigns,

        'draft_campaigns': draft_campaigns,

        'finished_campaigns': finished_campaigns,

        'messages_sent': messages_sent,

        'current_date': timezone.now().strftime('%a, %d %b %Y'),

    }

    return render(request, 'home.html', context)