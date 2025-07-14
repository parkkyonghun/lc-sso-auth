"""
Analytics routes for Flask Admin Panel
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_admin.auth import login_required
from flask_admin.api_client import api_client

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/system-stats')
@login_required
def system_stats():
    """System statistics page"""
    stats_data = api_client.get('/api/v1/admin/stats/system')
    
    if 'error' in stats_data:
        flash(f"Error loading system stats: {stats_data['error']}", 'danger')
        if stats_data.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
        stats_data = {}
    
    return render_template('analytics/system_stats.html', stats=stats_data)


@analytics_bp.route('/user-stats')
@login_required
def user_stats():
    """User analytics page"""
    stats_data = api_client.get('/api/v1/admin/stats/users')
    
    if 'error' in stats_data:
        flash(f"Error loading user stats: {stats_data['error']}", 'danger')
        if stats_data.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
        stats_data = {}
    
    return render_template('analytics/user_stats.html', stats=stats_data)


@analytics_bp.route('/activities')
@login_required
def activities():
    """Activity logs page"""
    # Get filter parameters
    activity_type = request.args.get('type', '')
    date_from = request.args.get('from', '')
    date_to = request.args.get('to', '')
    user_filter = request.args.get('user', '')
    limit = request.args.get('limit', 50, type=int)
    page = request.args.get('page', 1, type=int)
    
    # Build API parameters
    params = {
        'limit': limit,
        'page': page
    }
    
    if activity_type:
        params['type'] = activity_type
    if date_from:
        params['from'] = date_from
    if date_to:
        params['to'] = date_to
    if user_filter:
        params['user'] = user_filter
    
    activities_data = api_client.get('/api/v1/admin/activities', params=params)
    
    if 'error' in activities_data:
        flash(f"Error loading activities: {activities_data['error']}", 'danger')
        if activities_data.get('status_code') in [401, 403]:
            return redirect(url_for('main.logout'))
        activities_data = {'activities': [], 'total': 0, 'page': 1, 'pages': 1}
    
    return render_template('analytics/activities.html', 
                         activities=activities_data.get('activities', []),
                         total=activities_data.get('total', 0),
                         page=activities_data.get('page', 1),
                         pages=activities_data.get('pages', 1),
                         filters={
                             'type': activity_type,
                             'from': date_from,
                             'to': date_to,
                             'user': user_filter
                         })


@analytics_bp.route('/reports')
@login_required
def reports():
    """Reports page"""
    return render_template('analytics/reports.html')


@analytics_bp.route('/export')
@login_required
def export_data():
    """Export analytics data"""
    export_type = request.args.get('type', 'users')
    format_type = request.args.get('format', 'csv')
    
    # TODO: Implement actual export functionality
    flash(f'Export {export_type} as {format_type} - Feature coming soon!', 'info')
    return redirect(request.referrer or url_for('analytics.system_stats'))
