from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# 1. ตั้งค่าให้หาไฟล์ HTML ในโฟลเดอร์ปัจจุบัน (.)
app = Flask(__name__, template_folder='.')

app.secret_key = "secret_key_for_session" 

# ตั้งค่า Database และ Path หลักของโปรเจค
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'project_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ตั้งค่าที่เก็บไฟล์ Upload (จะสร้างโฟลเดอร์ uploads แยกออกมาเอง)
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'rar'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# --- MODELS ---
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    author1 = db.Column(db.String(100), nullable=False)
    author2 = db.Column(db.String(100))
    level = db.Column(db.String(50))
    description = db.Column(db.Text)
    year = db.Column(db.String(10), nullable=False)
    file_report = db.Column(db.String(200))
    file_manual = db.Column(db.String(200))
    file_code = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)

class HistoryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50)) 
    details = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, default=datetime.now)

# --- HELPER FUNCTIONS ---
def save_file(file):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None

def log_history(action, project_name):
    new_log = HistoryLog(action=action, details=f"จัดการโปรเจค: {project_name}")
    db.session.add(new_log)
    db.session.commit()

# --- ROUTES พิเศษ (แก้ไขเรียบร้อยแล้ว!) ---
# ใช้ BASE_DIR แทน '.' เพื่อให้ Server หาไฟล์เจอแน่นอน 100%

@app.route('/style.css')
def serve_css():
    # ส่งไฟล์ style.css โดยอ้างอิงจากที่อยู่ไฟล์ app.py โดยตรง
    return send_from_directory(BASE_DIR, 'style.css')

@app.route('/script.js')
def serve_js():
    # ส่งไฟล์ script.js โดยอ้างอิงจากที่อยู่ไฟล์ app.py โดยตรง
    return send_from_directory(BASE_DIR, 'script.js')

@app.route('/uploads/<filename>')
def download_file(filename):
    # อันนี้ถูกต้องอยู่แล้ว (ใช้ app.config['UPLOAD_FOLDER'])
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- ROUTES ปกติ ---

@app.route('/')
def index():
    recent_logs = HistoryLog.query.order_by(HistoryLog.timestamp.desc()).limit(5).all()
    return render_template('index.html', logs=recent_logs)

@app.route('/projects')
def projects():
    all_projects = Project.query.order_by(Project.year.desc()).all()
    grouped_projects = {}
    for p in all_projects:
        if p.year not in grouped_projects:
            grouped_projects[p.year] = []
        grouped_projects[p.year].append(p)
    return render_template('projects.html', grouped_projects=grouped_projects)

@app.route('/history')
def history():
    logs = HistoryLog.query.order_by(HistoryLog.timestamp.desc()).all()
    return render_template('history.html', logs=logs)

@app.route('/add_project', methods=['POST'])
def add_project():
    try:
        name = request.form['name']
        author1 = request.form['author1']
        author2 = request.form['author2'] or "-"
        level = request.form['level']
        description = request.form['description']
        
        year_select = request.form['year_select']
        year_custom = request.form.get('year_custom', '').strip()
        year = year_custom if year_select == 'other' else year_select

        f_report = save_file(request.files['file_report'])
        f_manual = save_file(request.files['file_manual'])
        f_code = request.form.get('github_link') 
        if not f_code: 
             f_code_file = request.files.get('file_code')
             if f_code_file:
                 f_code = save_file(f_code_file)

        new_project = Project(
            name=name, author1=author1, author2=author2, level=level,
            description=description, year=year,
            file_report=f_report, file_manual=f_manual, file_code=f_code
        )
        db.session.add(new_project)
        db.session.commit()
        
        log_history("เพิ่มโปรเจค", name)
        flash('บันทึกสำเร็จ!', 'success')
        
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    name = project.name
    db.session.delete(project)
    db.session.commit()
    log_history("ลบโปรเจค", name)
    flash('ลบข้อมูลเรียบร้อย', 'success')
    return redirect(url_for('projects'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
