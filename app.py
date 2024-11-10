import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Đặt một secret key cho session và flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/managerment'  # Sửa lại với thông tin của bạn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model Sinh Viên
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    birth_year = db.Column(db.Integer, nullable=False)

# Model Điểm
class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)
    math = db.Column(db.Float)
    literature = db.Column(db.Float)
    english = db.Column(db.Float)

# Route đăng nhập
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db_name = request.form['db_name']
        user = request.form['user']
        password = request.form['password']
        host = request.form['host']
        port = request.form['port']
        
        # Kiểm tra kết nối đến cơ sở dữ liệu PostgreSQL
        try:
            # Giả sử kết nối thành công (tạo kết nối trong app.config trước)
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('dashboard'))
        except:
            flash("Kết nối thất bại! Vui lòng kiểm tra lại thông tin đăng nhập.", "danger")
            return render_template('login.html')
    return render_template('login.html')

# Route quản lý sinh viên (Trang chính)
@app.route('/dashboard')
def dashboard():
    students = Student.query.all()
    return render_template('student_management.html', students=students)

# Route thêm sinh viên
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['student_name']
    student_id = request.form['student_id']
    birth_year = request.form['birth_year']
    
    # Kiểm tra sinh viên trùng lặp
    if Student.query.filter_by(student_id=student_id).first():
        flash("Sinh viên đã tồn tại!", "danger")
    else:
        new_student = Student(name=name, student_id=student_id, birth_year=birth_year)
        db.session.add(new_student)
        db.session.commit()
        flash("Thêm sinh viên thành công!", "success")
    return redirect(url_for('dashboard'))

# Route quản lý điểm
@app.route('/score_management')
def score_management():
    students = Student.query.all()  # Lấy danh sách sinh viên từ cơ sở dữ liệu
    scores = Score.query.all()  # Lấy dữ liệu điểm nếu cần
    return render_template('score_management.html', students=students, scores=scores)

# Route thêm điểm
@app.route('/add_score', methods=['POST'])
def add_score():
    student_id = request.form['student_id']
    math = request.form['math_score']
    literature = request.form['literature_score']
    english = request.form['english_score']

    # Kiểm tra điểm trùng lặp cho sinh viên
    if Score.query.filter_by(student_id=student_id).first():
        flash("Điểm cho sinh viên này đã tồn tại!", "danger")
    else:
        # Tạo đối tượng Score mới và lưu vào cơ sở dữ liệu
        new_score = Score(student_id=student_id, math=math, literature=literature, english=english)
        db.session.add(new_score)
        db.session.commit()
        flash("Thêm điểm thành công!", "success")
    
    return redirect(url_for('score_management'))

# Route xuất dữ liệu điểm vào file .txt
@app.route('/export_scores')
def export_scores():
    scores = Score.query.all()
    
    # Tạo nội dung cho file txt
    file_content = "Danh sách điểm sinh viên\n\n"
    for score in scores:
        file_content += (
            f"Sinh viên {score.student_id}: Toán={score.math}, "
            f"Văn={score.literature}, Anh={score.english}\n"
        )

    # Đường dẫn tới file .txt
    file_path = os.path.join(os.path.dirname(__file__), 'scores_data.txt')

    # Ghi dữ liệu vào file .txt
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(file_content)

    flash("Dữ liệu điểm đã được xuất ra file scores_data.txt!", "success")
    
    # Trả về file cho người dùng tải xuống
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
