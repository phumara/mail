from django import forms

from .models import Campaign, EmailTemplate

class CampaignForm(forms.ModelForm):

    class Meta:

        model = Campaign

        fields = ['name', 'subject', 'from_name', 'from_email', 'reply_to_email', 'template', 'html_content', 'text_content', 'subscriber_segments', 'smtp_provider', 'scheduled_at']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['template'].queryset = EmailTemplate.objects.all()

        self.fields['template'].empty_label = 'Select a template'
        
        # Make certain fields optional in the form
        self.fields['from_name'].required = False
        self.fields['from_email'].required = False
        self.fields['reply_to_email'].required = False
        self.fields['text_content'].required = False
        self.fields['scheduled_at'].required = False
        self.fields['template'].required = False
        
        # Set up subscriber_lists field as a multiple select
        self.fields['subscriber_segments'].widget = forms.CheckboxSelectMultiple()
        self.fields['subscriber_segments'].help_text = 'Select target subscriber segments (optional)'
        
        # Add placeholders and help text
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter campaign name'})
        self.fields['subject'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter email subject'})
        self.fields['from_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'From Name'})
        self.fields['from_email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'sender@example.com'})
        self.fields['reply_to_email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'replyto@example.com'})
        self.fields['template'].widget.attrs.update({'class': 'form-control'})
        self.fields['html_content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'HTML email content', 'rows': 10})
        self.fields['text_content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Plain text email content (optional)', 'rows': 5})
        self.fields['scheduled_at'].widget.attrs.update({'class': 'form-control', 'placeholder': 'YYYY-MM-DD HH:MM:SS'})

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