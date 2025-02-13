# views.py (Route Handlers)

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Project, ProjectParticipant, Expense
from forms import RegistrationForm, LoginForm, CreateProjectForm, AddExpenseForm, ShareProjectForm
from collections import defaultdict

@login_required
def index():
    created_projects = current_user.projects.all()
    participating_projects = [pp.project for pp in current_user.participations]
    all_projects = created_projects + participating_projects
    return render_template('index.html', projects=all_projects)

def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@login_required
def create_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        new_project = Project(name=form.project_name.data, creator_id=current_user.id)
        db.session.add(new_project)
        participant = ProjectParticipant(project=new_project, user=current_user)
        db.session.add(participant)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_project.html', form=form)

@login_required
def project(id):
    project = Project.query.get_or_404(id)

    if current_user != project.creator and current_user not in [p.user for p in project.participants]:
        flash('You do not have permission to view this project.', 'warning')
        return redirect(url_for('index'))

    add_expense_form = AddExpenseForm()
    share_project_form = ShareProjectForm()


    # Populate choices for the AddExpenseForm's user_id field.  VERY IMPORTANT.
    participant_users = [p.user for p in project.participants]
    all_possible_users = participant_users + [project.creator]
    all_possible_users = list({user.id: user for user in all_possible_users}.values()) # Remove duplicates!
    add_expense_form.user_id.choices = [(user.id, user.username) for user in all_possible_users]

    if request.method == 'POST':
      # Handle Add Expense Form Submission
      if 'expense_description' in request.form: # Check for form identifier
        if add_expense_form.validate_on_submit():
            new_expense = Expense(
                description=add_expense_form.description.data,
                amount=add_expense_form.amount.data,
                project_id=project.id,
                user_id=add_expense_form.user_id.data
            )
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('project', id=project.id)) # Stay on project page
        else:
          # If form validation fails, flash errors
            for field, errors in add_expense_form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", 'danger')

      # Handle Share Project Form Submission
      elif 'share_username' in request.form:  # Check for form identifier
        if share_project_form.validate_on_submit():
            user_to_share = User.query.filter_by(username=share_project_form.share_username.data).first()
            if user_to_share:
                if ProjectParticipant.query.filter_by(project_id=project.id, user_id=user_to_share.id).first():
                    flash(f'{share_project_form.share_username.data} is already a participant.', 'warning')
                else:
                    participant = ProjectParticipant(project_id=project.id, user_id=user_to_share.id)
                    db.session.add(participant)
                    db.session.commit()
                    flash(f'Project shared with {share_project_form.share_username.data}!', 'success')
            else:
                flash('User not found.', 'danger')
            return redirect(url_for('project', id=project.id))  # Stay on project page
        else:
            for field, errors in share_project_form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", 'danger')

    # Calculations (same as before, but now outside the POST handling)
    expenses = project.expenses.all()
    total_spending = defaultdict(float)
    for expense in expenses:
        total_spending[expense.user.username] += expense.amount

    total_project_cost = sum(expense.amount for expense in expenses)
    num_participants = len(project.participants)
    split_amount = total_project_cost / num_participants if num_participants > 0 else 0

    balances = {}
    for user in [p.user for p in project.participants] + [project.creator]:
        balances[user.username] = total_spending[user.username] - split_amount

    return render_template('project.html', project=project, expenses=expenses,
                           total_spending=total_spending, split_amount=split_amount,
                           balances=balances, add_expense_form=add_expense_form,
                           share_project_form=share_project_form)



@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.creator_id != current_user.id:
        flash("You can only delete projects you created.", 'warning')
        return redirect(url_for('index'))

    db.session.delete(project)
    db.session.commit()
    flash("Project deleted successfully.", 'success')
    return redirect(url_for('index'))

@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    project_id = expense.project_id
    project = Project.query.get_or_404(project_id)

    if current_user.id != project.creator_id and current_user.id != expense.user_id:
        flash("You do not have permission to delete this expense.", 'warning')
        return redirect(url_for('project', id=project_id))

    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", 'success')
    return redirect(url_for('project', id=project_id))

@login_required
def remove_participant(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    user_to_remove = User.query.get_or_404(user_id)

    if current_user.id != project.creator_id:
        flash("You do not have permission to remove participants.", 'warning')
        return redirect(url_for('project', id=project.id))

    if user_to_remove.id == project.creator_id:
        flash("You cannot remove yourself.", 'warning')
        return redirect(url_for('project', id=project_id))

    participant = ProjectParticipant.query.filter_by(project_id=project.id, user_id=user_id).first()
    if participant:
        db.session.delete(participant)
        db.session.commit()
        flash(f"{user_to_remove.username} removed.", 'success')
    else:
        flash("Participant not found.", 'warning')
    return redirect(url_for('project', id=project.id))