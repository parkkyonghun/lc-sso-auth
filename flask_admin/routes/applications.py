"""
Application management routes for Flask Admin Panel
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_admin.auth import login_required
from flask_admin.api_client import api_client

applications_bp = Blueprint('applications', __name__, url_prefix='/applications')


@applications_bp.route('/')
@login_required
def applications():
    """List all applications with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '', type=str)
    page_size = request.args.get('limit', 20, type=int)
    
    params = {
        'page': page,
        'limit': page_size
    }
    if search:
        params['q'] = search

    apps_data = api_client.get('/api/v1/admin/applications', params=params)

    if 'error' in apps_data:
        flash(f"Error loading applications: {apps_data['error']}", 'danger')
        if apps_data.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
        apps_data = {'applications': [], 'total': 0, 'page': 1, 'pages': 1}

    return render_template('applications.html', 
                         applications=apps_data.get('applications', []),
                         total=apps_data.get('total', 0),
                         page=apps_data.get('page', 1),
                         pages=apps_data.get('pages', 1),
                         search=search)


@applications_bp.route('/create', methods=['GET', 'POST'])
@applications_bp.route('/<app_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_application(app_id=None):
    """Create new application or edit existing application"""
    app_data = None
    is_edit = app_id and app_id != '0'
    
    if is_edit:
        # Get application details from API
        app_result = api_client.get(f'/api/v1/admin/applications/{app_id}')

        if 'error' in app_result:
            flash(f"Error loading application: {app_result['error']}", 'danger')
            if app_result.get('status_code') in [401, 403]:
                return redirect(url_for('main.logout'))
            return redirect(url_for('applications.applications'))

        app_data = app_result

    if request.method == 'POST':
        # Prepare application data
        app_payload = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'website_url': request.form.get('website_url'),
            'privacy_policy_url': request.form.get('privacy_policy_url'),
            'terms_of_service_url': request.form.get('terms_of_service_url'),
            'logo_url': request.form.get('logo_url'),
            'is_active': 'is_active' in request.form,
            'is_confidential': 'is_confidential' in request.form,
            'require_consent': 'require_consent' in request.form,
            'redirect_uris': request.form.get('redirect_uris', '').split('\n'),
            'allowed_scopes': request.form.get('allowed_scopes', '').split('\n'),
            'grant_types': request.form.get('grant_types', '').split('\n'),
            'response_types': request.form.get('response_types', '').split('\n'),
            'access_token_lifetime': int(request.form.get('access_token_lifetime', 3600)),
            'refresh_token_lifetime': int(request.form.get('refresh_token_lifetime', 86400)),
            'token_endpoint_auth_method': request.form.get('token_endpoint_auth_method', 'client_secret_basic')
        }

        # Clean up empty strings from lists
        for key in ['redirect_uris', 'allowed_scopes', 'grant_types', 'response_types']:
            app_payload[key] = [uri.strip() for uri in app_payload[key] if uri.strip()]

        if is_edit:
            # Call API to update application
            result = api_client.put(f'/api/v1/admin/applications/{app_id}', app_payload)

            if 'error' in result:
                flash(f"Error updating application: {result['error']}", 'danger')
                if result.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
            else:
                flash(f'Application "{app_payload["name"]}" updated successfully!', 'success')
                return redirect(url_for('applications.applications'))
        else:
            # Call API to create application
            result = api_client.post('/api/v1/admin/applications', app_payload)

            if 'error' in result:
                flash(f"Error creating application: {result['error']}", 'danger')
                if result.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
            else:
                flash(f'Application "{app_payload["name"]}" created successfully!', 'success')
                return redirect(url_for('applications.applications'))

    return render_template('application_form.html', application=app_data, is_edit=is_edit)


@applications_bp.route('/<app_id>/delete', methods=['POST'])
@login_required
def delete_application(app_id):
    """Delete an application"""
    result = api_client.delete(f'/api/v1/admin/applications/{app_id}')

    if 'error' in result:
        flash(f"Error deleting application: {result['error']}", 'danger')
        if result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
    else:
        flash('Application deleted successfully!', 'success')

    return redirect(url_for('applications.applications'))


@applications_bp.route('/<app_id>/regenerate-secret', methods=['POST'])
@login_required
def regenerate_secret(app_id):
    """Regenerate application client secret"""
    result = api_client.post(f'/api/v1/admin/applications/{app_id}/regenerate-secret')

    if 'error' in result:
        flash(f"Error regenerating secret: {result['error']}", 'danger')
        if result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
    else:
        flash('Client secret regenerated successfully!', 'success')

    return redirect(url_for('applications.applications'))


@applications_bp.route('/<app_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(app_id):
    """Toggle application active status"""
    result = api_client.post(f'/api/v1/admin/applications/{app_id}/toggle-status')

    if 'error' in result:
        flash(f"Error toggling application status: {result['error']}", 'danger')
        if result.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
    else:
        flash('Application status updated successfully!', 'success')

    return redirect(url_for('applications.applications'))
