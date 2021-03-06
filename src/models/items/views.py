import os

from flask import Blueprint, session, render_template, make_response, request, flash, jsonify

from src.models.items.item import Item
from src.models.messages.message import Message
from src.models.users.user import User
import src.models.admins.constants as AdminConstants
import src.models.items.constants as ItemConstants
import src.models.users.constants as UserConstants
import src.models.items.decorators as item_decorators
import src.config as CONFIG

__author__ = 'ibininja'

item_blueprints = Blueprint('items', __name__)

# UPLOAD_FOLDER = './static/resources/'
APP_ROOT = (os.path.realpath('./'))
categories = CONFIG.CATEGORIES


@item_blueprints.route('/user/items/view')
@item_decorators.requires_login
def view_items():
    # if session.get('email') is None:
    #     return render_template("login.jinja2", message="You must be logged in to view your items")
    # else:
    if session.get('email') is None:
        return render_template("login.jinja2", message="You must be logged in to view your items")
    user = User.get_user_by_email(session['email'], UserConstants.COLLECTION)
    items = Item.get_items_by_user_id(user._id)
    session['msgs_count'] = Message.get_unread_messages_count(user._id)
    return render_template("item/items.jinja2", items=items)


@item_blueprints.route('/items/view')
def view_all_items():
    if session.get('email') is None:
        flash("sign up for FREE to post your items.")
    else:
        user = User.get_user_by_email(session['email'], UserConstants.COLLECTION)
        session['msgs_count'] = Message.get_unread_messages_count(user._id)
    items = Item.get_all_approved_items()
    return render_template("item/all_items.jinja2", items=items)


@item_blueprints.route('/user/items/add', methods=['POST', 'GET'])
@item_decorators.requires_login
def add_item():
    # if session.get('email') is None:
    #     return render_template("login.jinja2", message="You must be logged in to add items")
    # else:
    if request.method == 'GET':
        return render_template("item/add_item.jinja2", categories=categories)
    else:
        uploaded_file_list = request.files.getlist("file")
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']
        contact = request.form['contact']
        user = User.get_user_by_email(session['email'], UserConstants.COLLECTION)
        # Target folder for these uploads.
        target = os.path.join(APP_ROOT, 'static/resources/images/{}/{}'.format(user.username, title))
        # target = './static/resources/{}'.format(upload_key)
        try:
            if not os.path.isdir(target):
                os.mkdir(target)
        except Exception as e:
            print(e)
            return render_template("message_center.jinja2",
                                   message="System was not able to store uploaded file in server! Contact Admin.")
        filename = ''
        images_path = []
        for upload in uploaded_file_list:
            filename = upload.filename.rsplit("/")[0]
            # TODO: Change this to be in Config File.
            destination = os.path.join(APP_ROOT,
                                       'static/resources/images/{}/{}/{}'.format(user.username, title, filename))
            images_path.append('resources/images/{}/{}/{}'.format(user.username, title, filename))
            # destination = "/".join([target, filename])
            upload.save(destination)
        user.add_item(title=title, description=description,
                      image_url=images_path, contact=contact, category=[category])
        return make_response(view_items())


@item_blueprints.route('/user/items/detail/<string:item_id>')
def item_details(item_id):
    item = Item.get_item_by_id(item_id)
    if item is not None:
        if session.get('email') is not None:
            user = User.get_user_by_email(email=session['email'], collection=UserConstants.COLLECTION)
            session['msgs_count'] = Message.get_unread_messages_count(user._id)
            if (user._id == item.user_id) or (session.get('admin') is not None):
                return render_template("item/item_details.jinja2", item=item, editable=True)
            else:
                return render_template("item/item_details.jinja2", item=item)
        else:
            return render_template("item/item_details.jinja2", item=item)
    else:
        return render_template("message_center.jinja2",
                               message="Item {} does not have details. Contact Us if you need further information!".format(
                                       item.title))


@item_blueprints.route('/user/items/delete/<string:item_id>')
@item_decorators.requires_login
def delete_item(item_id):
    # if session.get('email') is not None:
    item = Item.get_item_by_id(item_id)
    if item is not None:
        user = User.get_user_by_email(email=session['email'], collection=UserConstants.COLLECTION)
        if item.user_id == user._id:
            item.remove_item()
            return make_response(view_items())
    return render_template("item/items.jinja2", message="You can't remove item")
    # else:
    #     return render_template("login.jinja2", message="You must be logged-in to remove items.")


@item_blueprints.route('/user/items/edit/<string:item_id>/<string:attribute_name>/<string:attribute_value>')
@item_decorators.requires_login
def edit_item(item_id, attribute_name, attribute_value):
    item = Item.get_item_by_id(item_id)
    if item is not None:
        item.update_item(attribute_name=attribute_name, attribute_value=attribute_value)
        if session.get('admin') is not None:
            return render_template("item/item_details.jinja2", item=item)
        else:
            item.update_item(attribute_name="approved", attribute_value=False)
            return render_template("message_center.jinja2",
                                   message="Item will published as soon as the change is approved")
    else:
        return render_template("message_center.jinja2",
                               message="Could not update Item {} . Contact Us if you need further information!".format(
                                       item.title))


@item_blueprints.route('/user/item/update/title', methods=['GET', 'POST'])
@item_decorators.requires_login
def update_title():
    item_id = request.form['pk']
    value = request.form['value']
    item = Item.get_item_by_id(item_id)
    item.update_item("title", value)
    if session.get('admin') is not None:
        return render_template("item/item_details.jinja2", item=item)
    else:
        item.update_item(attribute_name="approved", attribute_value=False)
        return render_template("message_center.jinja2", message="Item will published as soon as the change is approved")


@item_blueprints.route('/user/item/update/description', methods=['GET', 'POST'])
@item_decorators.requires_login
def update_description():
    item_id = request.form['pk']
    value = request.form['value']
    item = Item.get_item_by_id(item_id)
    item.update_item("description", value)
    if session.get('admin') is not None:
        return render_template("item/item_details.jinja2", item=item)
    else:
        item.update_item(attribute_name="approved", attribute_value=False)
        return render_template("message_center.jinja2", message="Item will published as soon as the change is approved")


@item_blueprints.route('/user/item/update/contact', methods=['GET', 'POST'])
@item_decorators.requires_login
def update_contact():
    item_id = request.form['pk']
    value = request.form['value']
    item = Item.get_item_by_id(item_id)
    item.update_item("contact", value)
    if session.get('admin') is not None:
        return render_template("item/item_details.jinja2", item=item)
    else:
        item.update_item(attribute_name="approved", attribute_value=False)
        return render_template("message_center.jinja2", message="Item will published as soon as the change is approved")
