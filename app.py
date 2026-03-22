from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

app = Flask(__name__)
# Session Secret Key config
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_id_genix_v3')
app.permanent_session_lifetime = timedelta(days=7) # For Remember Me

# Production-ready Database URI using OS environment, fallback to local sqlite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'database.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SMTP Configuration (Using Env Vars)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_app_password')
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', 'admin@id-genix.local')

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)    # New mandatory field
    email = db.Column(db.String(100), nullable=False)   # New mandatory field
    service_type = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='جديد')
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.client_name}>'

def send_admin_email(task):
    """Send immediate email notification to admin via SMTP upon new order"""
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = app.config['ADMIN_EMAIL']
        msg['Subject'] = f"طلب خدمة جديد: {task.service_type} - ID-Genix"
        
        body = f"""
        لديك طلب خدمة جديد في النظام:
        
        بيانات العميل:
        - الاسم: {task.client_name}
        - رقم الهاتف: {task.phone}
        - البريد الإلكتروني: {task.email}
        
        الطلب:
        - نوع الخدمة: {task.service_type}
        - ملخص المشروع / التفاصيل:
        {task.details}
        """
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        # To test with real credentials, uncomment the line below:
        # server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        # server.send_message(msg)
        server.quit()
        print("Email notification simulation successful.")
    except Exception as e:
        print(f"Failed to send email notification: {e}")

# Session Auth checking
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('الرجاء تسجيل الدخول للمتابعة', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/order', methods=['POST'])
def order():
    if request.is_json:
        data = request.get_json()
        client_name = data.get('client_name')
        phone = data.get('phone')
        email = data.get('email')
        service_type = data.get('service_type')
        details = data.get('details')
    else:
        client_name = request.form.get('client_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        service_type = request.form.get('service_type')
        details = request.form.get('details')
    
    if not all([client_name, phone, email, service_type, details]):
        if request.is_json:
            return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة!'}), 400
        else:
            flash('جميع الحقول مطلوبة!', 'danger')
            return redirect(url_for('index'))
            
    new_task = Task(client_name=client_name, phone=phone, email=email, service_type=service_type, details=details)
    try:
        db.session.add(new_task)
        db.session.commit()
        # 4. Instant Email Notification
        send_admin_email(new_task)
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'تم استلام طلبك بنجاح!'})
        else:
            return redirect(url_for('index', success=1))
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500
        else:
            flash('حدث خطأ أثناء إرسال الطلب.', 'danger')
            return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
        ADMIN_PASS = os.environ.get('ADMIN_PASS', '123456')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_logged_in'] = True
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            return redirect(url_for('admin_dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin-portal-secure-88')
@requires_auth
def admin_dashboard():
    try:
        tasks = Task.query.order_by(Task.date.desc()).all()
    except Exception as e:
        tasks = []
        print(f"[Admin Dashboard Error] Database query failed: {e}")
        flash('تعذر جلب البيانات. يرجى التأكد من اتصال قاعدة البيانات.', 'danger')

    # 5. Advanced Dashboard Stats
    statuses = {'جديد': 0, 'قيد التنفيذ': 0, 'مكتمل': 0}
    for t in tasks:
        if t.status in statuses:
            statuses[t.status] += 1
        else:
            statuses[t.status] = 1 
            
    return render_template('admin.html', tasks=tasks, statuses=statuses)

@app.route('/admin/update_status/<int:task_id>', methods=['POST'])
@requires_auth
def update_status(task_id):
    # 5. Interactive Update DB Status
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get('status')
    if new_status in ['جديد', 'قيد التنفيذ', 'مكتمل']:
        task.status = new_status
        db.session.commit()
        flash(f'تم تحديث حالة الطلب #{task.id} بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

# Create database tables automatically (Crucial for Gunicorn/Render deployments)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Failed to create DB tables: {e}")

if __name__ == '__main__':
    app.run(debug=True)
