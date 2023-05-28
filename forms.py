from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField



class CreatePostForm(FlaskForm):
    s1 = StringField("Skill-1", validators=[DataRequired()])
    s2 = StringField("Skill-2", validators=[DataRequired()])
    s3 = StringField("Skill-3", validators=[DataRequired()])
    s4 = StringField("Skill-4", validators=[DataRequired()])
    s5 = StringField("Skill-5", validators=[DataRequired()])
    company = StringField("Company Name", validators=[DataRequired()])
    title = StringField("Job Title", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Job Description", validators=[DataRequired()])
    submit = SubmitField("Submit JD")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    pdf_file = FileField('PDF File', validators=[FileRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")

