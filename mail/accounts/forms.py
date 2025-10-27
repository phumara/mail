from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationFormWithPermissions(UserCreationForm):
    """Form for creating users with custom permissions"""
    
    can_manage_subscribers = forms.BooleanField(
        required=False,
        label='Can manage all subscribers',
        help_text='Allow this user to view, edit, and delete all subscribers'
    )
    
    can_add_own_subscribers = forms.BooleanField(
        required=False,
        label='Can add own subscribers',
        initial=True,
        help_text='Allow this user to create and manage their own subscribers'
    )
    
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional. First name of the user.'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional. Last name of the user.'
    )
    
    is_staff = forms.BooleanField(
        required=False,
        label='Staff status',
        help_text='Designates whether the user can log into this admin site.'
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Active',
        help_text='Designates whether this user should be treated as active.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'password1', 'password2', 'is_staff', 'is_active',
                 'can_manage_subscribers', 'can_add_own_subscribers')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True
        
        # Set up form field order
        field_order = [
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2', 'is_staff', 'is_active',
            'can_manage_subscribers', 'can_add_own_subscribers'
        ]
        
        # Reorder fields
        self.fields = {k: self.fields[k] for k in field_order if k in self.fields}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.is_active = self.cleaned_data.get('is_active', True)
        user.can_manage_subscribers = self.cleaned_data.get('can_manage_subscribers', False)
        user.can_add_own_subscribers = self.cleaned_data.get('can_add_own_subscribers', True)
        
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Form for editing existing users"""
    
    can_manage_subscribers = forms.BooleanField(
        required=False,
        label='Can manage all subscribers',
        help_text='Allow this user to view, edit, and delete all subscribers'
    )
    
    can_add_own_subscribers = forms.BooleanField(
        required=False,
        label='Can add own subscribers',
        help_text='Allow this user to create and manage their own subscribers'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'is_staff', 'is_active', 'can_manage_subscribers', 
                 'can_add_own_subscribers')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True