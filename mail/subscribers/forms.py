from django import forms

from .models import Subscriber, Segment

class SubscriberForm(forms.ModelForm):

    class Meta:

        model = Subscriber

        fields = ['email', 'name']

class SegmentForm(forms.ModelForm):

    class Meta:

        model = Segment

        fields = ['name', 'description', 'type', 'optin', 'tags']