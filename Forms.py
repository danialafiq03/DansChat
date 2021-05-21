from wtforms import Form, StringField, SelectField, validators, PasswordField


class RegisterForm(Form):
    first_name = StringField('First Name', [validators.Length(min=3, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=2, max=150), validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    email = StringField('Email', [validators.DataRequired(), validators.Email("Invalid Email")])
    password = PasswordField('Password', [validators.DataRequired(),validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')
