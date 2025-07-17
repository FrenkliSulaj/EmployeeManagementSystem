from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.utils import admin_required
from app.forms import LoginForm, RegistrationForm, EmployeeForm, DeleteForm, ApproveUserForm
from app.models import User, Employee
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')  # Homepage

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'warning')
            return redirect(url_for('main.register'))

        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if not user.is_approved:
                flash("Your account is pending admin approval.", "warning")
                return redirect(url_for('main.login'))
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')
    else:
        if request.method == 'POST':
            print("Form did NOT validate")
            print(form.errors)
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('main.login'))

@bp.route('/employees')
@login_required
def list_employees():
    employees = Employee.query.all()
    delete_form = DeleteForm()
    return render_template('employees/list.html', employees=employees, delete_form=delete_form)

@bp.route('/employees/new', methods=['GET', 'POST'])
@login_required
def create_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            department=form.department.data,
            position=form.position.data
        )
        db.session.add(employee)
        db.session.commit()
        flash('Employee created successfully.')
        return redirect(url_for('main.list_employees'))
    return render_template('employees/create.html', form=form)

@bp.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)
    if form.validate_on_submit():
        form.populate_obj(employee)
        db.session.commit()
        flash('Employee updated successfully.')
        return redirect(url_for('main.list_employees'))
    return render_template('employees/edit.html', form=form)

@bp.route('/employees/<int:id>/delete', methods=['POST'])
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully.')
    return redirect(url_for('main.list_employees'))

@bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    approve_form = ApproveUserForm()
    return render_template('admin/dashboard.html', users=users, approve_form=approve_form)

@bp.route('/approve_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    form = ApproveUserForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        user.is_approved = True
        db.session.commit()
        flash(f"User {user.username} has been approved.", "success")
    else:
        flash("Invalid request.", "danger")
    return redirect(url_for('main.admin_dashboard'))