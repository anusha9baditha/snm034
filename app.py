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
    try:
        if request.method=='POST':
            print(request.form)
            username=request.form.get('username')
            useremail=request.form.get('email') #sowmya@codegnan.com
            userpassword=request.form.get('password')
            mydb.ping(reconnect=True) #it reconnect mysql server autoimatically
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select account_status from userdata where useremail=%s',[useremail])
            db_response=cursor.fetchone() #('inactive',)
            print(db_response)
            server_otp=genotp()
            otp_expiry_time=datetime.now()+timedelta(minutes=5)
            if  db_response:
                if db_response[0]=='active':
                    return 'User already existed'
                cursor.execute('update userdata set otp=%s,otp_expiry_time=%s,account_status=%s where useremail=%s',[server_otp,otp_expiry_time,'inactive',useremail])
            else:
                cursor.execute('insert into userdata(username,useremail,userpassword,otp,otp_expiry_time,account_status) values(%s,%s,%s,%s,%s,%s)',[username,useremail,userpassword,server_otp,otp_expiry_time,'inactive'])
            mydb.commit()
            cursor.close()
            subject='User OTP Verification for SNM Application'
            body=f'Hello {username} use thye given otp {server_otp}'
            send_mail(subject=subject,body=body,to=useremail)
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
                return 'user not found in db'
            if user_otp_time > stored_userdata[1]:
                return 'OTP Expiried pls try again'
            if stored_userdata[2]=='active':
                return 'User already Existed pls login'
            if user_otp !=stored_userdata[0]:
                return 'INvalid otp pls check again'
            cursor.execute("update  userdata set otp=null,otp_expiry_time=null,account_status='active' where useremail=%s",[useremail])
            mydb.commit()
            cursor.close()
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