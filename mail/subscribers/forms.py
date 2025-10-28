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

class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Import subscribers from a CSV file.',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    segment = forms.ModelChoiceField(
        queryset=Segment.objects.all(),
        label='List',
        help_text='Select the list to add subscribers to.',
        widget=forms.Select(attrs={'class': 'form-control'})
    )