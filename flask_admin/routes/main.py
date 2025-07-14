"""
Main routes for Flask Admin Panel
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_admin.auth import login_required
from flask_admin.api_client import api_client
from flask_admin.forms import LoginForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Redirect to admin dashboard"""
    if 'access_token' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if 'access_token' in session and session.get('user', {}).get('is_superuser'):
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # Authenticate with FastAPI backend
        result = api_client.login(form.username.data, form.password.data)
        
        if 'error' not in result:
            # Store session data
            session['access_token'] = result['access_token']
            session['token_type'] = result['token_type']
            session['user'] = result['user']
            
            # Set auth token for API client
            api_client.set_auth_token(result['access_token'])
            
            flash(f'Welcome back, {result["user"]["username"]}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash(f'Login failed: {result["error"]}', 'danger')
    
    return render_template('login.html', form=form)


@main_bp.route('/logout')
def logout():
    """Logout and clear session"""
    # Clear API client auth
    api_client.clear_auth_token()
    
    # Clear session
    session.clear()
    
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard with comprehensive data"""
    # Get system statistics
    stats = api_client.get('/api/v1/admin/stats')

    # Get recent activities
    activities = api_client.get('/api/v1/admin/activities', params={'limit': 10})

    # Get recent users
    recent_users = api_client.get('/api/v1/admin/users/search', params={'page': 1, 'limit': 5})

    if 'error' in stats:
        flash(f"Error loading dashboard: {stats['error']}", 'danger')
        if stats.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
        stats = {}

    if 'error' in activities:
        activities = {'activities': []}

    if 'error' in recent_users:
        recent_users = {'users': []}

    dashboard_data = {
        'stats': stats,
        'activities': activities.get('activities', []),
        'recent_users': recent_users.get('users', []),
        'user': session.get('user')
    }

    return render_template('dashboard.html', **dashboard_data)


@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_data = session.get('user', {})
    return render_template('profile/profile.html', user=user_data)


# Quick access routes for organization management
@main_bp.route('/department')
@main_bp.route('/departments')
@login_required
def departments_redirect():
    """Redirect to organization departments"""
    return redirect(url_for('organization.departments'))


@main_bp.route('/branches')
@login_required
def branches_redirect():
    """Redirect to organization branches"""
    return redirect(url_for('organization.branches'))


@main_bp.route('/positions')
@login_required
def positions_redirect():
    """Redirect to organization positions"""
    return redirect(url_for('organization.positions'))


@main_bp.route('/organization')
@login_required
def organization_redirect():
    """Redirect to organization branches (default)"""
    return redirect(url_for('organization.branches'))


@main_bp.route('/api/health')
@login_required
def health_check():
    """Proxy health check to backend"""
    try:
        import requests
        from flask_admin.config import Config
        response = requests.get(f"{Config.FASTAPI_BASE_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500





# Error handlers
@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
