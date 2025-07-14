"""
Roles and permissions management routes for Flask Admin Panel
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_admin.auth import login_required, super_admin_required
from flask_admin.api_client import api_client
from flask_admin.forms import PermissionForm

roles_bp = Blueprint('roles', __name__)


@roles_bp.route('/permissions')
@login_required
def permissions():
    """List all permissions via FastAPI backend"""
    permissions_result = api_client.get('/api/v1/admin/permissions')
    if 'error' in permissions_result:
        flash(f"Error loading permissions: {permissions_result['error']}", 'danger')
        if permissions_result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
        permissions_data = []
    else:
        permissions_data = permissions_result
    return render_template('permissions.html', permissions=permissions_data)


@roles_bp.route('/roles')
@login_required
def roles():
    """List all roles via FastAPI backend"""
    roles_result = api_client.get('/api/v1/admin/roles')
    permissions_result = api_client.get('/api/v1/admin/permissions')
    if 'error' in roles_result:
        flash(f"Error loading roles: {roles_result['error']}", 'danger')
        if roles_result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
        roles_data = []
    else:
        roles_data = roles_result
    if 'error' in permissions_result:
        permissions_data = []
    else:
        permissions_data = permissions_result
    return render_template('roles.html', roles=roles_data, permissions=permissions_data)


@roles_bp.route('/roles/create', methods=['GET', 'POST'])
@roles_bp.route('/roles/<role_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_role(role_id=None):
    """Create new role or edit existing role"""
    role_data = None
    is_edit = role_id and role_id != '0'
    permissions_result = api_client.get('/api/v1/admin/permissions')
    if 'error' in permissions_result:
        permissions_data = []
    else:
        permissions_data = permissions_result
    
    if is_edit:
        # Get role details from API
        role_result = api_client.get(f'/api/v1/admin/roles/{role_id}')

        if 'error' in role_result:
            flash(f"Error loading role: {role_result['error']}", 'danger')
            if role_result.get('status_code') in [401, 403]:
                return redirect(url_for('main.logout'))
            return redirect(url_for('roles.roles'))

        role_data = role_result

    if request.method == 'POST':
        # Prepare role data
        role_payload = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'permissions': request.form.getlist('permissions')
        }

        if is_edit:
            # Call API to update role
            result = api_client.put(f'/api/v1/admin/roles/{role_id}', role_payload)

            if 'error' in result:
                flash(f"Error updating role: {result['error']}", 'danger')
                if result.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
            else:
                flash(f'Role "{role_payload["name"]}" updated successfully!', 'success')
                return redirect(url_for('roles.roles'))
        else:
            # Call API to create role
            result = api_client.post('/api/v1/admin/roles', role_payload)

            if 'error' in result:
                flash(f"Error creating role: {result['error']}", 'danger')
                if result.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
            else:
                flash(f'Role "{role_payload["name"]}" created successfully!', 'success')
                return redirect(url_for('roles.roles'))

    return render_template('role_form.html', role=role_data, permissions=permissions_data, is_edit=is_edit)


@roles_bp.route('/roles/<role_id>/delete', methods=['POST'])
@super_admin_required
def delete_role(role_id):
    """Delete a role"""
    result = api_client.delete(f'/api/v1/admin/roles/{role_id}')

    if 'error' in result:
        flash(f"Error deleting role: {result['error']}", 'danger')
        if result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
    else:
        flash('Role deleted successfully!', 'success')

    return redirect(url_for('roles.roles'))


@roles_bp.route('/permissions/create', methods=['GET', 'POST'])
@roles_bp.route('/permissions/<permission_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_permission(permission_id=None):
    """Create new permission or edit existing permission"""
    permission_data = None
    is_edit = permission_id and permission_id != '0'
    form = PermissionForm()
    title = 'Edit Permission' if is_edit else 'Create Permission'

    if is_edit:
        # Get permission details from API
        permission_result = api_client.get(f'/api/v1/admin/permissions/{permission_id}')

        if 'error' in permission_result:
            flash(f"Error loading permission: {permission_result['error']}", 'danger')
            if permission_result.get('status_code') in [401, 403]:
                return redirect(url_for('main.logout'))
            return redirect(url_for('roles.permissions'))

        permission_data = permission_result
        if request.method == 'GET':
            form.code.data = permission_data.get('code', '')
            form.label.data = permission_data.get('label', '')
            form.description.data = permission_data.get('description', '')

    if form.validate_on_submit():
        permission_payload = {
            'code': form.code.data,
            'label': form.label.data,
            'description': form.description.data
        }

        if is_edit:
            # Call API to update permission
            result = api_client.put(f'/api/v1/admin/permissions/{permission_id}', permission_payload)

            if 'error' in result:
                flash(f"Error updating permission: {result['error']}", 'danger')
                if result.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
            else:
                flash(f'Permission "{permission_payload["label"]}" updated successfully!', 'success')
                return redirect(url_for('roles.permissions'))
        else:
            # Call API to create permission
            result = api_client.post('/api/v1/admin/permissions', permission_payload)

            if 'error' in result:
                flash(f"Error creating permission: {result['error']}", 'danger')
                if result.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
            else:
                flash(f'Permission "{permission_payload["label"]}" created successfully!', 'success')
                return redirect(url_for('roles.permissions'))

    return render_template('permission_form.html', form=form, title=title, is_edit=is_edit)


@roles_bp.route('/permissions/<permission_id>/delete', methods=['POST'])
@super_admin_required
def delete_permission(permission_id):
    """Delete a permission"""
    result = api_client.delete(f'/api/v1/admin/permissions/{permission_id}')

    if 'error' in result:
        flash(f"Error deleting permission: {result['error']}", 'danger')
        if result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
    else:
        flash('Permission deleted successfully!', 'success')

    return redirect(url_for('roles.permissions'))
