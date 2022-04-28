from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


# Below are the models (e.g. classes) for all of your tables.

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    # Define the relationship to Student via StudentCourses
    students = db.relationship('Student', secondary='student_courses')

    def __str__(self):
        students = "["
        for stud in self.students:
            students = students + stud.name + ','
        students = students + "]"
        string_object = str(self.id) + "|" + str(self.name) +"|" + students
        return string_object

class StudentCourses(db.Model):
    __tablename__ = 'student_courses'
    id = db.Column(db.Integer(), primary_key=True)
    course_id = db.Column(db.Integer(), db.ForeignKey('courses.id', ondelete='CASCADE'))
    student_id = db.Column(db.Integer(), db.ForeignKey('student.id', ondelete='CASCADE'))

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    age = db.Column(db.Integer())
    student_nick_names = db.relationship("StudentNickName", backref='student', cascade='all')

    # Define the relationship to Course via StudentCourses
    courses = db.relationship('Course', secondary='student_courses', overlaps='students')

    def __str__(self):
        nick_names = "["
        for nick in self.student_nick_names:
            nick_names = nick_names + nick.nick_name + ','
        nick_names = nick_names + "]"
        courses = "["
        for course in self.courses:
            courses = courses + course.name + ','
        courses = courses + "]"
        string_object = str(self.id) + "|" + str(self.name) +"|" + str(self.email) + "|" + str(self.age) + "|" + nick_names + "|" + courses
        return string_object

class StudentNickName(db.Model):
    __tablename__ = 'student_nick_name'
    id = db.Column(db.Integer(), primary_key=True)
    nick_name = db.Column(db.String(50), unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))

    def __str__(self):
        string_object = nick_name
        return string_object

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/create_all')
def create_all():
    db.create_all()
    # TODO create the db
    message = "DB Created! (A SQLite DB File Should Appear In Your Project Folder.  " \
              "Also, if changes are made to the model, running this again should " \
              "add these changes to the db."
    return render_template('index.html', message=message)

@app.route('/drop_all')
def drop_all():
    # TODO drop the db
    db.drop_all()
    message = "DB Dropped!!"
    return render_template('index.html', message=message)

@app.route('/add_students')
def add_students():
    # TODO add two students to the DB with the following attributes:
    # name='Joe',email="joe@weber.edu",age=21
    # name='Mary', email="mary@weber.edu", age=22 | Mary's nickname: Maria
    joe = Student(name='Joe', email="joe@weber.edu", age=21)
    db.session.add(joe)
    mary = Student(name='Mary', email="mary@weber.edu", age=22)
    db.session.add(mary)
    mary = Student.query.filter(Student.name == 'Mary').all()
    nickname = StudentNickName(nick_name='Maria', student_id=mary[0].id)
    db.session.add(nickname)
    db.session.commit()
    message = "Student named Joe and Mary added to DB.  Mary's nickname also added. "
    return render_template('index.html', message=message)

@app.route('/add_nicknames_to_student')
def add_nicknames_to_student():
    # TODO associate the nicknames Jojo and Joey to Joe 
    joe = Student.query.filter(Student.name == 'Joe').all()
    nickname_one = StudentNickName(nick_name='Joe', student_id=joe[0].id)
    nickname_two = StudentNickName(nick_name='Joey', student_id=joe[0].id)
    db.session.add(nickname_one)
    db.session.add(nickname_two)
    db.session.commit()
    message = "Two nicknames (Joe and Joey) added to Joe<br>" + str(nickname_one.nick_name) + " " + str(nickname_two.nick_name)
    return render_template('index.html', message=message)

@app.route('/update_student')
def update_student():
    # TODO: change Joe's name to Joseph
    joe = Student.query.filter(Student.name == 'Joe').all()
    joe[0].name='Joseph'
    db.session.commit()
    message = "Student Joe Updated<br>" + joe[0].name
    return render_template('index.html', message=message)


@app.route('/select_student')
def select_student():
    # TODO: Retrieve the student with the email "joe@weber.edu" and display his name, email and nicknames 
    joe = Student.query.filter(Student.email == 'joe@weber.edu').first()
    message = "Query Results:<br>" +  joe.name + "<br>" + joe.email + "<br>" + '<br>'.join(str(item.nick_name) for item in joe.student_nick_names)
    return render_template('index.html', message=message)

@app.route('/select_students')
def select_students():
    # TODO: Retrieve all the students and display their names, nicknames (and later their enrollments) 
    allStudents = Student.query.all()
    message = "Query Results: <br>" + '<br>'.join(str(item.name) for item in allStudents)
    return render_template('index.html', message=message)

@app.route('/delete_student')
def delete_student():
    # TODO: Delete Joe and his associated info from the DB
    joe = Student.query.filter(Student.name.like('%jo%')).first()
    db.session.delete(joe)
    db.session.commit()
    message = "Joe deleted from DB"
    return render_template('index.html', message=message)

@app.route('/add_courses')
def add_courses():
    # TODO: Add a course named Anthro 1000 and another named English 1100 to the DB
    course1 = Course(name='Anthro 1000')
    course2 = Course(name='English 1100')
    db.session.add(course1)
    db.session.add(course2)
    db.session.commit()
    message = "Two courses added to DB"
    return render_template('index.html', message=message)

@app.route('/enroll_students')
def enroll_students():
    # TODO: Enroll Joe in Anthro and English.  Enroll Mary in Anthro.
    joe = Student.query.filter(Student.name.like('%Jo%')).first()
    mary = Student.query.filter(Student.name == 'Mary').first()
    course1 = Course.query.filter(Course.name == 'Anthro 1000').first()
    course2 = Course.query.filter(Course.name == 'English 1100').first()
    student_course1 = StudentCourses(course_id=course1.id, student_id=joe.id)
    student_course2 = StudentCourses(course_id=course2.id, student_id=joe.id)
    student_course3 = StudentCourses(course_id=course1.id, student_id=mary.id)
    joe.courses.append(course1)
    joe.courses.append(course2)
    mary.courses.append(course1)
    db.session.add(student_course1)
    db.session.add(student_course2)
    db.session.add(student_course3)
    db.session.commit()
    message = "Joe Enrolled in Anthro and English.  Mary enrolled in Anthro" + str(joe)
    return render_template('index.html', message=message)


@app.route('/show_course_enrollments')
def show_course_enrollments():
    # TODO: Show the enrollments for Anthro and English
    anthro = Course.query.filter(Course.name == 'Anthro 1000').first()
    english = Course.query.filter(Course.name == 'English 1100').first()
    message = "Course Enrollments:<br> Anthro: " + ', '.join(str(item.name) for item in anthro.students) + "<br>English: " + ''.join(str(item.name) for item in english.students)
    return render_template('index.html', message=message)

@app.route('/show_student_enrollments')
def show_student_enrollments():
    # TODO: Show Joe's enrollments
    joe = Student.query.filter(Student.name.like('%Jo%')).first()
    message = "Joe is enrolled in:<br> &nbsp;" + '<br>&nbsp;'.join(str(item.name) for item in joe.courses)
    return render_template('index.html', message=message)
