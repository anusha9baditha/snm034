from flask import Flask,request,redirect,url_for,render_template,session,flash
from flask_session import Session #stores secure server side session 
from otp import genotp
from cmail import send_mail
from mysql.connector import (connection)
mydb=connection.MySQLConnection(user='root',host='localhost',password='admin@123',db='snm034db')
from datetime import datetime,timedelta
app=Flask(__name__)
app.secret_key='Codegnan123'
app.config['SESSION_TYPE']='filesystem'
Session(app) #it intialize the session data
@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/register',methods=['GET','POST'])
def register():
    try:
        if request.method=='POST':
            print(request.form)
            username=request.form.get('username')
            useremail=request.form.get('email') #sowmya@codegnan.com
            userpassword=request.form.get('password')
            mydb.ping(reconnect=True) #it reconnect mysql server autoimatically
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select account_status from userdata where useremail=%s',[useremail])
            db_response=cursor.fetchone() #('active',) or None
            print(db_response)
            server_otp=genotp() #'M7hS4f'
            otp_expiry_time=datetime.now()+timedelta(minutes=5)
            if  db_response:
                if db_response[0]=='active':
                    flash('User already existed')
                    return redirect(url_for('register'))
                cursor.execute('update userdata set otp=%s,otp_expiry_time=%s,account_status=%s where useremail=%s',[server_otp,otp_expiry_time,'inactive',useremail])
            else:
                cursor.execute('insert into userdata(username,useremail,userpassword,otp,otp_expiry_time,account_status) values(%s,%s,%s,%s,%s,%s)',[username,useremail,userpassword,server_otp,otp_expiry_time,'inactive'])
            mydb.commit()
            cursor.close()
            subject='User OTP Verification for SNM Application'
            body=f'Hello {username} use thye given otp {server_otp}'
            send_mail(subject=subject,body=body,to=useremail)
            flash('OTP has been sent to given email')
            return redirect(url_for('otp_verify',useremail=useremail))
        return render_template('register.html')
    except Exception as e:
        print(e)
        return redirect(url_for('register'))
@app.route('/otp_verify/<useremail>',methods=['GET','POST'])
def otp_verify(useremail):
    try:     
        if request.method=='POST':
            print(request.form)
            #accept user otp
            user_otp=request.form['otp']
            user_otp_time=datetime.now()
            #verify otp stored otp in db
            mydb.ping(reconnect=True)
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select otp,otp_expiry_time,account_status from userdata where useremail=%s',[useremail])
            stored_userdata=cursor.fetchone()
            print(stored_userdata)
            if not stored_userdata:
                flash('user not found in db')
                return redirect(url_for('otp_verify',useremail=useremail))
            if user_otp_time > stored_userdata[1]:
                flash('OTP Expiried pls try again')
                return redirect(url_for('otp_verify',useremail=useremail))
            if stored_userdata[2]=='active':
                flash('User already Existed pls login')
                return redirect(url_for('otp_verify',useremail=useremail))
            if user_otp !=stored_userdata[0]:
                flash('INvalid otp pls check again')
                return redirect(url_for('otp_verify',useremail=useremail))
            cursor.execute("update  userdata set otp=null,otp_expiry_time=null,account_status='active' where useremail=%s",[useremail])
            mydb.commit()
            cursor.close()
            flash('OTp verified successfuly')
            return redirect(url_for('login'))
        return render_template('otp.html')
    except Exception as e:
        mydb.rollback()
        print('Error in otp verify ',e)
        return redirect(url_for('otp_verify',useremail=useremail))
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        #accept login details
        login_useremail=request.form.get('useremail') 
        login_password=request.form.get('password')
        mydb.ping(reconnect=True)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select account_status,userpassword from userdata where useremail=%s',[login_useremail])
        user_data=cursor.fetchone()
        print(user_data)
        if not user_data:
            flash('Email Not found pls try again')
            return redirect(url_for('login'))
        if user_data[0]=='active':
            if user_data[1]==login_password:
                #create session data to remember the user,user prefernces 
                #like a dictionary add a key 
                print(session,'before')
                session['user']=login_useremail
                print(session,'after')
                flash('Login successfull')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password')
                return redirect(url_for('login'))
        else:
            flash('User Not verified pls register again')
            return redirect(url_for('login'))
    return render_template('login.html')
@app.route('/dashboard',methods=['GET'])
def dashboard():
    if not session.get('user'):
        flash('To access dashboard pls login first')
        return redirect(url_for('login'))
    return render_template('dashboard.html')
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    try:
        if not session.get('user'):
            flash('To access addnotes pls login first')
            return redirect(url_for('login'))
        if request.method=='POST':
            print(request.form)
            Notestitle=request.form.get('title') #python
            Notescontent=request.form.get('content')
            if not Notestitle:
                flash('Title is required')
                return redirect(url_for('addnotes'))
            mydb.ping(reconnect=True)
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select userid from userdata where useremail=%s',[session.get('user')])
            userid=cursor.fetchone() #(1,) or None
            if not userid:
                flash('User not found plscheck')
            cursor.execute('insert into notesdata(notestitle,notescontent,added_by) values(%s,%s,%s)',[Notestitle,Notescontent,userid[0]])
            mydb.commit()
            cursor.close()
            flash(f'Notes added successfully {Notestitle}')
            return redirect(url_for('addnotes'))
        return render_template('addnotes.html')
    except Exception as e:
        print('Error in added notes',e)
        flash('Could add notes ')
        return redirect(url_for('addnotes'))
@app.route('/viewallnotes',methods=['GET','POST'])
def viewallnotes():
    return render_template('viewallnotes.html')
@app.route('/userlogout',methods=['GET'])
def userlogout():
    if not session.get('user'):
        flash('To logout pls login first')
        return redirect(url_for('login'))
    session.pop('user') #deletes nuser session data
    return redirect(url_for('index'))



if __name__=='__main__':
    app.run(debug=True,use_reloader=True)