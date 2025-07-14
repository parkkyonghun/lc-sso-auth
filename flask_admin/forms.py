"""
Forms module for Flask Admin Panel
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional as OptionalValidator



class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class UserForm(FlaskForm):
    """User creation/edit form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[OptionalValidator(), Length(max=100)])
    password = PasswordField('Password', validators=[OptionalValidator(), Length(min=6)])
    is_active = BooleanField('Active', default=True)
    is_verified = BooleanField('Verified', default=False)
    is_superuser = BooleanField('Superuser', default=False)
    bio = TextAreaField('Bio', validators=[OptionalValidator(), Length(max=500)])
    timezone = StringField('Timezone', validators=[OptionalValidator(), Length(max=50)])
    language = StringField('Language', validators=[OptionalValidator(), Length(max=10)])
    
    # Organization fields
    branch = SelectField('Branch', coerce=str, validators=[OptionalValidator()])
    department = SelectField('Department', coerce=str, validators=[OptionalValidator()])
    position = SelectField('Position', coerce=str, validators=[OptionalValidator()])
    manager_name = StringField('Manager Name', validators=[OptionalValidator(), Length(max=100)])

    # Submit button
    submit = SubmitField('Save User')


class ApplicationForm(FlaskForm):
    """Application creation/edit form"""
    name = StringField('Application Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[OptionalValidator(), Length(max=500)])
    website_url = StringField('Website URL', validators=[OptionalValidator(), Length(max=200)])
    privacy_policy_url = StringField('Privacy Policy URL', validators=[OptionalValidator(), Length(max=200)])
    terms_of_service_url = StringField('Terms of Service URL', validators=[OptionalValidator(), Length(max=200)])
    logo_url = StringField('Logo URL', validators=[OptionalValidator(), Length(max=200)])
    is_active = BooleanField('Active', default=True)
    is_confidential = BooleanField('Confidential Client', default=True)
    require_consent = BooleanField('Require User Consent', default=True)
    
    # OAuth specific fields
    redirect_uris = TextAreaField('Redirect URIs (one per line)', validators=[DataRequired()])
    allowed_scopes = TextAreaField('Allowed Scopes (one per line)', validators=[OptionalValidator()])
    grant_types = TextAreaField('Grant Types (one per line)', validators=[OptionalValidator()])
    response_types = TextAreaField('Response Types (one per line)', validators=[OptionalValidator()])
    
    # Token settings
    access_token_lifetime = IntegerField('Access Token Lifetime (minutes)', validators=[OptionalValidator()])
    refresh_token_lifetime = IntegerField('Refresh Token Lifetime (days)', validators=[OptionalValidator()])
    token_endpoint_auth_method = SelectField(
        'Token Endpoint Auth Method',
        choices=[
            ('client_secret_basic', 'Client Secret Basic'),
            ('client_secret_post', 'Client Secret Post'),
            ('none', 'None (Public Client)')
        ],
        default='client_secret_basic'
    )


class RoleForm(FlaskForm):
    """Role creation/edit form"""
    role_name = StringField('Role Name', validators=[DataRequired(), Length(min=3, max=50)])
    description = TextAreaField('Description', validators=[OptionalValidator(), Length(max=200)])
    permissions = SelectField('Permissions', coerce=str, validators=[OptionalValidator()])


class PermissionForm(FlaskForm):
    """Permission creation/edit form"""
    permission_name = StringField('Permission Name', validators=[DataRequired(), Length(min=3, max=50)])
    description = TextAreaField('Description', validators=[OptionalValidator(), Length(max=200)])


class BranchForm(FlaskForm):
    """Branch creation/edit form"""
    branch_name = StringField('Branch Name', validators=[DataRequired(), Length(min=3, max=100)])
    branch_code = StringField('Branch Code', validators=[DataRequired(), Length(min=2, max=20)])
    address = TextAreaField('Address', validators=[OptionalValidator(), Length(max=300)])
    province = StringField('Province', validators=[OptionalValidator(), Length(max=50)])


class DepartmentForm(FlaskForm):
    """Department creation/edit form"""
    department_name = StringField('Department Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[OptionalValidator(), Length(max=300)])


class PositionForm(FlaskForm):
    """Position creation/edit form"""
    title = StringField('Position Title', validators=[DataRequired(), Length(min=3, max=100)])
    department_id = SelectField('Department', coerce=str, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[OptionalValidator(), Length(max=300)])


class SearchForm(FlaskForm):
    """Generic search form"""
    q = StringField('Search', validators=[OptionalValidator(), Length(max=100)])
    page = StringField('Page', validators=[OptionalValidator()])
    limit = SelectField(
        'Items per page',
        choices=[('10', '10'), ('20', '20'), ('50', '50'), ('100', '100')],
        default='20'
    )


class BulkActionForm(FlaskForm):
    """Bulk action form"""
    action = SelectField(
        'Action',
        choices=[
            ('activate', 'Activate'),
            ('deactivate', 'Deactivate'),
            ('verify', 'Verify'),
            ('delete', 'Delete'),
            ('unlock', 'Unlock')
        ],
        validators=[DataRequired()]
    )
    selected_ids = StringField('Selected IDs', validators=[DataRequired()])
