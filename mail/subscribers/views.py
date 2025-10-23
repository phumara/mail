from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages

from django.http import HttpResponse

import csv

import io

from .models import Subscriber, Segment

from .forms import SubscriberForm, SegmentForm

def subscriber_list(request):

    subscribers = Subscriber.objects.all()

    return render(request, 'subscribers/list.html', {'subscribers': subscribers})

def subscriber_create(request):

    if request.method == 'POST':

        form = SubscriberForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, 'Subscriber added successfully.')

            return redirect('subscriber_list')

    else:

        form = SubscriberForm()

    return render(request, 'subscribers/create.html', {'form': form})

def subscriber_edit(request, pk):

    subscriber = get_object_or_404(Subscriber, pk=pk)

    if request.method == 'POST':

        form = SubscriberForm(request.POST, instance=subscriber)

        if form.is_valid():

            form.save()

            messages.success(request, 'Subscriber updated successfully.')

            return redirect('subscriber_list')

    else:

        form = SubscriberForm(instance=subscriber)

    return render(request, 'subscribers/edit.html', {'form': form})

def subscriber_delete(request, pk):

    subscriber = get_object_or_404(Subscriber, pk=pk)

    if request.method == 'POST':

        subscriber.delete()

        messages.success(request, 'Subscriber deleted successfully.')

        return redirect('subscriber_list')

    return render(request, 'subscribers/delete.html', {'subscriber': subscriber})

def subscriber_import(request):

    segments = Segment.objects.all()

    if request.method == 'POST' and request.FILES['csv_file']:

        csv_file = request.FILES['csv_file']

        segment_id = request.POST.get('segment')

        if not csv_file.name.endswith('.csv'):

            messages.error(request, 'File is not CSV type')

            return redirect('subscriber_import')

        if not segment_id:

            messages.error(request, 'Please select a list.')

            return redirect('subscriber_import')

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

        return redirect('subscriber_list')

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

            return redirect('segment_list')

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

            return redirect('segment_list')

    else:

        form = SegmentForm(instance=segment)

    return render(request, 'subscribers/segment_edit.html', {'form': form})

def segment_delete(request, pk):

    segment = get_object_or_404(Segment, pk=pk)

    if request.method == 'POST':

        segment.delete()

        messages.success(request, 'List deleted successfully.')

        return redirect('segment_list')

    return render(request, 'subscribers/segment_delete.html', {'segment': segment})

def segment_subscribers(request, pk):

    segment = get_object_or_404(Segment, pk=pk)

    subscribers = segment.subscribers.all()

    return render(request, 'subscribers/segment_subscribers.html', {'segment': segment, 'subscribers': subscribers})