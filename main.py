from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, CreatePostForm
from flask_gravatar import Gravatar
from data import all_q

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
import random


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)

Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Job.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    resume = db.Column(db.LargeBinary)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    JD = relationship("JD", back_populates="author")


class JD(db.Model):
    __tablename__ = "JD"
    id = db.Column(db.Integer, primary_key=True)
    s1 = db.Column(db.String(250), nullable=False)
    s2 = db.Column(db.String(250), nullable=False)
    s3 = db.Column(db.String(250), nullable=False)
    s4 = db.Column(db.String(250), nullable=False)
    s5 = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="JD")
    cname = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

db.create_all()


def extract_text_from_pdf(pdf_data):
    with io.BytesIO(pdf_data) as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
            yield text
            converter.close()
            fake_file_handle.close()

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def get_all_posts():
    posts = JD.query.all()

    return render_template("index.html", all_posts=posts, current_user=current_user)

@app.route('/Recommend')
def recommend():
    posts = JD.query.all()
    if current_user.id:
        user = User.query.get(current_user.id)
        pdf = user.resume


        event_pre = {}
        post_id = {}
        match  = []
        a = ""
        for page in extract_text_from_pdf(pdf):
            a += ' ' + page

        b = a.index("Skills")
        c = a.find("\n\n", b + 7)
        d = a[b + 8:c]
        user_pre = d.split("\n")
        user_pre = [x.upper() for x in user_pre]




        print(user_pre)

        for post in posts:
            event = {
                post.id: [post.s1.upper(), post.s2.upper(), post.s3.upper(), post.s4.upper(), post.s5.upper()]
            }
            event_pre.update(event)
        print(event_pre)
        for key, val in event_pre.items():
            list1 = []
            for i in range(0, 5):
                if val[i] in user_pre:
                    list1.append(val[i])
            print(list1)
            match_per = round(len(list1) / 5,3)
            if match_per >.5:
                newpost = {
                    JD.query.filter_by(id=key):match_per*100
                }

                post_id.update(newpost)



        return render_template("index1.html", posts=post_id,current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())

            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        pdf_file = form.pdf_file.data
        file_data = pdf_file.read()


        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
            resume = file_data

        )


        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))


    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])

def show_post(post_id):
    requested_post = JD.query.get(post_id)
    return render_template("post.html", post=requested_post, current_user=current_user)


@app.route("/test/<int:post_id>")
def test(post_id):
    post = JD.query.get(post_id)
    list1=[]
    index = []
    if current_user.id:
        user = User.query.get(current_user.id)
        pdf = user.resume

        a = ""
        for page in extract_text_from_pdf(pdf):
            a += ' ' + page

        b = a.index("Skills")
        c = a.find("\n\n", b + 7)
        d = a[b + 8:c]
        user_pre = d.split("\n")
        user_pre = [x.upper() for x in user_pre]
        print(user_pre)


        event = [post.s1.upper(), post.s2.upper(), post.s3.upper(), post.s4.upper(), post.s5.upper()]


        print(event)

        for i in range(0, len(user_pre)):
            if user_pre[i] in event:
                list1.append(user_pre[i])
        print(list1)


    domain={
        "CSS":0,
        "C++":10,
       "C":20,
        "PYTHON":30,

        "SQL":40,
        "FLASK":50

    }
    domainl = ["C++","SQL","PYTHON","CSS","C","FLASK"]
    start =[]
    for item in list1:
        if item in domainl:
            start.append(domain[item])
    print(start)
    for i in start:
        x = random.sample(range(i,i+10),2)
        index.append(x[0])
        index.append(x[1])
    print(index)

    raw_q = []
    for i in index:
        raw_q.append(all_q[i])
    print(raw_q)



    def write_questions_to_js_file(questions, filename):
        with open(filename, 'w') as file:
            file.write('const questions = [\n')
            for question in questions:

                file.write('  {\n')
                file.write(f'    numb:{question["numb"]},\n')
                file.write(f'    question: "{question["question"]}",\n')
                file.write(f'    answer: "{question["answer"]}",\n')
                file.write('    options: [\n')
                for option in question['options']:
                    file.write(f'      "{option}",\n')
                file.write('    ]\n')
                file.write('  },\n')


            file.write('];\n')

    write_questions_to_js_file(raw_q, 'static/js-1/questions.js')

    return render_template("test.html",rno = random.randint(2,100))


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = JD(
            title=form.title.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
            s1 = form.s1.data,
            cname = form.company.data,
        s2 = form.s2.data,
        s3 = form.s3.data,
        s4 = form.s4.data,
        s5 = form.s5.data
        )


        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)




@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = JD.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,

        img_url=post.img_url,
        author=current_user,
        body=post.body,
        company =post.cname,
    s1 = post.s1,
    s2 = post.s2,
    s3 = post.s3,
    s4 = post.s4,
    s5 = post.s5
    )
    if edit_form.validate_on_submit():
        post.s1 = edit_form.s1.data
        post.s2 = edit_form.s2.data
        post.s3 = edit_form.s3.data
        post.s4 = edit_form.s4.data
        post.s5 = edit_form.s5.data
        post.cname = edit_form.company.data
        post.title = edit_form.title.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = JD.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
