from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя', validators=[
        DataRequired(), 
        Length(min=4, max=20, message='Имя должно содержать от 4 до 20 символов')
    ])
    email = StringField('Электронная почта', validators=[
        DataRequired(), 
        Email(message='Неверная электронная почта')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(), 
        Length(min=6, message='Пароль должен содержать хотя бы 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Отправить!')

class PostForm(FlaskForm):
    title = StringField('Наименование', validators=[
        DataRequired(), 
        Length(max=150, message='Наименование публикации не должно привышать 150 символов')
    ])
    content = TextAreaField('Содержимое', validators=[DataRequired()])
    submit = SubmitField('Создать')

class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[
        DataRequired(), 
        Length(max=500, message='Комментарий не должен привышать 500 символов')
    ])
    submit = SubmitField('Отправить!')

class CategoryForm(FlaskForm):
    name = StringField('Наименование категории', validators=[
        DataRequired(), 
        Length(max=100, message='Наименование категории не должно привышать 100 символов')
    ])
    description = StringField('Описание', validators=[
        Length(max=200, message='Описание категории не должно привышать 200 символов')
    ])
    submit = SubmitField('Создать')