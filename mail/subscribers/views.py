from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import csv
import io

from .models import Subscriber, Segment

from .forms import SubscriberForm, SegmentForm

@login_required
def subscriber_list(request):
    """List subscribers with permission-based filtering"""
    # Check if user has global subscriber management permission
    if request.user.can_manage_subscribers:
        # User can see all subscribers
        subscribers = Subscriber.objects.all()
    else:
        # User can only see subscribers they created
        subscribers = Subscriber.objects.filter(created_by=request.user)
        if not subscribers.exists():
            messages.info(request, 'You haven\'t created any subscribers yet.')

    return render(request, 'subscribers/list.html', {'subscribers': subscribers})

@login_required
def subscriber_create(request):
    """Create subscriber with permission check"""
    # Check if user has permission to add subscribers
    if not request.user.can_add_own_subscribers:
        messages.error(request, 'You don\'t have permission to add subscribers.')
        return redirect('subscribers:subscriber_list')

    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save(commit=False)
            # Set the created_by field to current user
            subscriber.created_by = request.user
            subscriber.save()
            messages.success(request, 'Subscriber added successfully.')
            return redirect('subscribers:subscriber_list')
    else:
        form = SubscriberForm()

    return render(request, 'subscribers/create.html', {'form': form})

@login_required
def subscriber_edit(request, pk):
    """Edit subscriber with permission check"""
    subscriber = get_object_or_404(Subscriber, pk=pk)
    
    # Check if user has permission to edit this subscriber
    if not request.user.can_manage_subscribers and subscriber.created_by != request.user:
        messages.error(request, 'You don\'t have permission to edit this subscriber.')
        return redirect('subscribers:subscriber_list')

    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscriber updated successfully.')
            return redirect('subscribers:subscriber_list')
    else:
        form = SubscriberForm(instance=subscriber)

    return render(request, 'subscribers/edit.html', {'form': form})

@login_required
def subscriber_delete(request, pk):
    """Delete subscriber with permission check"""
    subscriber = get_object_or_404(Subscriber, pk=pk)
    
    # Check if user has permission to delete this subscriber
    if not request.user.can_manage_subscribers and subscriber.created_by != request.user:
        messages.error(request, 'You don\'t have permission to delete this subscriber.')
        return redirect('subscribers:subscriber_list')

    if request.method == 'POST':
        subscriber.delete()
        messages.success(request, 'Subscriber deleted successfully.')
        return redirect('subscribers:subscriber_list')

    return render(request, 'subscribers/delete.html', {'subscriber': subscriber})

def subscriber_import(request):

    segments = Segment.objects.all()

    if request.method == 'POST' and request.FILES['csv_file']:

        csv_file = request.FILES['csv_file']

        segment_id = request.POST.get('segment')

        if not csv_file.name.endswith('.csv'):

            messages.error(request, 'File is not CSV type')

            return redirect('subscribers:subscriber_import')

        if not segment_id:

            messages.error(request, 'Please select a list.')

            return redirect('subscribers:subscriber_import')

        segment = get_object_or_404(Segment, pk=segment_id)

        file_data = csv_file.read().decode('utf-8')

        io_string = io.StringIO(file_data)

        next(io_string)  # skip header

        imported_count = 0

        for row in csv.reader(io_string, delimiter=','):

            if len(row) >= 2:

                email = row[0].strip()

                name = row[1].strip() if len(row) > 1 else ''

                if email:

                    subscriber, created = Subscriber.objects.get_or_create(email=email, defaults={'name': name})

                    segment.subscribers.add(subscriber)

                    if created:

                        imported_count += 1

        messages.success(request, f'{imported_count} subscribers imported and added to {segment.name}.')

        return redirect('subscribers:subscriber_list')

    return render(request, 'subscribers/import.html', {'segments': segments})

def subscriber_bounces(request):

    bounces = Subscriber.objects.filter(status='bounced')

    return render(request, 'subscribers/bounces.html', {'bounces': bounces})

def segment_list(request):

    segments = Segment.objects.all()

    return render(request, 'subscribers/segment_list.html', {'segments': segments})

def segment_create(request):

    if request.method == 'POST':

        form = SegmentForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, 'List created successfully.')

            return redirect('subscribers:segment_list')

    else:

        form = SegmentForm()

    return render(request, 'subscribers/segment_create.html', {'form': form})

def segment_edit(request, pk):

    segment = get_object_or_404(Segment, pk=pk)

    if request.method == 'POST':

        form = SegmentForm(request.POST, instance=segment)

        if form.is_valid():

            form.save()

            messages.success(request, 'List updated successfully.')

            return redirect('subscribers:segment_list')

    else:

        form = SegmentForm(instance=segment)

    return render(request, 'subscribers/segment_edit.html', {'form': form})

def segment_delete(request, pk):

    segment = get_object_or_404(Segment, pk=pk)

    if request.method == 'POST':

        segment.delete()

        messages.success(request, 'List deleted successfully.')

        return redirect('subscribers:segment_list')

    return render(request, 'subscribers/segment_delete.html', {'segment': segment})

def segment_subscribers(request, pk):

    segment = get_object_or_404(Segment, pk=pk)

    if request.method == 'POST':
        subscriber_ids = request.POST.getlist('subscriber_ids')
        print(f"Received subscriber_ids: {subscriber_ids}") # Debug print
        if not subscriber_ids:
            messages.warning(request, 'No subscribers selected to add.')
            return redirect('subscribers:segment_subscribers', pk=segment.pk)
        subscribers_to_add = Subscriber.objects.filter(pk__in=subscriber_ids)
        segment.subscribers.add(*subscribers_to_add)
        messages.success(request, f'{subscribers_to_add.count()} subscribers added to {segment.name}.')
        return redirect('subscribers:segment_subscribers', pk=segment.pk)

    subscribers_in_segment = segment.subscribers.all()
    
    search_query = request.GET.get('q')
    search_results = Subscriber.objects.none() # Initialize as empty queryset

    if search_query:
        search_results = Subscriber.objects.exclude(segments=segment).filter(
            Q(email__icontains=search_query) | Q(name__icontains=search_query) | Q(status__icontains=search_query)
        ).distinct()

    return render(request, 'subscribers/segment_subscribers.html', {'segment': segment, 'subscribers': subscribers_in_segment, 'search_results': search_results, 'search_query': search_query})


def search_subscribers(request):
    """AJAX view to search for subscribers not in a given segment."""
    query = request.GET.get('q', '')
    segment_id = request.GET.get('segment_id')
    segment = get_object_or_404(Segment, pk=segment_id)

    subscribers = []
    if query:
        # Search for subscribers not in the current segment
        search_results = Subscriber.objects.exclude(segments=segment).filter(
            Q(email__icontains=query) | Q(name__icontains=query) | Q(status__icontains=query)
        ).distinct()

        for sub in search_results:
            subscribers.append({
                'pk': sub.pk,
                'email': sub.email,
                'name': sub.name,
                'status': sub.status,
            })
    return JsonResponse({'subscribers': subscribers})