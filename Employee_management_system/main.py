from flask import Flask, flash, render_template, request,redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt

app=Flask(__name__)
app.config["SECRET_KEY"]='65b0b774279de460f1cc5c92'
app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:@localhost/userManagementSystem"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
Session(app)

# User Class
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(255), nullable=False)
    email=db.Column(db.String(255), nullable=False)
    password=db.Column(db.String(255), nullable=False)
    status=db.Column(db.Integer,default=1, nullable=False)

    def __repr__(self):
        return f'User("{self.id}","{self.username}","{self.email}","{self.status}")'
# Data model 

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_field1 = db.Column(db.String(255), nullable=False)
    data_field2 = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Data("{self.id}", "{self.data_field1}", "{self.data_field2}")'
# create admin Class
class Admin(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(255), nullable=False)
    password=db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Admin("{self.username}","{self.id}")'

# create table
with app.app_context():
    # Create database tables
    db.create_all()
# insert admin data one time only one time insert this data
# latter will check the condition
    if not Admin.query.first():
        admin = Admin(username='admin', password=bcrypt.generate_password_hash('admin', 10))
        db.session.add(admin)
        db.session.commit()

# main index 
@app.route('/')
def index():
    return render_template('index.html',title="")


# admin loign
@app.route('/admin/',methods=["POST","GET"])
def adminIndex():
    # chect the request is post or not
    if request.method == 'POST':
        # get the value of field
        username = request.form.get('username')
        password = request.form.get('password')
        # check the value is not empty
        if username=="" and password=="":
            flash('Please fill all the field','danger')
            return redirect('/admin/')
        else:
            # login admin by username 
            admins=Admin().query.filter_by(username=username).first()
            if admins and bcrypt.check_password_hash(admins.password,password):
                session['admin_id']=admins.id
                session['admin_name']=admins.username
                flash('Login Successfully','success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Email and Password','danger')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html',title="Admin Login")

# admin Dashboard
@app.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    totalUser=User.query.count()
    totalApprove=User.query.filter_by(status=1).count()
    NotTotalApprove=User.query.filter_by(status=0).count()
    return render_template('admin/dashboard.html',title="Admin Dashboard",totalUser=totalUser,totalApprove=totalApprove,NotTotalApprove=NotTotalApprove)

