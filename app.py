from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

# Startup Variables
choices = [(1, 'Blue'), (2, 'Grey'), (3, 'Green'), (4, 'Red'), (5, 'Yellow')]
colors = {1: 'primary', 2: 'secondary', 3: 'success', 4: 'danger', 5: 'warning'}

# App Config
app = Flask(__name__)
app.secret_key = "2!j@56czUkTQ53"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"
db = SQLAlchemy()
db.init_app(app)


# Task database Model
class Tasks(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(250), nullable=False)
    category = db.Column(db.Integer, nullable=False)
    checked = db.Column(db.Boolean, default=False, nullable=False)


with app.app_context():
    db.create_all()


# Forms
class NewTaskForm(FlaskForm):
    content = StringField('Content', validators=[DataRequired()], render_kw={'class': 'form-control', 'placeholder': 'insert task here'})
    category = SelectField('Category', choices=choices,  render_kw={'class': 'form-select'})
    submit = SubmitField('Add', render_kw={'class': 'btn btn-success'})


# # Routes
# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    form = NewTaskForm()
    if form.validate_on_submit():
        new_task = Tasks(
            content=form.content.data,
            category=form.category.data,
            checked=0
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    all_tasks = db.session.query(Tasks).order_by(Tasks.checked, Tasks.id.desc()).all()
    return render_template('index.html', form=form, tasks=all_tasks, colors=colors)


# Update task route
@app.route('/update/<int:task_id>', methods=['GET', 'POST'])
def update(task_id):
    task_edit = Tasks.query.get_or_404(task_id)
    form = NewTaskForm(
        content=task_edit.content,
        category=task_edit.category
    )
    if form.validate_on_submit():
        task_edit.content = form.content.data
        task_edit.category = form.category.data
        db.session.commit()
        return redirect(url_for('home'))
    form.submit.label.text = "Update"
    return render_template('edit.html', form=form, colors=colors, task_id=task_id)


# Delete task route
@app.route('/delete/<int:task_id>')
def delete(task_id):
    task_delete = Tasks.query.get_or_404(task_id)
    db.session.delete(task_delete)
    db.session.commit()
    return redirect(url_for('home'))


# Check and uncheck tasks
@app.route('/check/<int:task_id>')
def check(task_id):
    task = Tasks.query.get_or_404(task_id)
    if task.checked == 0:
        task.checked = 1
    else:
        task.checked = 0
    db.session.commit()
    return redirect(url_for('home'))


# App Run
if __name__ == '__main__':
    app.run()
