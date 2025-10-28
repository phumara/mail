from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserCreationFormWithPermissions, UserEditForm

User = get_user_model()

def is_admin(user):
    """Check if user is admin or superuser"""
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        form = UserCreationFormWithPermissions(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserCreationFormWithPermissions()
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Create User',
        'button_text': 'Create User'
    })

@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    """Edit existing user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': f'Edit User: {user.username}',
        'button_text': 'Update User',
        'editing': True
    })

@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    """Delete user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Prevent admin from deleting themselves
        if user == request.user:
            messages.error(request, 'You cannot delete your own account!')
            return redirect('accounts:user_list')
        
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

@login_required
def user_profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {'user': request.user})