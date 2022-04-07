# Importing modules required these project
from flask import Flask, render_template, redirect, session, url_for, g, request, flash
from flask_sqlalchemy import SQLAlchemy
from threading import Thread

import smtplib
from email.message import EmailMessage
from datetime import datetime as dt
import datetime

import time

import os

# creating app as a reference
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://learnejo_x:learnejo_x@s483.bom7.mysecurecloudhost.com/ec"
#congiguring database i.e connecting databse
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://oocbinqhrvchbv:8883cf8c8eebeea06004d6d245775a0e2af6ea47e8658af364ef804676a2970c@ec2-52-21-136-176.compute-1.amazonaws.com:5432/dfch5qs8n1rrjs"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = os.urandom(24)


# creating Ec table in the database
class EC(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Student_Name = db.Column(db.String(200), nullable=False)
    Email_Id = db.Column(db.String(500), nullable=False)
    Contact_No = db.Column(db.String(20), nullable=False)
    Stream_Allocated = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"{self.Sno} - {self.Student_Name}"


# creating Templates table into database
class Templates(db.Model):
    Tem_Id = db.Column(db.Integer, primary_key=True)
    Sub = db.Column(db.String(1000), nullable=False)
    Body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"{self.Tem_Id} - {self.Sub}"


# Admin login page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        session.pop('user', None)

        if request.form["password"] == 'password':
            session['user'] = request.form["username"]

            return redirect(url_for('home'))

    return render_template('index.html')


# Home page i.e Admin Dashboard
@app.route('/home')
def home():
    if g.user:
        return render_template('home.html', user=session['user'])

    return redirect(url_for('index'))


# fetching the data of all the registered students and rendering it into registered students.html page
@app.route('/registeredstudents', methods=['GET', 'POST'])
def registeredstudents():
    #if g.user:
    allec = EC.query.all()
    return render_template('registeredstudents.html')
    #return redirect(url_for('index'))


# selecting mails templates
@app.route('/sendemails/<string:name>/<string:mail>/<string:templateid>', methods=['GET', 'POST'])
def sendemails(name, mail, templateid):
    allmails = Templates.query.all()
    selected_temp = Templates.query.filter_by(Tem_Id=templateid).first()

    return render_template('sendmail.html', name=name, mail=mail, allmails=allmails, selected_temp=selected_temp)


# sending bulks mail logic
@app.route('/sendbuklemails/<string:templateid>', methods=['GET', 'POST'])
def sendbulkemails(templateid):
    allmails = Templates.query.all()
    selected_temp = Templates.query.filter_by(Tem_Id=templateid).first()

    return render_template('sendbulkmail.html', allmails=allmails, selected_temp=selected_temp)


# Seding Individual Mails
@app.route('/hitmail', methods=['GET', 'POST'])
def hitmail():
    if g.user:
        class Hitmail(Thread):
            if request.method == "POST":
                def remmail(self):
                    name = request.form["name"]
                    self.tomail = request.form['tomail']
                    self.subject = request.form['subject']
                    self.emailbody = request.form['editor1']
                    remtime = request.form['rimtime']
                    if (remtime):
                        rtime = remtime.replace("T", "-")
                        self.y, self.m, self.d, h_all = str(rtime).split('-')
                        self.h, self.min = h_all.split(':')
                        self.s = 00
                    else:
                        self.m, self.d, self.y, h_all = str(time.strftime('%m %d %Y %H:%M:%S')).split(' ')
                        self.h, self.min, self.s = h_all.split(':')
                        self.min = int(self.min) + 1
                        self.s = 00

                    if request.form.get('onsave'):
                        template = request.form['templatename']
                        alltemp = Templates(Sub=template, Body=self.emailbody)
                        db.session.add(alltemp)
                        db.session.commit()

                def run(self):
                    msg = EmailMessage()
                    msg['Subject'] = str(self.subject)
                    msg['From'] = 'Suraj'
                    msg['To'] = str(self.tomail)
                    msg.set_content(f"{self.emailbody}", subtype='html')

                    # server
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login('demo72897@gmail.com', "Demo@123")
                    send_time = datetime.datetime(int(self.y), int(self.m), int(self.d), int(self.h), int(self.min),
                                                  int(self.s))
                    time.sleep(send_time.timestamp() - time.time())
                    server.send_message(msg)
                    server.quit()

        remainder_mail = Hitmail()
        remainder_mail.remmail()
        remainder_mail.start()
    return redirect(url_for('registeredstudents'))


# Sending Bulk mail by using the for loop at line 179-180
@app.route('/hitbulkmail', methods=['GET', 'POST'])
def hitbulkmail():
    if g.user:
        class Bulk(Thread):
            if request.method == "POST":
                def bulk_mail(self):
                    self.subject = request.form['subject']
                    self.emailbody = request.form['editor1']
                    remtime = request.form['rimtime']
                    if (remtime):
                        rtime = remtime.replace("T", "-")
                        self.y, self.m, self.d, h_all = str(rtime).split('-')
                        self.h, self.min = h_all.split(':')
                        self.s = 00
                    else:
                        self.m, self.d, self.y, h_all = str(time.strftime('%m %d %Y %H:%M:%S')).split(' ')
                        self.h, self.min, self.s = h_all.split(':')
                        self.min = int(self.min) + 1
                        self.s = 00

                    if request.form.get('onsave'):
                        template = request.form['templatename']
                        alltemp = Templates(Sub=template, Body=self.emailbody)
                        db.session.add(alltemp)
                        db.session.commit()

                    self.allec = EC.query.all()
                    self.mailx = []
                    for ec in self.allec:
                        self.mailx.append(ec.Email_Id)

                def run(self):
                    msg = EmailMessage()
                    msg['Subject'] = str(self.subject)
                    msg['From'] = 'Suraj'
                    msg['To'] = self.mailx
                    msg.set_content(f"{self.emailbody}", subtype='html')

                    # server
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login('demo72897@gmail.com', "Demo@123")
                    send_time = datetime.datetime(int(self.y), int(self.m), int(self.d), int(self.h), int(self.min),
                                                  int(self.s))
                    time.sleep(send_time.timestamp() - time.time())
                    server.send_message(msg)
                    server.quit()

        obj_bulk = Bulk()
        obj_bulk.bulk_mail()
        obj_bulk.start()
    return redirect(url_for('registeredstudents'))


# setting remainder to send the mail
@app.route('/remainder', methods=['GET', 'POST'])
def remainder():
    if g.user:
        class Remainder(Thread):
            if request.method == "POST":
                def rem(self):
                    self.msg = EmailMessage()
                    self.msg['Subject'] = 'Remainders'
                    self.msg['From'] = 'Suraj'
                    self.msg['To'] = 'demo72897@gmail.com'
                    self.msg.set_content("Test")

                    self.year = request.form["year"]
                    self.month = request.form["month"]
                    self.date = request.form["date"]
                    self.time_t = request.form["time"]
                    self.minute = request.form["minute"]
                    self.second = request.form["second"]

                    # type-casting
                    self.year = int(self.year)
                    self.month = int(self.month)
                    self.date = int(self.date)
                    self.time_t = int(self.time_t)
                    self.minute = int(self.minute)
                    self.second = int(self.second)

                def run(self):
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login('demo72897@gmail.com', "Demo@123")
                    send_time = datetime.datetime(self.year, self.month, self.date, self.time_t, self.minute,
                                                  self.second)
                    print(send_time)
                    time.sleep(send_time.timestamp() - time.time())
                    server.send_message(self.msg)
                    server.quit()
                    print("Succesful")

        t1 = Remainder()
        t1.rem()
        t1.start()

    return redirect(url_for('registeredstudents'))


# @app.route('/templates')
# def templates():
#     return render_template('templates.html')


# it will run before any request is made to the server
@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']


# the sesssion will drop here
@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
