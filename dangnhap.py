from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ma-bi-mat-cua-ban'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 1. Model Người dùng
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Tạo database (Chỉ chạy lần đầu hoặc khi xóa file db)
with app.app_context():
    db.create_all()

# 2. Trang chủ
@app.route('/')
@login_required
def index():
    return f'Chào mừng {current_user.username}! <br><a href="/logout">Đăng xuất</a>'

# 3. Trang Đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Tên đăng nhập đã tồn tại!')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Đăng ký thành công!')
            return redirect(url_for('login'))
    return render_template('register.html')

# 4. Trang Đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!')
    return render_template('login.html')

# 5. Trang Đăng xuất
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#Lệnh để chạy Server
if __name__ == '_main_':
    app.run(debug=True)