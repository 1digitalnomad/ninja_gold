from flask import Flask, render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
from helpers import create_activity
from helpers import calculate_gold
from helpers import get_current_gold
from helpers import update_user_gold
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
SCHEMA = 'ninja_gold' #here we are giving putting our database in mysql into a variable called SCHEMA. we are defining globally.


app = Flask(__name__)
app.secret_key = "thisisasecretkeyman"
bcrypt = Bcrypt(app)

@app.route('/')  #this is our index page route.
def index():
    if 'user_id' not in session:
        return redirect('/login_reg')

    db = connectToMySQL(SCHEMA)
    query = 'SELECT * FROM locations;'
    location_list = db.query_db(query)

    db = connectToMySQL(SCHEMA)
    query = 'SELECT gold_amount, locations.name AS location FROM activities JOIN locations ON activities.location_id = locations.id WHERE activities.user_id = %(user_id)s ORDER BY activities.created_at DESC;'
    data = {
        'user_id': session['user_id']
    }
    activities_list = db.query_db(query, data)

    db = connectToMySQL(SCHEMA)
    query = 'SELECT gold FROM users WHERE id = %(user_id)s;'
    data = {
        'user_id': session['user_id']
    }
    user_list = db.query_db(query,data)
    print(user_list)
    gold = user_list[0]['gold']
    # this is what is returned. It's in a list. It's in the zero index with the key label as 'gold' [{'gold': 0}]

    return render_template('index.html', locations = location_list, activities = activities_list, gold_total=gold)

#update the users gold with this route.
@app.route('/process', methods = ['post'])
def process():
    gold = calculate_gold(request.form['location']) #this will return something and it will be stored in the gold variable.
    create_activity(session['user_id'], request.form['location'], gold) #remember this is a function. sending arguments to the helpers file def create_activity.
    user_gold = get_current_gold(session['user_id'])
    updated_gold = user_gold + gold
    update_user_gold(session['user_id'], updated_gold)
    print('*' *80)
    print(user_gold)
    return redirect('/')
    #create an activity
        #users_id comes from session
        #location_id comes from the form
        #gold amount has to be created
            #get the location from the database
            #create a randome number between the locations min/max value
    #update the users gold
    #create a helpers.py file. It's like a link css or link js. Makes your code less cluttered. 
    #you can import the process from the helpers.py file. make sure to import it above.




@app.route('/login_reg') #this page has our html registration and login forms.
def login_reg():
    return render_template('/login_reg.html')

@app.route('/user/create', methods=['POST']) #the registration action link will go to this route to create a new user.
def create_user():
    print(request.form)
    errors = False  #for now we are saying, no errors yet. lets see what happens in the validations. we are assuming no errors at this line.

    if len(request.form['username']) <3: #if the username is less than 3 characters flash the following message.
        flash('Username must be longer than 3 characters.')

    else: #or else if it is longer than 3 character we can run the following code to verify if the username is not already in the db.
        db = connectToMySQL(SCHEMA)  # remember SCHEMA = 'ninja_gold' which is the name of the mysql db we created the tables in. db is the var. we are now
        #in the database. we are connected so lets run the searches and compare it to our database.
        query = 'SELECT username FROM users WHERE username = %(username)s;' #this is the sql command to find the username in the users table.
        data = {
            'username' : request.form['username']
        } #data is the dictionary we got back from the form the user just submitted to us.
        matching_users = db.query_db(query,data) #matching_users is our varible for the db connection. db.query_db() is a function and we are 
        #passing the arguments of query and data from line 34 and 35. 
        if len(matching_users)> 0: #if matching_users comes back as 1 found. Then we flash the following messages. this error is true.
            flash('Username is already in use. Try again.')
            errors = True

    if not EMAIL_REGEX.match(request.form['email']): #we are validating if the email was intered and passes the regex checks.
        flash('Email must be valid')
        errors = True
    else:
        db = connectToMySQL(SCHEMA) #ok let's log into the db again.
        query = 'SELECT id FROM users WHERE email = %(email)s;'  #let's use this sql command to find the email in the db in the users table.
        data = {
            'email' : request.form['email']
        }
        matching_users = db.query_db(query,data) #ok we are in the db, let's run the QUERY, and try to match it with the DATA.
        if len(matching_users) > 0: #did you find something? then this error is tru and the message will flash.
            flash('Email already in use')
            errors = True



    if len(request.form['password']) < 8: #let's make sure the password is up to our specs.
        flash('Password must be longer than 8 characters')
        errors = True
    if request.form['password'] != request.form['confirm_password']: #let's make sure the passwords match.
        flash('Passwords mush match. Try again.')
        errors=True

        if errors == True:  #if all the erros above are true. redirect them to /login_reg, there the flash messages code will flash the errors.
            return redirect('/login_reg')

    else: #now if we find NO errors above after we validate. Now we can submit the users form data in the msql database and create an account for them.
        db = connectToMySQL(SCHEMA) #lets connect to the database
        query = 'INSERT INTO users(username, email, pw_hash, gold, created_at, updated_at) VALUES(%(username)s, %(email)s, %(pw_hash)s, 0, NOW(), NOW())'
        #use this SQL command to submit the users registration information into the proper table and columns. Use the data dictionary below to fill in the blanks.

        data = {
            'username' : request.form['username'], #requst.form is what the user submited. we can grab any data and put it here.
            'email' : request.form['email'],
            'pw_hash' : bcrypt.generate_password_hash(request.form['password'])
        }
        user_id = db.query_db(query, data) #we are going to put db.query_db(query, data) into a variable called user_id because we will want to register them and log them in at the same time.
        session['user_id'] = user_id #user_id is everything in the database we just created using the QUERY and DATA for this user and now their information is in session/browser. This user is now registerd and logged in.
        print(user_id)
        return redirect('/')

# this is 1 way of logging a user in. I uses a negative method.
# @app.route('/login', methods=['POST'])
# def login():
#     db = connectToMySQL(SCHEMA)
#     query =  'SELECT id, email, pw_hash FROM users WHERE email = %(email)s'
#     data = {
#         'email' : request.form['email']
#     }
#     matching_users = db.query_db(query,data)
#     if not matching_users:
#         flash('Email does not seem correct. Try again.')
#         return redirect('/login_reg')

#     user= matching_users[0]
#     if not bcrypt.check_password_hash(user['pw_hash'], request.form['password']):
#         flash('email or password not correct.')
#         return redirect('/login_reg')

#     session['user_id'] =  user['id']
#     return redirect('/')

#this is the 2nd way of logging someone in.
@app.route('/login', methods=['post'])
def login():
    db = connectToMySQL(SCHEMA) #lets access the db and see if we can match what the user just entered.
    query = 'SELECT * FROM users WHERE email = %(email)s' #we are using this SQL command to find the email in the users table.
    data = {
        'email' : request.form['email']
    } #lets use this email from the form the user just submitted to see if we can find this email or not.

    matching_users = db.query_db(query, data) #this is returning what we just entered above. we will use match_users as the variable to we don't have to keep typing db.query_db(query,data) over and over again.
    if matching_users: #match_users will bring back a list. it will either be empty which means False [] or True [email]
        if bcrypt.check_password_hash(matching_users[0]['pw_hash'], request.form['password']): #remember bcrypt.check_password_hash() is a function. we are passing two arguments the pw_hash and the password the user just entered. if true then we move on to the next line of code.
            session['user_id'] = matching_users[0]['id']
            return redirect('/')
    flash('You could not be logged in') #if bcrypt.check_password_hash(matching_users[0]['pw_hash'], request.form['password']) comes back false. we flash.
    return redirect('/login_reg')






@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