# admin get all user 
@app.route('/admin/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method== "POST":
        search=request.form.get('search')
        users=User.query.filter(User.username.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='Approve User',users=users)
    else:
        users=User.query.all()
        return render_template('admin/all-user.html',title='Approve User',users=users)

@app.route('/admin/approve-user/<int:id>')
def adminApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    User().query.filter_by(id=id).update(dict(status=1))
    db.session.commit()
    flash('Approve Successfully','success')
    return redirect('/admin/get-all-user')

# change admin password
@app.route('/admin/change-admin-password',methods=["POST","GET"])
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('Please fill the field','danger')
            return redirect('/admin/change-admin-password')
        else:
            Admin().query.filter_by(username=username).update(dict(password=bcrypt.generate_password_hash(password,10)))
            db.session.commit()
            flash('Admin Password update successfully','success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)

# admin logout
@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')
# -------------------------user area----------------------------


# User login
@app.route('/user/',methods=["POST","GET"])
def userIndex():
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=="POST":
        # get the name of the field
        email=request.form.get('email')
        password=request.form.get('password')
        # check user exist in this email or not
        users=User().query.filter_by(email=email).first()
        if users and bcrypt.check_password_hash(users.password,password):
            # check the admin approve your account are not
            is_approve=User.query.filter_by(id=users.id).first()
            # first return the is_approve:
            if is_approve.status == 0:
                flash('Your Account is not approved by Admin','danger')
                return redirect('/user/')
            else:
                session['user_id']=users.id
                session['username']=users.username
                flash('Login Successfully','success')
                return redirect('/user/dashboard')
        else:
            flash('Invalid Email and Password','danger')
            return redirect('/user/')
    else:
        return render_template('user/index.html',title="User Login")

# User Register
@app.route('/user/signup',methods=['POST','GET'])
def userSignup():
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=='POST':
        # get all input field name
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        # check all the field is filled are not
        if username =="" or email=="" or password=="":
            flash('Please fill all the field','danger')
            return redirect('/user/signup')
        else:
            is_email=User().query.filter_by(email=email).first()
            if is_email:
                flash('Email already Exist','danger')
                return redirect('/user/signup')
            else:
                hash_password=bcrypt.generate_password_hash(password,10)
                user=User(username=username,email=email,password=hash_password)
                db.session.add(user)
                db.session.commit()
                flash('Account Created Successfully  ','success')
                return redirect('/user/')
    else:
        return render_template('user/signup.html',title="User Signup")


# user dashboard
@app.route('/user/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User().query.filter_by(id=id).first()
    data = Data.query.all()
    return render_template('user/dashboard.html',title="User Dashboard",users=users,data=data)

# user logout
@app.route('/user/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/user/')

    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/user/')

@app.route('/user/change-password',methods=["POST","GET"])
def userChangePassword():
    if not session.get('user_id'):
        return redirect('/user/')
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        if email == "" or password == "":
            flash('Please fill the field','danger')
            return redirect('/user/change-password')
        else:
            users=User.query.filter_by(email=email).first()
            if users:
               hash_password=bcrypt.generate_password_hash(password,10)
               User.query.filter_by(email=email).update(dict(password=hash_password))
               db.session.commit()
               flash('Password Change Successfully','success')
               return redirect('/user/change-password')
            else:
                flash('Invalid Email','danger')
                return redirect('/user/change-password')

    else:
        return render_template('user/change-password.html',title="Change Password")

# user update profile
@app.route('/user/update-profile', methods=["POST","GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User.query.get(id)
    if request.method == 'POST':
        # get all input field name
        username=request.form.get('username')
        email=request.form.get('email')
        if username =="" or email=="":
            flash('Please fill all the field','danger')
            return redirect('/user/update-profile')
        else:
            session['username']=None
            User.query.filter_by(id=id).update(dict(username=username,email=email))
            db.session.commit()
            session['username']=username
            flash('Profile update Successfully','success')
            return redirect('/user/dashboard')
    else:
        return render_template('user/update-profile.html',title="Update Profile",users=users)
@app.route('/admin/new-user', methods=['GET', 'POST'])
def adminNewUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([username, email, password]):
            flash('Please fill all the fields', 'danger')
            return redirect('/admin/new-user')
        else:
            is_email = User.query.filter_by(email=email).first()
            if is_email:
                flash('Email already exists', 'danger')
                return redirect('/admin/new-user')
            else:
                hash_password = bcrypt.generate_password_hash(password, 10)
                user = User(username=username, email=email, password=hash_password)
                db.session.add(user)
                db.session.commit()
                flash('User added successfully', 'success')
                return redirect('/admin/get-all-user')
    return render_template('admin/addnewuser.html', title="Add New User")
@app.route('/admin/edit-user/<int:id>', methods=['GET', 'POST'])
def adminEditUser(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    user = User.query.get(id)
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([username, email]):
            flash('Please fill all the required fields', 'danger')
            return redirect(f'/admin/edit-user/{id}')
        else:
            user.username = username
            user.email = email
            if password:
                user.password = bcrypt.generate_password_hash(password, 10)
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect('/admin/get-all-user')
    return render_template('admin/edituser.html', title="Edit User", user=user)
@app.route('/admin/delete-user/<int:id>')
def adminDeleteUser(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    else:
        flash('User not found', 'danger')

    return redirect('/admin/get-all-user')
# employee add new data
@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def userEditData(id):
    data = Data.query.get_or_404(id)
    if request.method == 'POST':
        # Get form data
        data_field1 = request.form.get('data_field1')
        data_field2 = request.form.get('data_field2')
        # Check if all fields are filled
        if not all([data_field1, data_field2]):
            flash('Please fill all the fields', 'danger')
            return redirect(f'/user/edit/{id}')
        else:
            # Update the data in the database
            data.data_field1 = data_field1
            data.data_field2 = data_field2
            db.session.commit()
            flash('Data updated successfully', 'success')
            return redirect('/user/dashboard')
    return render_template('user/edit.html', title="Edit Data", data=data)

@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get(id)
    if request.method == 'POST':
        # Update user data
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form['password']:
            user.password = bcrypt.generate_password_hash(request.form['password'])
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect('/user/dashboard')
    return render_template('edit.html', title='Edit User', user=user)

@app.route('/user/delete/<int:id>', methods=['GET', 'POST'])
@app.route('/user/delete-data/<int:id>', methods=['POST'])
def delete_data(id):
    data = Data.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    flash('Data deleted successfully', 'success')
    return redirect('/user/dashboard')
if __name__=="__main__":
    app.run(debug=True)