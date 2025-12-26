import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'chuoi-bao-mat-cua-ban'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- 1. MODEL DỮ LIỆU ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    summary = db.Column(db.String(500))
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500)) # Thêm dòng này để lưu link ảnh

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Khởi tạo database và dữ liệu mẫu
with app.app_context():
    db.create_all()
    if not Story.query.first():
        sample = Story(
            title="Hành Trình Học Python",
            author="Gemini",
            summary="Câu chuyện về một lập trình viên tập sự xây dựng ứng dụng đầu tiên.",
            content="Ngày xửa ngày xưa, có một lập trình viên bắt đầu học Flask...\nĐây là nội dung chương 1."
        )
        db.session.add(sample)
        db.session.commit()

# --- 2. CÁC ĐƯỜNG DẪN (ROUTES) ---

@app.route('/')
@login_required
def index():
    stories = Story.query.all()
    return render_template('index.html', stories=stories)

@app.route('/story/<int:story_id>')
@login_required
def read_story(story_id):
    story = Story.query.get_or_404(story_id)
    return render_template('read.html', story=story)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!')
        else:
            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash('Đăng ký thành công!')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Sai tài khoản hoặc mật khẩu!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
# Route để thêm truyện mới
@app.route('/add-story', methods=['GET', 'POST'])
@login_required
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/add-story', methods=['GET', 'POST'])
@app.route('/add-story', methods=['GET', 'POST'])
@login_required
def add_story():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        summary = request.form.get('summary')
        content = request.form.get('content')
        
        # Xử lý file ảnh
        file = request.files.get('image_file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            # Tạo thư mục nếu chưa tồn tại
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"/static/uploads/{filename}"
        else:
            image_url = ""

        # Lưu vào Database
        new_story = Story(title=title, author=author, summary=summary, 
                          content=content, image_url=image_url)
        db.session.add(new_story)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('add_story.html')
# Route để xóa truyện
@app.route('/delete-story/<int:story_id>')
@login_required
def delete_story(story_id):
    # Tìm truyện theo id
    story_to_delete = Story.query.get_or_404(story_id)
    
    try:
        db.session.delete(story_to_delete)
        db.session.commit()
        flash('Đã xóa truyện thành công!', 'success')
    except:
        flash('Có lỗi xảy ra khi xóa truyện!', 'error')
        
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)