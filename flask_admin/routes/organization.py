"""
Organization management routes for Flask Admin Panel (Class-Based Views)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.views import MethodView
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import login_required
from api_client import api_client

organization_bp = Blueprint('organization', __name__, url_prefix='/organization')

class BranchView(MethodView):
    decorators = [login_required]

    def get(self, branch_id=None):
        if branch_id:
            # This would be for a detail view, not implemented in the original code
            pass
        else:
            branches_data = api_client.get('/api/v1/admin/branches')
            if 'error' in branches_data:
                flash(f"Error loading branches: {branches_data['error']}", 'danger')
                if branches_data.get('status_code') in [401, 403]:
                    return redirect(url_for('main.logout'))
                branches_data = []
            return render_template('organization/branches.html', branches=branches_data)

    def post(self):
        branch_data = {
            'name': request.form.get('name'),
            'code': request.form.get('code'),
            'address': request.form.get('address'),
            'province': request.form.get('province')
        }
        result = api_client.post('/api/v1/admin/branches', branch_data)
        if 'error' in result:
            flash(f"Error creating branch: {result['error']}", 'danger')
        else:
            flash('Branch created successfully!', 'success')
        return redirect(url_for('organization.branches'))

class DepartmentView(MethodView):
    decorators = [login_required]

    def get(self):
        departments_data = api_client.get('/api/v1/admin/departments')
        if 'error' in departments_data:
            flash(f"Error loading departments: {departments_data['error']}", 'danger')
            if departments_data.get('status_code') in [401, 403]:
                return redirect(url_for('main.logout'))
            departments_data = []
        return render_template('organization/departments.html', departments=departments_data)

    def post(self):
        department_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description')
        }
        result = api_client.post('/api/v1/admin/departments', department_data)
        if 'error' in result:
            flash(f"Error creating department: {result['error']}", 'danger')
        else:
            flash('Department created successfully!', 'success')
        return redirect(url_for('organization.departments'))

class PositionView(MethodView):
    decorators = [login_required]

    def get(self):
        positions_data = api_client.get('/api/v1/admin/positions')
        if 'error' in positions_data:
            flash(f"Error loading positions: {positions_data['error']}", 'danger')
            if positions_data.get('status_code') in [401, 403]:
                return redirect(url_for('main.logout'))
            positions_data = []
        return render_template('organization/positions.html', positions=positions_data)

    def post(self):
        position_data = {
            'title': request.form.get('title'),
            'department_id': request.form.get('department_id')
        }
        result = api_client.post('/api/v1/admin/positions', position_data)
        if 'error' in result:
            flash(f"Error creating position: {result['error']}", 'danger')
        else:
            flash('Position created successfully!', 'success')
        return redirect(url_for('organization.positions'))

# Register class-based views
organization_bp.add_url_rule('/branches', view_func=BranchView.as_view('branches'))
organization_bp.add_url_rule('/branches/create', view_func=BranchView.as_view('create_branch'))
organization_bp.add_url_rule('/departments', view_func=DepartmentView.as_view('departments'))
organization_bp.add_url_rule('/departments/create', view_func=DepartmentView.as_view('create_department'))
organization_bp.add_url_rule('/positions', view_func=PositionView.as_view('positions'))
organization_bp.add_url_rule('/positions/create', view_func=PositionView.as_view('create_position'))