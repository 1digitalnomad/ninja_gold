from mysqlconnection import connectToMySQL
import random

SCHEMA = 'ninja_gold'

def create_activity(user_id, location_id, gold):
    print('*' * 80)
    db = connectToMySQL(SCHEMA)
    query = 'INSERT INTO activities (user_id, location_id, gold_amount, created_at, updated_at) VALUES (%(user)s, %(location)s, %(gold_amount)s, NOW(), NOW());'
    data = {
        'user' : user_id,
        'location' :location_id,
        'gold_amount' : gold

    }

    db.query_db(query, data)

    # we are getting this from the @app.route('/process')in the server.py file.
    print(user_id, location_id) #since the location_id is coming from the form it is a string. it should be an int.
    #does all of the havey lifting
    #create an activity
    #users_id comes from session
    #location_id comes from the form
    #gold amount has to be created
    #get the location from the database
    #create a randome number between the locations min/max value
    #update the users gold

def calculate_gold(location_id):
    db = connectToMySQL(SCHEMA) #This connects us into the db. we defined SCHEMA globally uptop. we could also just add in the () 'ninja_gold.
    query = 'SELECT min_gold, max_gold FROM locations WHERE id = %(id)s'
    data = {
        'id' : location_id
    }
    location_list = db.query_db(query, data) #lets rund this query. it's like hitting the thunderbolt in mysqlworkbench. it will return a list just like in mysql workbench. it brings somethign back.
    location = location_list[0]
    gold = random.randint(int(location['min_gold']), int(location['max_gold']))
    print('*' * 80)
    print(location_list)
    return gold

def get_current_gold(user_id):
    db = connectToMySQL(SCHEMA)
    query = 'SELECT gold FROM users WHERE id = %(user)s;'
    data = {
        'user' : user_id
    }
    user_list = db.query_db(query,data)
    print(user_list)
    user = user_list[0]
    current_gold =  user['gold'] #we are sending user.gold an it's' value. 
    #alternative way of coding the same thing is return db.query_db(query,data)[0]['gold']

    return current_gold 

def update_user_gold(user_id, gold):
    db = connectToMySQL(SCHEMA)
    query = 'UPDATE users SET gold = %(gold_amount)s WHERE id = %(user)s;'
    data = {
        'gold_amount' : gold,
        'user' : user_id
    }
    db.query_db(query,data)




    #update user gold
    #write an update query
    #gold should be the old gold plus new gold
     #get user from db and get current gold




    #this function will be called from the process route in the server.py file

