from django import forms
from .models import Media, Campaign, EmailTemplate, SMTPProvider, Attachment

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
from subscribers.models import Segment

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['name', 'file']


class CampaignForm(forms.ModelForm):

    class Meta:

        model = Campaign

        fields = ['name', 'subject', 'from_name', 'from_email', 'reply_to_email', 'cc_recipients', 'bcc_recipients', 'template', 'html_content', 'text_content', 'subscriber_segments', 'smtp_provider']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['template'].queryset = EmailTemplate.objects.all()

        self.fields['template'].empty_label = 'Select a template'
        
        # Make certain fields optional in the form
        self.fields['from_name'].required = False
        self.fields['from_email'].required = False
        self.fields['reply_to_email'].required = False
        self.fields['text_content'].required = False

        self.fields['template'].required = False

        # Set up subscriber_segments field as a multiple select
        self.fields['subscriber_segments'].widget = forms.CheckboxSelectMultiple()
        self.fields['subscriber_segments'].queryset = Segment.objects.all()
        self.fields['subscriber_segments'].help_text = 'Select target subscriber segments (optional)'

        # Configure smtp_provider field
        self.fields['smtp_provider'].queryset = SMTPProvider.objects.filter(is_active=True)
        self.fields['smtp_provider'].widget.attrs.update({'class': 'form-control'})
        self.fields['smtp_provider'].empty_label = 'Use default if available'
        
        # Add placeholders and help text
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter campaign name'})
        self.fields['subject'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter email subject'})
        self.fields['from_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'From Name'})
        self.fields['from_email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'sender@example.com'})
        self.fields['reply_to_email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'replyto@example.com'})
        self.fields['cc_recipients'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Comma-separated emails for CC'})
        self.fields['bcc_recipients'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Comma-separated emails for BCC'})
        self.fields['template'].widget.attrs.update({'class': 'form-control'})
        self.fields['html_content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'HTML email content', 'rows': 10})
        self.fields['text_content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Plain text email content (optional)', 'rows': 5})


    def clean(self):
        cleaned_data = super().clean()
        template = cleaned_data.get('template')
        html_content = cleaned_data.get('html_content')
        
        # Ensure either template or html_content is provided
        if not template and not html_content:
            raise forms.ValidationError(
                'Either select a template or provide HTML content for the campaign.'
            )
        
        return cleaned_data

class TemplateForm(forms.ModelForm):

    class Meta:

        model = EmailTemplate

        fields = ['name', 'subject', 'html_content', 'text_content', 'is_active']

        widgets = {

            'name': forms.TextInput(attrs={'placeholder': 'Template Name'}),

            'subject': forms.TextInput(attrs={'placeholder': 'Email Subject'}),

            'html_content': forms.Textarea(attrs={'placeholder': 'HTML Email Content', 'rows': 10}),

            'text_content': forms.Textarea(attrs={'placeholder': 'Plain Text Email Content (optional)', 'rows': 5}),

            'is_active': forms.CheckboxInput(attrs={'placeholder': 'Set as Active'}),

        }

class SMTPProviderForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = SMTPProvider
        fields = [
            'name', 'provider_type', 'is_active', 'is_default',
            'host', 'port', 'use_tls', 'use_ssl', 'skip_tls_verify',
            'username', 'password', 'api_key', 'api_secret',
            'emails_per_day', 'emails_per_hour', 'emails_per_second',
            'from_email', 'from_name', 'reply_to_email',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'provider_type': forms.Select(attrs={'class': 'form-control'}),
            'host': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'use_ssl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'skip_tls_verify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            # 'password': forms.PasswordInput(attrs={'class': 'form-control'}), # Handled above
            'api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'api_secret': forms.TextInput(attrs={'class': 'form-control'}),
            'emails_per_day': forms.NumberInput(attrs={'class': 'form-control'}),
            'emails_per_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'emails_per_second': forms.NumberInput(attrs={'class': 'form-control'}),
            'from_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'from_name': forms.TextInput(attrs={'class': 'form-control'}),
            'reply_to_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        provider = super().save(commit=False)
        if self.cleaned_data['password']:
            provider.password = self.cleaned_data['password']
        if commit:
            provider.save()
        return provider