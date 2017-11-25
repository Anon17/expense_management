#import modules
from flask import Flask,render_template,request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt

#initialization and configuration change the username and password of postgres
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://(username):(password)@localhost:5432/(database name)'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.secret_key = '(any random string)'
db = SQLAlchemy(app)


# Create database model for user
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = bcrypt.encrypt(password)

# Create database model for category
class category_master(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(120))
    user_id = db.Column(db.String(120))

    def __init__(self, cat_name, user_id):
        self.cat_name = cat_name
        self.user_id = user_id

# Create database model for expense
class expense_master(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120))
    cat_id = db.Column(db.Integer)
    desc = db.Column(db.String(255))
    amount = db.Column(db.Float(10,2))

    def __init__(self, user_id, cat_id, desc, amount):
        self.user_id = user_id
        self.cat_id = cat_id
        self.desc = desc
        self.amount = amount


#app logic to display login form
@app.route('/')
@app.route('/login')
def login():
    if 'username' in session:
        name = session['username']
        return render_template('index.html', name = name)
    else:
        return render_template('login.html')

#app logic for login form
@app.route('/loginuser',methods=['POST'])
def loginuser():
    error = None
    if request.method == 'POST':
        if not db.session.query(users).filter(users.username == request.form['username']).count():
            error = 'Invalid username. Please try again!'
        else:
            userdata = db.session.query(users).filter(users.username == request.form['username']).all()
            for data in userdata:
                if bcrypt.verify(request.form['pass'] ,data.password):
                    session['username'] = data.username
                    session['email'] = data.email
                    return render_template('index.html', name = request.form['username'])
                else:
                    error = 'Invalid password. Please try again!'
                    return render_template('login.html', error = error)
        return render_template('login.html', error = error)

#app logic to display registration form
@app.route('/register')
def signup():
    if 'username' in session:
        return render_template('index.html', name = session['username'])
    else:
        return render_template('register.html')


#app logic for user registration
@app.route('/registeruser', methods=['POST'])
def registeruser():
    if request.method == 'POST':
        error = None
        if not db.session.query(users).filter(users.email == request.form['email']).count():
    	   reg = users(request.form['email'],request.form['username'],request.form['pass'])
    	   db.session.add(reg)
    	   db.session.commit()
           session['username'] = request.form['username']
           session['email'] = request.form['email']
    	   return render_template('index.html', name = request.form['username'])
        else:
            error = 'Username already taken'
            return render_template('register.html',error = error)
	
	
#app logic to display dashboard page
@app.route('/home')
@app.route('/dashboard')
def index():
    if 'username' in session:
        name = session['username']
        return render_template('index.html', name = name)
    else:
        error = 'Invalid request. Please enter username and password!'
        return render_template('login.html',error = error)


#app logic to display add category page
@app.route('/category')
def category():
    if 'username' in session:
        error = None
        name = session['username']
        return render_template('category.html' , name = name)
    else:
        error = 'Invalid request. Please enter username and password!'
        return render_template('login.html',error = error)


#app logic to add category
@app.route('/addcategory', methods=['POST'])
def addcategory():
    if request.method == 'POST':
        error = None
        if not db.session.query(category_master).filter(category_master.cat_name == request.form['validate_category'],category_master.user_id == session['username']).count():
            cat = category_master(cat_name = request.form['validate_category'],user_id = session['username'])
            db.session.add(cat)
            db.session.commit()
            error = 'Category added successfully'
            name = session['username']
            return render_template('category.html', error = error, name = name)
        else:
            error = 'Category already added. Please try new name!'
            name = session['username']
            return render_template('category.html', error = error,name = name)
    return render_template('category.html',error=error)


#app logic to view all category of user
@app.route('/view-category')
def viewcategory():
    if 'username' in session:
        catdata = db.session.query(category_master).filter(category_master.user_id == session['username']).all()
        name = session['username']
        return render_template('viewcategory.html',catdata = catdata, name = name)
    else:
        error = 'Invalid request. Please enter username and password!'
        return render_template('login.html',error = error)


#app logic to display add expense page
@app.route('/add-expense')
def addexpense():
    if 'username' in session:
        catdata = db.session.query(category_master).filter(category_master.user_id == session['username']).all()
        name = session['username']
        return render_template('addexpense.html',catdata = catdata, name = name)
    else:
        error = 'Invalid request. Please enter username and password!'
        return render_template('login.html',error = error)



#app logic to add expense
@app.route('/addexpense', methods=['POST'])
def addnewexpense():
    if request.method == 'POST':
        error = None
        exp = expense_master(session['username'], request.form['validate_category'], request.form['validate_description'], request.form['validate_amount'])
        db.session.add(exp)
        db.session.commit()
        error = 'Expense Added successfully'
        name = session['username']
        return render_template('addexpense.html',error = error, name = name)


#app logic to view all expenes of user
@app.route('/view-expense')
def viewexpense():
    if 'username' in session:
        expdata = db.session.query(expense_master,category_master).filter(expense_master.cat_id == category_master.id).\
                                                                    filter(expense_master.user_id == session['username']).all()

        expdata = expense_master.query.join(category_master, expense_master.cat_id==category_master.id).add_columns(expense_master.id, expense_master.desc, expense_master.amount, category_master.cat_name).filter(expense_master.user_id == session['username']).all()
        name = session['username']
        return render_template('viewexpense.html',expdata = expdata, name = name)
    else:
        error = 'Invalid request. Please enter username and password!'
        return render_template('login.html',error = error)


#app logic to signout
@app.route('/signout')
def signout():
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
	db.create_all()
	app.run()
