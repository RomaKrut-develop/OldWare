from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Category, Forum, Topic, Post, bcrypt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oldware.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создаем тестовые данные
@app.before_first_request
def create_tables():
    db.create_all()
    # Создаем тестовые категории и форумы
    if not Category.query.first():
        cat1 = Category(name="Компьютерные технологии 90-х")
        cat2 = Category(name="Мобильные технологии 2000-х")
        
        forum1 = Forum(name="Железо и периферия", 
                      description="Обсуждение процессоров, видеокарт, модемов", 
                      category=cat1)
        forum2 = Forum(name="Операционные системы", 
                      description="Windows 95/98/ME, DOS, OS/2", 
                      category=cat1)
        forum3 = Forum(name="Кнопочные телефоны", 
                      description="Nokia, Siemens, Ericsson", 
                      category=cat2)
        
        db.session.add_all([cat1, cat2, forum1, forum2, forum3])
        db.session.commit()

# Маршруты аутентификации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Ошибка входа. Проверьте email и пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Основные маршруты форума
@app.route('/')
def index():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/forum/<int:forum_id>')
def forum(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    topics = Topic.query.filter_by(forum_id=forum_id).order_by(Topic.date_posted.desc()).all()
    return render_template('forum.html', forum=forum, topics=topics)

@app.route('/topic/<int:topic_id>')
def topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    posts = Post.query.filter_by(topic_id=topic_id).order_by(Post.date_posted.asc()).all()
    return render_template('topic.html', topic=topic, posts=posts)

@app.route('/new_topic/<int:forum_id>', methods=['GET', 'POST'])
@login_required
def new_topic(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        new_topic = Topic(title=title, user_id=current_user.id, forum_id=forum_id)
        db.session.add(new_topic)
        db.session.commit()
        
        new_post = Post(content=content, user_id=current_user.id, topic_id=new_topic.id)
        db.session.add(new_post)
        db.session.commit()
        
        flash('Тема успешно создана!', 'success')
        return redirect(url_for('topic', topic_id=new_topic.id))
    
    return render_template('new_topic.html', forum=forum)

@app.route('/new_post/<int:topic_id>', methods=['POST'])
@login_required
def new_post(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    content = request.form['content']
    
    new_post = Post(content=content, user_id=current_user.id, topic_id=topic_id)
    db.session.add(new_post)
    db.session.commit()
    
    flash('Сообщение добавлено!', 'success')
    return redirect(url_for('topic', topic_id=topic_id))

if __name__ == '__main__':
    app.run(debug=True)