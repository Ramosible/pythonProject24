from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import  SQLAlchemy
from flask_bcrypt import Bcrypt, generate_password_hash


#http://fw0rld.pythonanywhere.com/home

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MYKEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    First_Name = db.Column(db.String(30), nullable=False)
    Last_Name = db.Column(db.String(40), nullable=False)
    Email = db.Column(db.String(40), nullable=False,primary_key= True)
    Password = db.Column(db.String(40), nullable=False)

    def __str__(self):
        return f'User First Name:{self.First_Name}; Last Name: {self.Last_Name}; Email: {self.Email}'

class Rm_shop(db.Model):
    Name = db.Column(db.String(30),primary_key= True)
    Information = db.Column(db.String(40), nullable=False)
    Special_Price = db.Column(db.INTEGER, nullable=False)
    Save = db.Column(db.String(40))

    def __str__(self):
        return f'Name: {self.Name}, Special Price: {self.Special_Price} '



db.create_all()


@app.route('/', methods= ['GET','POST'])
@app.route('/home', methods= ['GET','POST'])
def home():

    return render_template('home.html', user = user, title='Home')



@app.route('/about')
def about():
    return redirect(url_for('home'))



@app.route('/<user>')
def user(user):
#If the user is logged in the account:
    if 'user' in session and User.query.filter_by(Email=session['user']).first():
        user = User.query.filter_by(Email=session['user']).first().First_Name

        return render_template('user.html', user= user, title=user)

#If  user is not logged in  the account
    return redirect(url_for('home',title='Home'))




@app.route('/login', methods= ['GET','POST'])
def login():
# If the user is logged in the account:

    if 'user' not in session:
        try:
            if request.method == 'POST' and User.query.filter_by(Email=request.form['email']).first().Email == request.form[
                'email']:
                hashed = User.query.filter_by(Email=request.form['email']).first().Password
                email = User.query.filter_by(Email=request.form['email']).first().Email
                passw_ = request.form['password']
                print(bcrypt.check_password_hash(hashed, passw_))
                # if  hashed password = password entered by the user (that is, if the password is correct)
                if bcrypt.check_password_hash(hashed, passw_):
                    userr = request.form['email']
                    session['user'] = userr
                    return redirect(url_for('user', user=userr))
                # if password is incorrect:
                if not bcrypt.check_password_hash(hashed, passw_):
                    flash('Password is incorrect!', 'not')

        # if user is not registered:
        except AttributeError:
            flash('You are not registered', 'not')

        return render_template('login.html',title='Login')
    return redirect(url_for('home',title='Home'))




@app.route('/logout')
def logout():
    #this is log out route
    session.pop('user',None)
    flash('You Are Log Out', 'succ')
    return redirect(url_for('home'))



@app.route('/registration', methods= ['GET','POST'])
def registration():
    try:
        #if user is already registered
        if request.method == 'POST' and User.query.filter_by(Email=request.form['email']).first().Email == request.form['email']:
            flash ('You are already registered', 'not')
     #if user is not registered, then here he/she can create account
    except AttributeError:
        global pas

        if request.method == 'POST':
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            email = request.form['email']
            psw = request.form['psw']
            hashed_psw = bcrypt.generate_password_hash(psw).decode('utf-8')
            pas = hashed_psw
            user = User(First_Name=firstname, Last_Name=lastname, Email= email,Password=hashed_psw )
            db.session.add(user)
            db.session.commit()

            userr = request.form['email']
            session['user'] = userr
            return redirect(url_for('user',user = userr))

    return render_template('registration.html', title='Register')





@app.route("/livescore")
def livescore():
    #if user is logged in the account, he or she can see livescore results.
    if 'user' in session:

        return render_template('livescore.html',title='LIVESCORE')


    #if not, he/she  will receive this message and return to the home page
    flash('Please, Log in to your account !', 'not')
    return redirect(url_for('home'))



@app.route('/laliga',methods= ['GET','POST'])
def laliga():

    if 'user' in session:
        if request.method=='POST':
            season = request.form['season']
            return render_template('laliga.html',season=season, title='La Liga')

        return render_template('laliga.html',title='La Liga')




@app.route('/ucl',methods= ['GET','POST'])
def ucl():
    if 'user' in session:
        if request.method=='POST':
            season = request.form['season']
            return render_template('ucl.html',season=season,title='UCL')

        return render_template('ucl.html',title='UCL')




@app.route('/premierleague',methods= ['GET','POST'])
def premierleague():
    if 'user' in session:
        if request.method=='POST':
            season = request.form['season']
            return render_template('premierleague.html',season=season,title='Premier League')

        return render_template('premierleague.html',title='Premier League')



@app.route('/rmshop', defaults={"page": 1})
@app.route('/rmshop/<int:page>')
def rmshop(page):
#this is parsed html (from https://www.uksoccershop.com/football-shirts/spanish-la-liga/real-madrid?page=1)
#this information is saved in the database (named user.sqlite), in the rm_shop table
    queri = Rm_shop.query.all()
    per_page = 30

    rm_shopp = Rm_shop.query.paginate(page,per_page,error_out=False)

    if 'user' in session:
        page = page

        return render_template('rmshop.html',queri=queri,rm_shopp=rm_shopp,title='RMshop')

    return redirect(url_for('home',title='Home'))






@app.route('/change-password', methods= ['GET','POST'])
def change_password():

    if 'user' in session:
        if request.method == 'POST':
            user_email =session['user']
            email = User.query.filter_by(Email=user_email).first().Email
            #if the user entered that email by which he is logged
            if request.form['email'] == email:
                new_password = request.form['new_password']
                User.query.filter_by(Email=user_email).first().Password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                db.session.commit()
                flash('Password updated!', 'done')

            #if email is incorrect :
            elif request.form['email'] != email:
                flash('Email is incorrect', 'err')

        return render_template('change_password.html',title='Change password')

    return redirect(url_for('home',title='Home'))





if __name__ == '__main__':
    app.run(debug=True)
