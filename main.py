import datetime
import os

import pymysql
from flask import Flask, render_template, session, request, redirect

conn = pymysql.connect(host="localhost", user="root", password="root", db="student_course_enrollment")
cursor = conn.cursor()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
Student_course_enrollment_files_path = APP_ROOT + "/static/course_materials"

app = Flask(__name__)
app.secret_key = "root"

admin_username = "admin"
admin_password = "admin"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/professor_login")
def professor_login():
    return render_template("professor_login.html")


@app.route("/student_login")
def student_login():
    return render_template("student_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == admin_username and password == admin_password:
        session['role'] = 'admin'
        return redirect("/admin_home")
    else:
        return render_template("admin_message.html", message="Invalid Login Credentials")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/professor")
def professor():
    keyword = request.args.get("keyword")
    print(keyword)
    if keyword == None:
        keyword =""
    if keyword == "":
        cursor.execute("select * from professor")
    else:
        cursor.execute("select * from professor where first_name like '%"+str(keyword)+"%' or last_name like '%"+str(keyword)+"%' or email like '%"+str(keyword)+"%' or designation like '%"+str(keyword)+"%'   ")
    professors = cursor.fetchall()
    return render_template("professor.html", professors=professors)


@app.route("/add_professor_action", methods=['post'])
def add_professor_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    designation = request.form.get("designation")
    count = cursor.execute("select * from professor where email ='"+str(email)+"' ")
    if count > 0:
        return render_template("admin_message.html", message="Duplicate Email !")
    count = cursor.execute("select * from professor where phone = '"+str(phone)+"' ")
    if count > 0:
        return render_template("admin_message.html", message="Duplicate Phone Number")
    cursor.execute("insert into professor(first_name,last_name,email,phone,password,designation,isLogged) values('"+str(first_name)+"','"+str(last_name)+"','"+str(email)+"','"+str(phone)+"','"+str(password)+"','"+str(designation)+"', '"+str(False)+"') ")
    conn.commit()
    return redirect("/professor")
    # return render_template("admin_message.html", message="Professor Added Successfully")


@app.route("/student")
def student():
    keyword = request.args.get("keyword")
    print(keyword)
    if keyword == None:
        keyword = ""
    if keyword == "":
        cursor.execute("select * from student")
    else:
        cursor.execute("select * from student where first_name like '%" + str(keyword) + "%' or last_name like '%" + str(keyword) + "%' or email like '%" + str(keyword) + "%' or phone like '%" + str(keyword) + "%'   ")
    students = cursor.fetchall()
    return render_template("student.html", students=students)


@app.route("/add_student_action", methods=['post'])
def add_student_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    dob = request.form.get("dob")
    count = cursor.execute("select * from student where email = '"+str(email)+"' ")
    if count > 0:
        return render_template("admin_message.html", message=" Duplicate Email !")
    count = cursor.execute("select * from student where phone = '"+str(phone)+"'")
    if count > 0:
        return render_template("admin_message.html", message=" Duplicate Phone Number !")
    cursor.execute("insert into student(first_name,last_name,email,phone,password,dob,isLogged) values('"+str(first_name)+"','"+str(last_name)+"','"+str(email)+"','"+str(phone)+"','"+str(password)+"','"+str(dob)+"', '"+str(False)+"')")
    conn.commit()
    return redirect("/student")
    # return render_template("admin_message.html", message="Student Added Successfully")


@app.route("/course")
def course():
    if session['role'] == 'admin':
        sql="select * from course"
    elif session['role'] == 'professor':
        sql = "select * from course where course_id  in(select course_id from section where professor_id='"+str(session['professor_id'])+"')"
    cursor.execute(sql)
    courses = cursor.fetchall()
    return render_template("course.html", courses=courses)


@app.route("/add_course_action", methods=['post'])
def add_course_action():
    course_name = request.form.get("course_name")
    count = cursor.execute("select * from course where course_name='"+str(course_name)+"' ")
    if count > 0:
        return render_template("admin_message.html", message="This Course Already Added")
    else:
        cursor.execute("insert into course(course_name) values('"+str(course_name)+"')")
        conn.commit()
        return redirect("/course")
    # return render_template("admin_message.html", message="Course Added Successfully")


@app.route("/section")
def section():
    course_id = request.args.get("course_id")
    if session['role']=='professor':
        if course_id is None:
            cursor.execute("select * from section where professor_id='" + str(session['professor_id']) + "'   ")
        else:
            cursor.execute("select * from section where professor_id='" + str(session['professor_id']) + "' and course_id='" + str(course_id) + "' ")
    elif session['role']=='admin':
        if course_id is None:
            cursor.execute("select * from section ")
        else:
            cursor.execute("select * from section where course_id='" + str(course_id) + "' ")
    elif session['role'] == 'student':
        if course_id is None:
            cursor.execute("select * from section ")
        else:
            cursor.execute("select * from section where course_id='" + str(course_id) + "' ")
    sections = cursor.fetchall()
    return render_template("section.html", sections=sections, get_is_enrollment_expired=get_is_enrollment_expired,get_professor_by_professor_id=get_professor_by_professor_id, get_course_by_course_id=get_course_by_course_id, get_enrollment_by_enrollment_id=get_enrollment_by_enrollment_id)


@app.route("/add_section_action", methods=['post'])
def add_section_action():
    crn = request.form.get("crn")
    course_id = request.form.get("course_id")
    professor_id = request.form.get("professor_id")
    class_start_date = request.form.get("class_start_date")
    class_end_date = request.form.get("class_end_date")
    room_number = request.form.get("room_number")
    day = request.form.get("day")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    number_of_students = request.form.get("number_of_students")
    number_of_credits = request.form.get("number_of_credits")
    class_start_date2 = datetime.datetime.strptime(class_start_date, "%Y-%m-%d")
    start_time2 = datetime.datetime.strptime(start_time,'%H:%M')
    start_time2 = start_time2.strftime("%H:%M")
    end_time2 = datetime.datetime.strptime(end_time, '%H:%M')
    end_time2 = end_time2.strftime("%H:%M")
    count = cursor.execute("select * from section where day='" + str(day) + "' and professor_id='" + str(
        professor_id) + "' and ((start_time >= '" + str(
        start_time2) + "' and start_time<= '" + str(
        start_time2) + "' and end_time >='" + str(
        start_time2) + "' and end_time >= '" + str(
        end_time2) + "') or (start_time <= '" + str(
        end_time2) + "' and start_time <= '" + str(
        end_time2) + "' and end_time >= '" + str(
        start_time2) + "' and end_time <= '" + str(
        end_time2) + "') or (start_time <= '" + str(
        start_time2) + "' and start_time <= '" + str(
        end_time2) + "' and end_time >= '" + str(
        start_time2) + "' and end_time >= '" + str(
        end_time2) + "') or (start_time <= '" + str(
        end_time2) + "' and start_time <= '" + str(
        end_time2) + "' and end_time <= '" + str(
        end_time2) + "' and end_time >= '" + str(end_time2) + "'))")
    if count == 0:
        count = cursor.execute("select * from section where crn = '"+str(crn)+"' ")
        if count == 0:
            cursor.execute("insert into section(crn,course_id,professor_id,class_start_date,class_end_date,room_number,day,start_time,end_time,number_of_students,number_of_credits) values('"+str(crn)+"','"+str(course_id)+"','"+str(professor_id)+"','"+str(class_start_date)+"','"+str(class_end_date)+"','"+str(room_number)+"','"+str(day)+"','"+str(start_time2)+"','"+str(end_time2)+"','"+str(number_of_students)+"','"+str(number_of_credits)+"')")
            conn.commit()
            return redirect("/section")
        return render_template("admin_message.html", message="CRN Already Exist")
    else:
        return render_template("admin_message.html", message="There is a Time Collision For Section! ")


@app.route("/add_section")
def add_section():
    cursor.execute("select * from course")
    courses = cursor.fetchall()
    cursor.execute("select * from professor")
    professors = cursor.fetchall()
    return render_template("add_section.html", courses=courses, professors=professors)


def get_professor_by_professor_id(professor_id):
    cursor.execute("select * from professor where professor_id = '"+str(professor_id)+"'")
    professors = cursor.fetchall()
    return professors[0]


def get_course_by_course_id(course_id):
    cursor.execute("select * from course where course_id= '"+str(course_id)+"'")
    courses = cursor.fetchall()
    return courses[0]


@app.route("/professor_login_action", methods=['post'])
def professor_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute(
        "select * from professor where email= '" + str(email) + "' and password = '" + str(password) + "' ")
    if count > 0:
        professor = cursor.fetchall()
        if str(professor[0][7]) == str("True"):
            session['professor_id'] = str(professor[0][0])
            session['role'] = 'professor'
            return redirect("/professor_home")
        else:
            session['professor_id'] = str(professor[0][0])
            session['role'] = 'professor'
            return render_template("changeProfessorPassword.html")
    else:
        return render_template("message.html", message="Invalid Email and Password")


@app.route("/change_professor_password_action", methods=['post'])
def change_professor_password_action():
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    professor = cursor.execute("select * from professor where professor_id='" + str(session['professor_id']) + "'")
    professor = cursor.fetchall()
    if str(new_password) != str(confirm_password):
        return render_template("professor_message.html", message="Invalid  confirm password")
    cursor.execute("update professor set password= '" + str(new_password) + "', isLogged= '" + str(True) + "' where professor_id='" + str(session['professor_id']) + "' ")
    conn.commit()
    session['professor_id'] = str(professor[0][0])
    session['role'] = 'professor'
    return redirect("/professor_home")


@app.route("/professor_home")
def professor_home():
    return render_template("professor_home.html")


@app.route("/student_login_action", methods=['post'])
def student_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from student where email= '"+str(email)+"' and password = '"+str(password)+"' ")
    if count > 0:
            student = cursor.fetchall()
            if str(student[0][7]) == str("True"):
                session['student_id'] = str(student[0][0])
                session['role'] = 'student'
                return redirect("/student_home")
            else:
                session['student_id'] = str(student[0][0])
                session['role'] = 'student'
                return render_template("changeStudentPassword.html")
    else:
        return render_template("message.html", message="Invalid Email and Password")


@app.route("/change_student_password_action", methods=['post'])
def change_student_password_action():
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    student = cursor.execute("select * from student where student_id='"+str(session['student_id'])+"'")
    student = cursor.fetchall()
    if str(new_password) != str(confirm_password):
        return render_template("student_message.html", message="Invalid  confirm password")
    cursor.execute("update student set password= '"+str(new_password)+"', isLogged= '"+str(True)+"' where student_id='"+str(session['student_id'])+"' ")
    conn.commit()
    session['student_id'] = str(student[0][0])
    session['role'] = 'student'
    return redirect("/student_home")


@app.route("/student_home")
def student_home():
    return render_template("student_home.html")


@app.route("/view_course")
def view_course():
    cursor.execute("select * from course")
    courses = cursor.fetchall()
    return render_template("view_course.html", courses=courses)


@app.route("/enroll")
def enroll():
    section_id = request.args.get("section_id")
    student_id = session['student_id']
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    day = request.args.get("day")
    start_time2 = datetime.datetime.strptime(start_time, '%H:%M')
    start_time2 = start_time2.strftime("%H:%M")
    end_time2 = datetime.datetime.strptime(end_time, '%H:%M')
    end_time2 = end_time2.strftime("%H:%M")
    count = cursor.execute("select * from section where day='" + str(
        day) + "' and section_id in(select section_id from enrollment where student_id = '" + str(
        student_id) + "' and status ='"+str("Enrolled")+"') and ((start_time >= '" + str(
        start_time2) + "' and start_time<= '" + str(
        start_time2) + "' and end_time >='" + str(
        start_time2) + "' and end_time >= '" + str(
        end_time2) + "') or (start_time <= '" + str(
        end_time2) + "' and start_time <= '" + str(
        end_time2) + "' and end_time >= '" + str(
        start_time2) + "' and end_time <= '" + str(
        end_time2) + "') or (start_time <= '" + str(
        start_time2) + "' and start_time <= '" + str(
        end_time2) + "' and end_time >= '" + str(
        start_time2) + "' and end_time >= '" + str(
        end_time2) + "') or (start_time <= '" + str(
        end_time2) + "' and start_time <= '" + str(
        end_time2) + "' and end_time <= '" + str(
        end_time2) + "' and end_time >= '" + str(end_time2) + "'))")
    if count == 0:
        cursor.execute("insert into enrollment(section_id,student_id,status) values('"+str(section_id)+"','"+str(session['student_id'])+"', 'Enrolled' )  ")
        conn.commit()
        return redirect("/section")
    else:
         return render_template("student_message.html", message="Time conflict with existing section")


@app.route("/drop_enrollment")
def drop_enrollment():
    section_id = request.args.get("section_id")
    cursor.execute("update enrollment set status = 'Dropped' where section_id = '" + str(section_id) + "' and student_id='"+str(session['student_id'])+"' ")
    conn.commit()
    return render_template("student_message.html", message="Your Course Dropped Successfully")


def get_enrollment_by_enrollment_id(enrollment_id):
    count = cursor.execute("select * from enrollment where section_id= '" + str(enrollment_id) + "' and student_id = '"+str(session['student_id'])+"' and status != 'Dropped' ")
    return count


@app.route("/view_enrollments")
def view_enrollments():
    cursor.execute("select * from enrollment where (status = '" + str('Enrolled') + "' or status = '" + str('Assigned Grade') + "')  and student_id = '"+str(session['student_id'])+"' ")
    enrollments = cursor.fetchall()
    return render_template("view_enrollments.html", enrollments=enrollments, get_section_by_section_id=get_section_by_section_id, get_course_by_course_id2=get_course_by_course_id2,get_section_by_professor_id=get_section_by_professor_id)


def get_section_by_section_id(section_id):
    cursor.execute("select * from section where section_id = '"+str(section_id)+"' ")
    section = cursor.fetchall()
    return section[0]


def get_course_by_course_id2(course_id):
    cursor.execute("select * from course where course_id = '"+str(course_id)+"' ")
    course = cursor.fetchall()
    return course[0]


def get_section_by_professor_id(professor_id):
    cursor.execute("select * from professor where professor_id = '"+str(professor_id)+"' ")
    professor = cursor.fetchall()
    return professor[0]


@app.route("/course_material")
def course_material():
    section_id = request.args.get("section_id")
    cursor.execute("select * from section")
    sections = cursor.fetchall()
    return render_template("course_material.html", section_id=section_id, sections=sections)


@app.route("/course_material_action", methods=['post'])
def course_material_action():
    section_id = request.form.get("section_id")
    course_material_name = request.form.get("course_material_name")
    description = request.form.get("description")
    material_pdf = request.files.get("material_pdf")
    path = Student_course_enrollment_files_path + "/" + material_pdf.filename
    material_pdf.save(path)
    cursor.execute("insert into course_material(section_id,course_material_name,description,material_pdf)values('"+str(section_id)+"','"+str(course_material_name)+"','"+str(description)+"','"+str(material_pdf.filename)+"') ")
    conn.commit()
    return render_template("professor_message.html", message="Course Material Added Successfully")


@app.route("/view_course_material")
def view_course_material():
    section_id = request.args.get("section_id")
    cursor.execute("select * from course_material where section_id= '"+str(section_id)+"' ")
    course_materials = cursor.fetchall()
    return render_template("view_course_material.html", section_id=section_id, course_materials=course_materials)


@app.route("/view_students")
def view_students():
    section_id = request.args.get("section_id")
    sql = ""
    if section_id is None:
        sql = "select * from enrollment where (status = '" + str('Enrolled') + "' or status = '" + str('Assigned Grade') + "') and  section_id in(select section_id from section where professor_id = '"+str(session['professor_id'])+"') "
    else:
        sql = "select * from enrollment where section_id= '"+str(section_id)+"' "
    cursor.execute(sql)
    enrollments = cursor.fetchall()
    return render_template("view_students.html", enrollments=enrollments, get_enrollment_by_student_id=get_enrollment_by_student_id, get_enrolledStudent_by_section_id=get_enrolledStudent_by_section_id, get_enrolledStudentCourse_by_course_id=get_enrolledStudentCourse_by_course_id, get_professorName_by_professor_id=get_professorName_by_professor_id)


def get_enrollment_by_student_id(student_id):
    cursor.execute("select * from student where student_id = '"+str(student_id)+"' ")
    students = cursor.fetchall()
    return students[0]


def get_enrolledStudent_by_section_id(section_id):
    cursor.execute("select * from section where section_id = '" + str(section_id) + "' ")
    sections = cursor.fetchall()
    return sections[0]


def get_enrolledStudentCourse_by_course_id(course_id):
    cursor.execute("select * from course where course_id = '" + str(course_id) + "' ")
    courses = cursor.fetchall()
    return courses[0]


def get_professorName_by_professor_id(professor_id):
    cursor.execute("select * from professor where professor_id = '" + str(professor_id) + "' ")
    professors = cursor.fetchall()
    return professors[0]


@app.route("/assignGrade")
def assignGrade():
    enrollment_id = request.args.get("enrollment_id")
    return render_template("assignGrade.html", enrollment_id=enrollment_id)


@app.route("/assignGrade_action", methods=['post'])
def assignGrade_action():
    enrollment_id = request.form.get("enrollment_id")
    grade = request.form.get("grade")
    cursor.execute("update enrollment set grade = '" + str(grade) + "',status = '" + str('Assigned Grade') + "' where enrollment_id = '"+str(enrollment_id)+"' ")
    conn.commit()
    return render_template("professor_message.html", message="Grade Assigned Successfully")


def get_is_enrollment_expired(section_id,class_start_date):
    c_date = datetime.date.today()
    count = cursor.execute("select * from section where section_id='"+str(section_id)+"' and '"+str(c_date)+"'>class_start_date ")
    if count == 0:
        return True
    else:
        return False

app.run(debug=True)

