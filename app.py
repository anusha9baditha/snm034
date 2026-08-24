from flask import Flask,request,redirect,url_for,render_template
from otp import genotp
from cmail import send_mail
from mysql.connector import (connection)
mydb=connection.MySQLConnection(user='root',host='localhost',password='admin@123',db='snm034db')
from datetime import datetime,timedelta
app=Flask(__name__)
@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        print(request.form)
        username=request.form.get('username')
        useremail=request.form.get('email')
        userpassword=request.form.get('password')
        mydb.ping(reconnect=True) #it reconnect mysql server autoimatically
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select account_status from userdata where useremail=%s',[useremail])
        db_response=cursor.fetchone()
        print(db_response)
        if  db_response:
            if db_response[0]=='active':
                return 'User already existed'
        server_otp=genotp()
        otp_expiry_time=datetime.now()+timedelta(minutes=5)
        cursor.execute('insert into userdata(username,useremail,userpassword,otp,otp_expiry_time,account_status) values(%s,%s,%s,%s,%s,%s)',[username,useremail,userpassword,server_otp,otp_expiry_time,'inactive'])
        mydb.commit()
        cursor.close()
        subject='User OTP Verification for SNM Application'
        body=f'Hello {username} use thye given otp {server_otp}'
        send_mail(subject=subject,body=body,to=useremail)
        return redirect(url_for('otp_verify'))
    return render_template('register.html')
@app.route('/otp_verify',methods=['GET','POST'])
def otp_verify():
    if request.method=='POST':
        print(request.form)
        #accept user otp
        #verify otp stored otp in db
        return redirect(url_for('login'))
    return render_template('otp.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        #accept login details
        #verify with db details
        #create session 
        return redirect(url_for('dashboard'))
    return render_template('login.html')
@app.route('/dashboard',methods=['GET'])
def dashboard():
    return render_template('dashboard.html')
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    return render_template('addnotes.html')
@app.route('/viewallnotes',methods=['GET','POST'])
def viewallnotes():
    return render_template('viewallnotes.html')
if __name__=='__main__':
    app.run(debug=True,use_reloader=True)