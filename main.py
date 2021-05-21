from flask import Flask, render_template, redirect, url_for, session, request, g
from flask_socketio import SocketIO, send
import shelve
import User
import random
from Forms import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

@app.before_request
def before_request():
    if 'user_id' in session:
        try:
            db = shelve.open('register.db', 'r')
        except:
            db = shelve.open('register.db', 'c')

        user_dict = db['Users']
        for key in user_dict:
            if key == session['user_id']:
                g.user = user_dict.get(key)
        db.close()
    else:
        random_num = random.randint(0, 10000)
        session['guest_id'] = random_num


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    ################################# To prevent overwriting in database #################################
    users_dict = {}
    db = shelve.open('register.db', 'c')
    users_dict = db['Users']

    # User.User.count_id = db['Users_Count']
    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        users_list.append(user)

    db['Users_Count'] = len(users_list)  # Creates new key-value pair in Shelve db
    new_user_dict = {}

    for index, user in enumerate(users_list):
        user.set_user_id(index+1)
        new_user_dict[index+1] = user

    # Replacing db['Users'] database
    db['Users'] = new_user_dict
    db.close()
    ######################################################################################################
    error = None
    db = shelve.open('register.db', 'r')
    user_dict = db['Users']
    if request.method == 'POST':
        session.pop('user_id', None)
        email = request.form['email']
        password = request.form['psw']
        for key in user_dict:
            user = user_dict.get(key)
            if user.get_email() == email and user.get_password() == password:
                if user.get_user_id() == 1:
                    session['user_id'] = user.get_user_id()

                    return redirect(url_for('user_dashboard'))
                session['user_id'] = user.get_user_id()

                return redirect(url_for('index'))

            else:
                error = 'Invalid Credentials. Please try again.'

    db.close()
    return render_template('login.html', error=error)

@app.route('/register', methods=["GET", "POST"])
def register():

    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        users_dict = {}
        db = shelve.open('register.db', 'c')

        try:
            users_dict = db['Users']
        except:
            print("Error in retrieving Users from register.db.")
        list_of_registered_emails = []
        for key in users_dict:
            user = users_dict.get(key)
            list_of_registered_emails.append(user.get_email())
        if form.email.data in list_of_registered_emails:
            error = 'Email has already been registered!'
        else:
            try:
                User.User.count_id = db['Users_Count']+1
            except:
                users_list = []
                for key in users_dict:
                    user = users_dict.get(key)
                    users_list.append(user)
                db['Users_Count'] = len(users_list) + 1
            user = User.User(form.first_name.data, form.last_name.data, form.gender.data, form.email.data, form.password.data)
            users_dict[user.get_user_id()] = user
            db['Users'] = users_dict
            db.close()
            session['user_created'] = "You"
            return redirect(url_for('login'))
        db.close()


        return render_template('register.html', form=form, error=error)
    else:
        return render_template('register.html', form=form)

@app.route('/dashboard')
def user_dashboard():
    users_dict = {}
    db = shelve.open('register.db', 'r')
    users_dict = db['Users']

    # User.User.count_id = db['Users_Count']
    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        users_list.append(user)

    db['Users_Count'] = len(users_list)  # Creates new key-value pair in Shelve db
    new_user_dict = {}

    for index, user in enumerate(users_list):
        user.set_user_id(index+1)
        new_user_dict[index+1] = user

    # Replacing db['Users'] database
    db['Users'] = new_user_dict
    db.close()

    if 'user_id' in session and session['user_id'] == 1:
        return render_template('UserDashboard.html', count=len(users_list), users_list=users_list)
    else:
        return 'You do not have authorized access to this webpage.'

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('user_id', None)

    return redirect(url_for('index'))

@socketio.on('message')
def handleMessage(msg):
    if msg == "has connected!":
        if 'user_id' in session:
            db = shelve.open('register.db', 'r')
            user_dict = db['Users']
            user = user_dict.get(session['user_id'])
            name = user.get_full_name()
            send(name + ' ' + msg, broadcast=True)
        else:
            send('Guest #' + str(session['guest_id']) + ' ' + msg, broadcast=True)
    else:
        if 'user_id' in session:
            db = shelve.open('register.db', 'r')
            user_dict = db['Users']
            user = user_dict.get(session['user_id'])
            name = user.get_full_name()
            send('' + name + ': ' + msg, broadcast=True)
        else:
            send('Guest #' + str(session['guest_id']) + ': ' + msg, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
