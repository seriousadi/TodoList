from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, validators, SubmitField, TextAreaField
from flask_wtf import FlaskForm
import json

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"
app.secret_key = "asdfasdfsafoiqwejru2q0u5c094rxdflkadsjflk"
db.init_app(app)


# wtf form
class TodolistForm(FlaskForm):
    title = StringField("list_title", validators=[validators.DataRequired()])
    subtitle = StringField('Subtitle')
    list_items = StringField('List Data', [validators.DataRequired()])
    submit = SubmitField("Add")


# todolist Model


class Todolist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    list_items = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String, nullable=True)


# creating todolist database
with app.app_context():
    db.create_all()


@app.route("/", methods=['POST', 'GET'])
def home_page():
    # reading database to check for existing list and then passing those lists to the page to show existing lists
    todolist_data = db.session.execute(db.select(Todolist).order_by()).scalars()

    form = TodolistForm()

    if request.method == 'POST' and form.validate_on_submit:
        data = request.form
        item = ""
        for n in data.getlist('listItem'):
            item = item + "@sdsplitk" + n
        # checking if that list already exists gives none or the list if it exists
        todo_list_check = db.session.execute(
            db.select(Todolist).filter_by(title=data['title'])).scalar_one_or_none()
        # using todo_list_check to decide to save or not to save the list
        if todo_list_check is None:
            list_to_save = Todolist(
                title=data['title'],
                subtitle=data['subtitle'],
                list_items=item,
            )
            db.session.add(list_to_save)
            db.session.commit()
        else:
            flash("This list already exists")
        #
        return redirect(url_for('home_page'))
    return render_template("home_page.html", todolist_data=todolist_data, form=form)


@app.route("/deletelist/<int:list_id>")
def delete_list(list_id):
    # checking if that list already exists gives none or the list if it exists
    todo_list = db.session.execute(db.select(Todolist).filter_by(id=list_id)).scalar_one_or_none()
    if todo_list is None:
        flash("This todo list doesn't exist")
    else:
        flash("successfully deleted that todolist")
        db.session.delete(todo_list)
        db.session.commit()
    return redirect(url_for('home_page'))


@app.route("/editlist/<int:list_id>", methods=['POST', 'GET'])
def edit_list(list_id):
    # checking if that list already exists gives none or the list if it exists

    todo_list = db.session.execute(db.select(Todolist).filter_by(id=list_id)).scalar_one_or_none()
    form = TodolistForm()

    # saving edited data to database
    if request.method == 'POST':
        if request.form['title'] == '':
            flash("Title cannot be empty")
            return redirect(url_for('edit_list', list_id=list_id))

        checking_todolist = db.session.execute(
            db.select(Todolist).filter_by(title=request.form['title'])).scalar_one_or_none()
        can_add = False
        if checking_todolist is None:
            can_add = True
        elif todo_list.title == checking_todolist.title and todo_list.id == checking_todolist.id:
            can_add = True
        else:
            can_add = False
            flash("Todolist with that title already exists")

        if can_add:

            data = request.form
            item = ""
            for n in data.getlist('listItem'):
                item = item + "@sdsplitk" + n
            if todo_list is None:
                flash("This todo list doesn't exist")
            else:
                todo_list.title = request.form['title']
                todo_list.subtitle = request.form['subtitle']
                todo_list.list_items = item
                db.session.commit()
                flash("Successfully updated the data")
            return redirect(url_for('home_page'))

    if todo_list is None:
        flash("This todo list doesn't exist")
    else:
        form.title.value = todo_list.title
        form.list_items.value = todo_list.list_items

    return render_template("edit.html", form=form, todolist_data=todo_list, id=list_id)


if __name__ == '__main__':
    app.run(debug=True)
