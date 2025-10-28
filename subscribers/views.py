from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import csv
import io
from email_validator import validate_email, EmailNotValidError

from .models import Subscriber, Segment

from .forms import SubscriberForm, SegmentForm, CSVImportForm

@login_required
def subscriber_list(request):
    """List subscribers with permission-based filtering and search"""
    # Check if user has global subscriber management permission
    if request.user.can_manage_subscribers:
        # User can see all subscribers
        subscribers_list = Subscriber.objects.all()
    else:
        # User can only see subscribers they created
        subscribers_list = Subscriber.objects.filter(created_by=request.user)
        if not subscribers_list.exists():
            messages.info(request, "You haven't created any subscribers yet.")

    search_query = request.GET.get('q')
    if search_query:
        subscribers_list = subscribers_list.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(status__icontains=search_query)
        ).distinct()

    paginator = Paginator(subscribers_list, 10)  # Show 10 subscribers per page
    page_number = request.GET.get('page')
    subscribers = paginator.get_page(page_number)

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
    invalid_emails = []
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            segment = form.cleaned_data['segment']
            
            try:
                file_data = csv_file.read().decode('utf-8')
                io_string = io.StringIO(file_data)
                next(io_string)  # skip header

                imported_count = 0
                for row in csv.reader(io_string, delimiter=','):
                    if len(row) >= 1:
                        email = row[0].strip()
                        name = row[1].strip() if len(row) > 1 else ''

                        if not email:
                            continue

                        try:
                            # Validate email
                            validate_email(email, check_deliverability=False)
                            
                            # Create or update subscriber
                            subscriber, created = Subscriber.objects.get_or_create(
                                email=email,
                                defaults={'name': name, 'created_by': request.user if request.user.is_authenticated else None}
                            )
                            segment.subscribers.add(subscriber)
                            
                            if created:
                                imported_count += 1

                        except EmailNotValidError as e:
                            invalid_emails.append({'email': email, 'reason': str(e)})

                if imported_count > 0:
                    messages.success(request, f'{imported_count} subscribers imported and added to {segment.name}.')
                
                if not invalid_emails:
                    return redirect('subscribers:subscriber_list')

            except Exception as e:
                messages.error(request, f'Error processing file: {e}')

    else:
        form = CSVImportForm()

    return render(request, 'subscribers/import.html', {
        'form': form,
        'invalid_emails': invalid_emails
    })

def subscriber_bounces(request):

    bounces = Subscriber.objects.filter(status='bounced')

    return render(request, 'subscribers/bounces.html', {'bounces': bounces})

def segment_list(request):
    segments_list = Segment.objects.all()
    search_query = request.GET.get('q')
    if search_query:
        segments_list = segments_list.filter(name__icontains=search_query)

    paginator = Paginator(segments_list, 10)  # Show 10 segments per page
    page_number = request.GET.get('page')
    segments = paginator.get_page(page_number)
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
        action = request.POST.get('action')
        subscriber_ids = request.POST.getlist('subscriber_ids')

        if action == 'add':
            if not subscriber_ids:
                messages.warning(request, 'No subscribers selected to add.')
                return redirect('subscribers:segment_subscribers', pk=segment.pk)
            subscribers_to_add = Subscriber.objects.filter(pk__in=subscriber_ids)
            segment.subscribers.add(*subscribers_to_add)
            messages.success(request, f'{subscribers_to_add.count()} subscribers added to {segment.name}.')

        elif action == 'remove':
            if not subscriber_ids:
                messages.warning(request, 'No subscribers selected to remove.')
                return redirect('subscribers:segment_subscribers', pk=segment.pk)
            subscribers_to_remove = Subscriber.objects.filter(pk__in=subscriber_ids)
            segment.subscribers.remove(*subscribers_to_remove)
            messages.success(request, f'{subscribers_to_remove.count()} subscribers removed from {segment.name}.')

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
    """AJAX view to search for all subscribers (not filtering by segment)."""
    query = request.GET.get('q', '')

    subscribers = []
    if query:
        # Search for all subscribers matching the query
        search_results = Subscriber.objects.filter(
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