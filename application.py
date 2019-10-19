#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 20:53:03 2019
@author: Miles
"""
# Import the methods required to run the web application and database layer.
from flask import Flask, render_template, request, redirect, url_for
from flask import flash, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# Import methods for user authorisation.
from functools import wraps
from flask import abort, make_response
from flask_httpauth import HTTPBasicAuth
from flask import session as login_session
from oauth2client import client
import requests
import httplib2
import json

# Create an instance of the Flask class.
app = Flask(__name__)

# Initiate a connection to the SQLite database.
# 'check_same_thread=False'stops threading errors.
engine = create_engine('sqlite:///itemCategory.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create an instance of the basic HTTP authenication class.
auth = HTTPBasicAuth()

# ------------------------------------------
# WEBSITE PAGES GO HERE -------------------
# ------------------------------------------


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


# This is the code for the Home Page.
@app.route('/')
@app.route('/catalog')
def categoryList():

    # Find list of categories to display.
    categories = session.query(Category).order_by(Category.name).all()
    # Find the top 10 items most recently added to the database.
    items = session.query(Category, Item).filter(
            Category.id == Item.cat_id).order_by(
                    Item.created.desc()).limit(10).all()
    # Redirect users to public page  if not logged in.
    if 'username' not in login_session:
        # Return the Public catalog home page.
        return render_template('catalogPublic.html',
                               categories=categories, items=items)
    else:
        # Return the catalog home page listing all
        # categories and the top 10 latest items.
        return render_template('catalog.html',
                               categories=categories, items=items)


# This is the code for listing items within a category.
@app.route('/catalog/<category_name>/items')
def itemsList(category_name):

    # Find list of categories to display.
    categories = session.query(Category).order_by(Category.name).all()
    # Find the category we want to list the items for.
    category = session.query(Category).filter_by(name=category_name).one()

    # Find the items for that category.
    items = session.query(Item).filter_by(cat_id=category.id).all()
    # Determine hwo many items to be listed. This is displayed on the web page.
    count = 0
    for i in items:
        count += 1
    # Redirect users to public page  if not logged in.
    if 'username' not in login_session:
        # Return the public web page for listing items with a category.
        return render_template('itemslistPublic.html', categories=categories,
                               category=category, items=items, count=count)
    else:
        # Return the web page for listing items with a category.
        return render_template('itemslist.html', categories=categories,
                               category=category, items=items, count=count)


# This is the code for viewing the description of an item.
@app.route('/catalog/<category_name>/<item_name>')
def itemDescription(category_name, item_name):

    # Find the category we want to list the item description for.
    category = session.query(Category).filter_by(name=category_name).one()

    # Find the item for that category.
    item = session.query(Item).filter_by(
                cat_id=category.id, name=item_name).one()

    # Find the user that created the item originally.
    user = session.query(User).filter_by(id=item.user_id).one()

    # Redirect users to public if not logged in or did not create the item.
    if ('username' not in login_session) or (
            login_session['username'] != user.username):
        # Return the web page showing the item description.
        return render_template('itemDescriptionPublic.html',
                               category=category, item=item)
    else:
        # Return the web page showing the item description.
        return render_template('itemDescription.html',
                               category=category, item=item)


# This is the code for creating a new item in a category.
@app.route('/catalog/<category_name>/newitem', methods=['GET', 'POST'])
@login_required
def newItem(category_name):

    # If a new item is being submitted run this code.
    if request.method == 'POST':
        # Find the category of the new item.
        category = session.query(Category).filter_by(
                name=request.form['selectedCategory']).one()
        # Find out if the items already exists in that category.
        exisitingItem = session.query(Item).filter_by(
                name=request.form['title'], cat_id=category.id).all()
        # If it exists already then display a flash message to the user.
        if (exisitingItem):
            flash("Item NOT created as it already exists!")
            # Return to the main itemlist for that category.
            return redirect(url_for('itemsList', category_name=category.name))
        # If the item does not exist, then create it and flash message to the
        # user.
        else:
            # Find the user details.
            user = session.query(User).filter_by(
                    username=login_session['username']).one()

            createItem = Item(name=request.form['title'],
                              description=request.form['details'],
                              cat_id=category.id,
                              user_id=user.id)
            session.add(createItem)
            session.commit()
            flash("New item created!")
            # Return to the main itemlist for that category.
            return redirect(url_for('itemsList', category_name=category.name))
    # Else return the web page to create a new item.
    else:
        # All categories are needed to populate the category drop down menu.
        categories = session.query(Category).order_by(Category.name).all()
        # Currently selected category is used to pre-select category from the
        # drop down menu and inform other features on the web page.
        category = session.query(Category).filter_by(name=category_name).one()
        # Return web page to create a new item.
        return render_template('newItem.html', categories=categories,
                               category=category)


# This is the code for creating a new item when navigating from the main page.
@app.route('/catalog/newitem', methods=['GET', 'POST'])
@login_required
def newItemMain():

    # If a new item is being submitted run this code.
    if request.method == 'POST':
        # Find the category of the new item.
        category = session.query(Category).filter_by(
                name=request.form['selectedCategory']).one()
        # Find out if the items already exists in that category.
        exisitingItem = session.query(Item).filter_by(
                name=request.form['title'], cat_id=category.id).all()
        # If it exists already then display a flash message to the user.
        if (exisitingItem):
            flash("Item NOT created as it already exist!")
            # Return to the main category list page.
            return redirect(url_for('categoryList'))
        # If the item does not exist, then create it and flash message to the
        # user.
        else:
            # Find the user details.
            user = session.query(User).filter_by(
                    username=login_session['username']).one()

            createItem = Item(name=request.form['title'],
                              description=request.form['details'],
                              cat_id=category.id,
                              user_id=user.id)
            session.add(createItem)
            session.commit()
            flash("New item created!")
            # Return to the main category list page.
            return redirect(url_for('categoryList'))
    # Else return the web page to create a new item.
    else:
        # All categories are needed to populate the category drop down menu.
        categories = session.query(Category).order_by(Category.name).all()
        # Return web page to create a new item.
        return render_template('newItemMain.html', categories=categories)


# This is the code for editing an item in a category.
@app.route('/catalog/<category_name>/<item_name>/edititem',
           methods=['GET', 'POST'])
@login_required
def editItem(category_name, item_name):

    # Return the category we want to edit an item from.
    category = session.query(Category).filter_by(name=category_name).one()
    # Return the item to edit.
    item = session.query(Item).filter_by(
            cat_id=category.id, name=item_name).one()
    # Find the user that created the item originally.
    user = session.query(User).filter_by(id=item.user_id).one()

    # Check if the user created the item and has rights to edit.
    if (login_session['username'] == user.username):
        # If a existing item is being editted run this code.
        if request.method == 'POST':
            if request.form['title']:
                # Set the item's new name.
                item.name = request.form['title']
            if request.form['details']:
                # Set the item's new description.
                item.description = request.form['details']
            if request.form['selectedCategory']:
                # Set the item's new category.
                category = session.query(Category).filter_by(
                        name=request.form['selectedCategory']).one()
                item.cat_id = category.id
            # Update the item in the database and flash message once complete.
            session.add(item)
            session.commit()
            flash(item.name+" edited in "+category.name+" category")
            # Return to the item list page for that category.
            return redirect(url_for('itemsList', category_name=category.name))
        # Else run the code to display the edit item page.
        else:
            # All categories required to populate the category drop down.
            categories = session.query(Category).order_by(Category.name).all()
            # Return the edit item web page.
            return render_template('editItem.html', categories=categories,
                                   category=category, item=item)
    else:
        flash("You are not allowed to access there")
        return redirect(url_for('itemDescription',
                                category_name=category.name,
                                item_name=item.name))


# This is the code for deleting an item in a category.
@app.route('/catalog/<category_name>/<item_name>/deleteitem',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_name, item_name):

    # Return the category we want to delete an item from.
    category = session.query(Category).filter_by(name=category_name).one()
    # Return the item to delete.
    item = session.query(Item).filter_by(
            cat_id=category.id, name=item_name).one()
    # Find the user that created the item originally.
    user = session.query(User).filter_by(id=item.user_id).one()

    # Check if the user created the item and has rights to delete.
    if (login_session['username'] == user.username):
        # If the item is being deleted run this code.
        if request.method == 'POST':
            # Delete the item and flash a confirmation message.
            session.delete(item)
            session.commit()
            flash(item.name+" deleted from "+category.name+" category")
            # Return to the main items list page for that category.
            return redirect(url_for('itemsList', category_name=category.name))
        # Else return the delete item web page.
        else:
            return render_template('deleteItem.html', category=category,
                                   item=item)
    else:
        flash("You are not allowed to access there")
        return redirect(url_for('itemDescription',
                                category_name=category.name,
                                item_name=item.name))


# --------------------------------------------
# JSON END POINTS GO HERE -------------------
# --------------------------------------------

# Return a JSON list of the categories and their items.
@app.route('/catalog.json')
def catalogJSON():

    # Find all the categories.
    categories = session.query(Category).order_by(Category.name).all()
    # Create a list to hold the categories.
    data = []
    # Iterate through the categories and build a list of items.
    for c in categories:
        # Find all the items for this category.
        items = session.query(Item).filter_by(cat_id=c.id).all()
        # Create a list to hold the items for this category.
        itemList = []
        # Iterate through each item and build of list of the items.
        for i in items:
            # Use a dictionary to represent the item attributes
            # and append each item to the list.
            itemList.append({"id": i.id, "name": i.name,
                             "description": i.description, "cat_id": i.cat_id})
        # Add the category and the items list as an entry in the data list.
        data.append({"id": c.id, "name": c.name, "item": itemList})
    # Return the carteory and item data in JSON format.
    return jsonify(Categories=data)


# Return a JSON list with a single category and its items.
@app.route('/catalog/<category_name>.json')
def catalogCategoryJSON(category_name):

    # Find the category. Use lower case filter in case of case issues.
    category = session.query(Category).filter(
            func.lower(Category.name) == category_name.lower()).one()
    # Create a list oject to hold the category.
    data = []
    # Find all the items for this category.
    items = session.query(Item).filter_by(cat_id=category.id).all()
    # Create a list to hold the items for this category.
    itemList = []
    # Iterate through each item and build of list of the items.
    for i in items:
        # Use a dictionary to represent the item attributes
        # and append each item to the list.
        itemList.append({"id": i.id, "name": i.name,
                         "description": i.description, "cat_id": i.cat_id})
    # Add the category and the items list as an entry in the data list.
    data.append({"id": category.id, "name": category.name, "item": itemList})
    # Return the carteory and item data in JSON format.
    return jsonify(Category=data)


# Return a JSON list with a single category and single item.
@app.route('/catalog/<category_name>/<item_name>.json')
def catalogItemJSON(category_name, item_name):

    # Find the category. Use lower case in case of user error.
    category = session.query(Category).filter(
            func.lower(Category.name) == category_name.lower()).one()
    # Create a list oject to hold the category.
    data = []
    # Find the item for this category. Use lower case in case of user error.
    item = session.query(Item).filter(
            Item.cat_id == category.id, func.lower(
                    Item.name) == item_name.lower()).one()
    # Create a list to hold the item for this category.
    itemList = [{"id": item.id, "name": item.name,
                 "description": item.description, "cat_id": item.cat_id}]
    # Add the category and the items list as an entry in the data list.
    data.append({"id": category.id, "name": category.name, "item": itemList})
    # Return the category and item data in JSON format.
    return jsonify(Category=data)


@app.route('/catalog/users.json')
def get_users():

    users = session.query(User).all()
    return jsonify(User=[u.serialize for u in users])


# --------------------------------------------------------
# OAUTH CODE GOES HERE ----------------------------------
# --------------------------------------------------------


@app.route('/storeauthcode', methods=['POST'])
def storeAuthCode():

    # Find the authorisation code in the POST data field.
    auth_code = request.data
    # print ("Step 1 - Complete, received auth code %s" % auth_code)

    # If request does not have `X-Requested-With` header, this could be a CSRF
    if not request.headers.get('X-Requested-With'):
        abort(403)

    # Set path to the Web application client_secret.json file
    CLIENT_SECRET_FILE = 'client_secrets.json'

    # Client ID.
    CLIENT_ID = json.loads(
            open('client_secrets.json', 'r').read())['web']['client_id']
    try:
        # Exchange auth code for access token, refresh token, and ID token
        credentials = client.credentials_from_clientsecrets_and_code(
                CLIENT_SECRET_FILE,
                ['https://www.googleapis.com/auth/drive.appdata', 'profile',
                 'email'], auth_code)
    except client.FlowExchangeError:
        response = make_response(json.dumps(
                'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get profile info from ID token
    # userid = credentials.id_token['sub']
    # email = credentials.id_token['email']
    # print ("Step 2 - Complete, %s %s %s" % (credentials.id_token,
    # credentials.access_token,credentials.refresh_token))

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads((h.request(url, 'GET')[1]).decode())

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    googleid = credentials.id_token['sub']
    if result['user_id'] != googleid:
        response = make_response(json.dumps(
                "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
                "Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # print ("Step 2 Complete! Access Token : %s " % credentials.access_token)

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    name = data['name']
    picture = data['picture']
    email = data['email']

    # print ("Step 3 Complete! User info: %s %s %s " % (name,picture,email))

    # See if user exists, if it doesn't make a new one
    user = session.query(User).filter_by(email=email).first()
    if not user:
        user = User(username=name, picture=picture, email=email)
        session.add(user)
        session.commit()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # flash("you are now logged in as %s" % login_session['username'])

    # Return to the main items list page for that category.
    return redirect(url_for('categoryList'))


'''
@app.route('/disconnect')
def disconnect():

    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
                json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
        'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
'''


@app.route('/login')
def login():

    # Return the login page with Google sign-in.
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():

    # If the user is logging out run this code.
    if request.method == 'POST':
        # Disconnect from Google
        # disconnect()
        # remove the username from the session if it is there
        login_session.pop('username', None)
        # flash ('you have been logged out')
        return redirect(url_for('categoryList'))
    else:
        return render_template('logout.html')


# -------------------------------------------------
# If this script is being executed in the context of main  it will run the
# app class with the below parameters.
# -------------------------------------------------


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    # app.debug = True
    app.run(host='0.0.0.0', port=8000)
