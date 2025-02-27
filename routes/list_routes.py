from flask import Blueprint, render_template, redirect, url_for, flash, request
from forms import CreateListForm, AddItemForm, ShareListForm
from models import db, List, Item, ListParticipant, User
from flask_login import login_required, current_user
from datetime import datetime

list_bp = Blueprint('list', __name__)

@list_bp.route('/')
@login_required
def index():
    created_lists = List.query.filter_by(created_by_id=current_user.id).all()
    participated_lists = []
    participant_records = ListParticipant.query.filter_by(user_id=current_user.id).all()
    for record in participant_records:
        participated_lists.append(record.list)
    return render_template('index.html', created_lists=created_lists, participated_lists=participated_lists, title='Dashboard')

@list_bp.route('/create_list', methods=['GET', 'POST'])
@login_required
def create_list():
    form = CreateListForm()
    if form.validate_on_submit():
        list_item = List(name=form.name.data, created_by_id=current_user.id)
        db.session.add(list_item)
        db.session.commit()
        flash('Your list has been created!', 'success')
        return redirect(url_for('list.index'))
    return render_template('create_list.html', form=form, title='Create New List')

@list_bp.route('/list/<int:list_id>', methods=['GET', 'POST'])
@login_required
def list_detail(list_id):
    list_obj = List.query.get_or_404(list_id)
    if list_obj.created_by_id != current_user.id and not ListParticipant.query.filter_by(list_id=list_id, user_id=current_user.id).first():
        flash("You don't have permission to view this list.", 'danger')
        return redirect(url_for('list.index'))

    add_item_form = AddItemForm()
    share_form = ShareListForm()

    print("Entering list_detail function for list_id:", list_id) # LOG 1: Function entry

    if request.method == 'POST':
        print("Request method is POST") # LOG 2: Request is POST

        if 'name' in request.form:
            print(" 'name' field is in request.form") # LOG 3: 'name' field is present
            if add_item_form.validate_on_submit():
                print("  add_item_form is valid") # LOG 4: Form validation success
                item = Item(name=add_item_form.name.data, list_id=list_obj.id, added_by_id=current_user.id)
                print("  Item object created:", item) # LOG 5: Item object creation
                db.session.add(item)
                print("  Item added to session") # LOG 6: Added to session
                db.session.commit()
                print("  Session committed") # LOG 7: Session commit
                flash('Item added to list!', 'success')
                print("  Flash message set, redirecting...") # LOG 8: Before redirect
                return redirect(url_for('list.list_detail', list_id=list_id))
            else:
                print("  add_item_form is NOT valid. Errors:", add_item_form.errors) # LOG 9: Form validation failed
        else:
            print(" 'name' field is NOT in request.form") # LOG 10: 'name' field missing

        if 'username' in request.form and share_form.validate_on_submit():
            user_to_share = User.query.filter_by(username=share_form.username.data).first()
            if not user_to_share:
                flash('User not found.', 'danger')
            elif ListParticipant.query.filter_by(list_id=list_id, user_id=user_to_share.id).first():
                flash('User is already participating in this list.', 'info')
            else:
                participant = ListParticipant(list_id=list_id, user_id=user_to_share.id)
                db.session.add(participant)
                db.session.commit()
                flash(f'List shared with {share_form.username.data}!', 'success')
            return redirect(url_for('list.list_detail', list_id=list_id))


        if 'tick_item' in request.form:
            item_id_to_tick = request.form['tick_item']
            item_to_tick = Item.query.get_or_404(item_id_to_tick)
            if item_to_tick.list_id == list_id:
                if item_to_tick.is_ticked:
                    item_to_tick.is_ticked = False
                    item_to_tick.ticked_by_id = None
                    item_to_tick.ticked_at = None
                    flash(f'Item "{item_to_tick.name}" unticked.', 'info')
                else:
                    item_to_tick.is_ticked = True
                    item_to_tick.ticked_by_id = current_user.id
                    item_to_tick.ticked_at = datetime.utcnow()
                    flash(f'Item "{item_to_tick.name}" ticked off!', 'success')
                db.session.commit()
            return redirect(url_for('list.list_detail', list_id=list_id))


    tick_counts = {}
    for item in list_obj.items:
        if item.is_ticked and item.ticked_by_user:
            if item.ticked_by_user.username in tick_counts:
                tick_counts[item.ticked_by_user.username] += 1
            else:
                tick_counts[item.ticked_by_user.username] = 1

    return render_template('list_detail.html', list=list_obj, add_item_form=add_item_form, share_form=share_form, tick_counts=tick_counts, title=list_obj.name)