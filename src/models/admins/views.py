import json
from bson import json_util
from flask import Blueprint, session, render_template, make_response

from src.models.admins.admin import Admin
from src.models.items.item import Item
import src.models.admins.constants as AdminConstants
import src.models.items.constants as ItemConstants
import src.models.users.constants as UserConstants
from src.models.users.user import User
import src.models.admins.decorators as admin_decorators
__author__ = 'ibininja'

admin_blueprints = Blueprint('admins', __name__)


@admin_blueprints.route('/admin/dashboard')
@admin_decorators.requires_admin_login
def dashboard():
    # verify User is admin
    # if session.get('admin') is None:

    # else:
    admin = Admin.get_user_by_email(session['admin'], AdminConstants.COLLECTION)
    if admin is None:
        return render_template("message_center.jinja2",
                               message="System could not detect rights to access to this area.")
    else:
        items_count = admin.get_number_of_all_items()
        approved_items_count = admin.get_number_of_all_approved_items()
        pending_items_count = admin.get_number_of_all_pending_items()
        users_count = admin.get_number_of_users()
        return render_template("admin/dashboard.jinja2", items_count=items_count,
                               approved_items_count=approved_items_count, pending_items_count=pending_items_count,
                               users_count=users_count, )

@admin_blueprints.route('/admin/dashboard/ditems')
@admin_decorators.requires_admin_login
def get_posted_items_count():
    #TODO: add authentication
    items_json = []
    item_counts_day = Item.get_posted_items_count()
    for item in item_counts_day:
        items_json.append(item)
    items_json=json_util.dumps(items_json, default=json_util.default)
    return items_json

@admin_blueprints.route('/admin/dashboard/dusers')
@admin_decorators.requires_admin_login
def get_posted_users_count():
    #TODO: add authentication
    users_json = []
    users_counts_day = User.get_posted_users_count()
    for user in users_counts_day:
        users_json.append(user)
    users_json=json_util.dumps(users_json, default=json_util.default)
    return users_json

@admin_blueprints.route('/admin/pending/items')
@admin_decorators.requires_admin_login
def pending_items():
    # if session.get('admin') is None:

    # else:
    admin = Admin.get_user_by_email(session['admin'], AdminConstants.COLLECTION)
    if admin is None:
        return render_template("message_center.jinja2",
                               message="System could not detect rights to access to this area.")
    else:
        items = Item.get_pending_items()
        return render_template("admin/pending_items.jinja2", items=items)


@admin_blueprints.route('/user/items/approve/<string:item_id>')
@admin_decorators.requires_admin_login
def approve_item(item_id):
    # if session.get('admin') is not None:
    item = Item.get_item_by_id(item_id)
    if item is not None:
        item.update_item(attribute_name="approved", attribute_value=True)
        return make_response(pending_items())
    return make_response(pending_items())
    # else:
    #     return render_template("login.jinja2", message="System could not detect rights to access this area.")

@admin_blueprints.route('/admin/test')
def test_graphs():
    return render_template("admin/statistics.jinja2")


