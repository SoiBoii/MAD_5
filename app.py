from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/sai/MAD_prac5/database.sqlite3'
db = SQLAlchemy(app)
app.app_context().push()

class Student(db.Model):
    _tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    courses = db.relationship("Course", secondary = "enrollment")

class Course(db.Model):
    __tablename__='course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    course_description = db.Column(db.String(500))

class Enrollment(db.Model):
    __tablename__='enrollment'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

    #student = db.relationship('Student', backref=db.backref('enrollments', cascade='all, delete-orphan'))
    #student = db.relationship('Student')
    #course = db.relationship('Course')

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        roll_number = request.form['roll']
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        course_ids = request.form.getlist('courses')
        rolls_list=Student.query.filter_by(roll_number=roll_number).all()
        
        if rolls_list !=[]:
            return render_template('error.html')


        student = Student(roll_number=roll_number, first_name=first_name, last_name=last_name)
        db.session.add(student)


        db.session.commit()

        for course_id in course_ids:
            enrollment = Enrollment(estudent_id=student.student_id, ecourse_id=int(course_id))
            db.session.add(enrollment)
        
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('create.html')


@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.first_name = request.form['f_name']
        student.last_name = request.form['l_name']
        course_ids = request.form.getlist('courses')

        # Remove existing enrollments for the student
        Enrollment.query.filter_by(estudent_id=student.student_id).delete()

        for course_id in course_ids:
            enrollment = Enrollment(estudent_id=student.student_id, ecourse_id=int(course_id))
            db.session.add(enrollment)

        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('update.html', student=student)


@app.route('/student/<int:student_id>/delete', methods=['GET', 'POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    """temp = Enrollment.query.filter_by(estudent_id = student_id).first()
    if temp is not None:            
        enroll = Enrollment.query.filter_by(estudent_id = student_id).all()
        for enrollment in enroll:
            db.session.delete(enrollment)"""
    #else:
        #return render_template('error.html')
    #Enrollment.query.filter_by(estudent_id = student_id).delete()
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/student/<int:student_id>')
def student_details(student_id):
    estudent_id=student_id
    student = Student.query.get_or_404(student_id)
    #enrollments = Enrollment.query.filter_by(estudent_id=student_id).all()
    enrollments = Enrollment.query.filter_by(estudent_id=student_id).all()
    #courses = Course.query.filter_by(course_id=enrollments)
    return render_template('student_details.html', student=student, enrollments=enrollments)


if __name__ == '__main__':
    app.run(debug=True)
