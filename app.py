from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm, PostForm, CommentForm, CategoryForm
from models import db, User, Post, Comment, Category
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime # Для индетификации создания публикаций, комментариев и т.д
from secret import SECRET # Импортируем секрет Полишенеля. (Это никому нельзя показывать)

app = Flask(__name__) # Создаем переменную в которую передаем основной конструктор приложения
app.config['SECRET_KEY'] = SECRET # Секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Инициализация базы данных
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', form=form, error='Неправильное имя или пароль')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    error = None
    
    if form.validate_on_submit():
        # Проверка существующего пользователя
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            error = 'Такой пользователь существует'
        else:
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(
                username=form.username.data, 
                email=form.email.data, 
                password=hashed_password,
                is_admin=False
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    
    # Добавим отладочную информацию
    print(f"Form submitted: {request.method == 'POST'}")
    print(f"Form validate: {form.validate()}")
    print(f"Form errors: {form.errors}")
    
    return render_template('register.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return "Forbidden", 403
    categories = Category.query.all()
    return render_template('admin.html', categories=categories)

@app.route('/create_category', methods=['GET', 'POST'])
@login_required
def create_category():
    if not current_user.is_admin:
        return "Forbidden", 403
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(
            name=form.name.data, 
            description=form.description.data
        )
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('create_category.html', form=form)

@app.route('/category/<int:category_id>')
def view_category(category_id):
    category = Category.query.get_or_404(category_id)
    posts = Post.query.filter_by(category_id=category_id).order_by(Post.created_at.desc()).all()
    return render_template('category.html', category=category, posts=posts)

@app.route('/create_post/<int:category_id>', methods=['GET', 'POST'])
@login_required
def create_post(category_id):
    category = Category.query.get_or_404(category_id)
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            category_id=category_id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('view_category', category_id=category_id))
    return render_template('create_post.html', form=form, category=category)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
            
        new_comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post_id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('view_post', post_id=post_id))
    
    return render_template('post.html', post=post, form=form, comments=comments)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.is_admin or current_user.id == comment.user_id:
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('view_post', post_id=comment.post_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Создание начального админа, если его нет
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('adminpass'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)