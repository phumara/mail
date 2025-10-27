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
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'optin': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
        }