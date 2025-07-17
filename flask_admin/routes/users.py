"""
User management routes for Flask Admin Panel
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_admin.auth import login_required, super_admin_required
from flask_admin.api_client import api_client, get_branches, get_departments, get_positions
from flask_admin.forms import UserForm
from datetime import datetime

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@login_required
def users():
    """List all users with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '', type=str)
    page_size = request.args.get('limit', 20, type=int)
    
    # Check for readonly mode
    user = session.get('user', {})
    appadmin_readonly = not user.get('is_superuser', False)
    
    params = {
        'page': page,
        'limit': page_size
    }
    if search:
        params['q'] = search

    result = api_client.get('/api/v1/admin/users/search', params=params)

    if 'error' in result:
        flash(f"Error loading users: {result['error']}", 'danger')
        if result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
        result = {'users': [], 'total': 0, 'page': 1, 'pages': 1}

    users_data = result.get('users', [])
    for user in users_data:
        if user.get('created_at'):
            try:
                user['created_at'] = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                user['created_at'] = None  # Or handle as an error
        if user.get('last_login'):
            try:
                user['last_login'] = datetime.fromisoformat(user['last_login'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                user['last_login'] = None


    # Create data object for template
    data = {
        'users': users_data,
        'total': result.get('total', 0),
        'page': result.get('page', 1),
        'pages': result.get('pages', 1)
    }

    return render_template('users.html',
                         data=data,
                         search=search,
                         appadmin_readonly=appadmin_readonly)


@users_bp.route('/create', methods=['GET', 'POST'])
@users_bp.route('/<user_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_user(user_id=None):
    """Create new user or edit existing user"""
    form = UserForm()
    user_data = None
    is_edit = user_id and user_id != '0'
    
    # Populate form choices
    form.branch.choices = [('', 'Select Branch')] + [(str(b['id']), b['branch_name']) for b in get_branches()]
    form.department.choices = [('', 'Select Department')] + [(str(d['id']), d['department_name']) for d in get_departments()]
    form.position.choices = [('', 'Select Position')] + [(str(p['id']), p['title']) for p in get_positions()]
    
    if is_edit:
        # Get user details from API
        user_result = api_client.get(f'/api/v1/admin/users/{user_id}')

        if 'error' in user_result:
            flash(f"Error loading user: {user_result['error']}", 'danger')
            if user_result.get('status_code') in [401, 403]:
                return redirect(url_for('main.logout'))
            return redirect(url_for('users.users'))

        user_data = user_result
        
        # Populate form with user data
        if request.method == 'GET':
            form.username.data = user_data.get('username', '')
            form.email.data = user_data.get('email', '')
            form.full_name.data = user_data.get('full_name', '')
            form.is_active.data = user_data.get('is_active', True)
            form.is_verified.data = user_data.get('is_verified', False)
            form.is_superuser.data = user_data.get('is_superuser', False)
            form.bio.data = user_data.get('bio', '')
            form.timezone.data = user_data.get('timezone', '')
            form.language.data = user_data.get('language', '')
            form.branch.data = str(user_data.get('branch_id', '')) if user_data.get('branch_id') else ''
            form.department.data = str(user_data.get('department_id', '')) if user_data.get('department_id') else ''
            form.position.data = str(user_data.get('position_id', '')) if user_data.get('position_id') else ''
            form.manager_name.data = user_data.get('manager_name', '')

    if form.validate_on_submit():
        # Prepare user data
        user_payload = {
            'username': form.username.data,
            'email': form.email.data,
            'full_name': form.full_name.data,
            'is_active': form.is_active.data,
            'is_verified': form.is_verified.data,
            'is_superuser': form.is_superuser.data,
            'bio': form.bio.data,
            'timezone': form.timezone.data,
            'language': form.language.data,
            'branch_id': form.branch.data if form.branch.data else None,
            'department_id': form.department.data if form.department.data else None,
            'position_id': form.position.data if form.position.data else None,
            'manager_name': form.manager_name.data
        }

        # Only include password if provided
        if form.password.data:
            user_payload['password'] = form.password.data

        if is_edit:
            # Call API to update user
            result = api_client.put(f'/api/v1/admin/users/{user_id}', user_payload)

            if 'error' in result:
                flash(f"Error updating user: {result['error']}", 'danger')
                if result.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
            else:
                flash(f'User "{form.username.data}" updated successfully!', 'success')
                return redirect(url_for('users.users'))
        else:
            # Call FastAPI to create user
            result = api_client.post('/api/v1/admin/users', user_payload)

            if 'error' in result:
                flash(f"Error creating user: {result['error']}", 'danger')
                if result.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
            else:
                flash(f'User "{form.username.data}" created successfully!', 'success')
                return redirect(url_for('users.users'))

    title = 'Edit User' if is_edit else 'Create User'
    return render_template('user_form.html', form=form, user=user_data, is_edit=is_edit, title=title)


@users_bp.route('/<user_id>/delete', methods=['POST'])
@super_admin_required
def delete_user(user_id):
    """Delete a user"""
    result = api_client.delete(f'/api/v1/admin/users/{user_id}')

    if 'error' in result:
        flash(f"Error deleting user: {result['error']}", 'danger')
        if result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
    else:
        flash('User deleted successfully!', 'success')

    return redirect(url_for('users.users'))


@users_bp.route('/<user_id>/unlock', methods=['POST'])
@super_admin_required
def unlock_user(user_id):
    """Unlock a user account"""
    result = api_client.post(f'/api/v1/admin/users/{user_id}/unlock')

    if 'error' in result:
        flash(f"Error unlocking user: {result['error']}", 'danger')
        if result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
    else:
        flash('User account unlocked successfully!', 'success')

    return redirect(url_for('users.users'))
