
import os
from flask import Flask, render_template, request, redirect, Response
import ipfsApi
import socket
import json

app = Flask("__name__")
app.secret_key = 'dropboxapp1234'
pid = 0
api = ipfsApi.Client('127.0.0.1', 5001)

@app.route('/PatientData', methods =['GET', 'POST'])
def PatientData():
    if request.method == 'POST':
        global pid
        global api
        pid = pid + 1
        name = str(request.form['t1']).strip()
        date = request.form['t2']
        address = request.form['t3']
        phone = request.form['t4']
        condition = request.form['t5']
        f = open(str(pid)+".txt", "w")
        f.write(str(pid)+","+name+","+date+","+address+","+phone+","+condition)
        f.close()
        new_file = api.add(str(pid)+".txt") #adding encrypted model to IPFS
        hashcode = new_file['Hash']
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(('localhost', 3333))
        hashdata = 'createrecord,'+str(pid)+","+hashcode
        message = client.send(hashdata.encode())
        data = client.recv(100)
        data = data.decode()
        print(data)
        os.remove(str(pid)+".txt")
        color = '<font size="" color="black">'
        output = color+" Record stored in IPFS and in Blockchain with ID : "+str(pid)+" <br/>Hashcode = "+hashcode
        return render_template("Patients.html",error=output)        
                

@app.route("/GetRecord", methods =['GET', 'POST'])
def GetRecord():
    if request.method == 'POST':
        name = str(request.form['t1']).strip()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(('localhost', 3333))
        hashdata = 'getrecord,'+name
        message = client.send(hashdata.encode())
        data = client.recv(1000)
        data = data.decode()
        data = data.strip()
        if '#' in data:
            data = data.split("#")
            print(data)
            data = data[len(data)-1]
        arr = data.split(",")
        print(arr)
        details = api.cat(arr[1])
        arr = details.split(",")

        color = '<font size="" color="black">'
        output = '<table border="1" align="center">'
        output+='<tr><th>Patient ID</th><th>Patient Name</th><th>Birth Date</th><th>Address</th><th>Phone</th><th>Disease Details</th></tr>'
        output+='<tr><td>'+color+arr[0]+'</td><td>'+color+arr[1]+'</td><td>'+color+arr[2]+'</td>'
        output+='<td>'+color+arr[3]+'</td><td>'+color+arr[4]+'</td>'
        output+='<td>'+color+arr[5]+'</td></tr>'
        output+='</table><br/><br/><br/><br/>'
        return render_template("ViewDetails.html",error=output)  

@app.route("/AccessRecords")        
def AccessRecords():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 3333))
    hashdata = 'getid'
    message = client.send(hashdata.encode())
    data = client.recv(1000)
    data = data.decode()
    data = data.strip()
    print(data)
    arr = data.split("#")
    output = '<tr><td><font size="" color="black">Patient&nbsp;ID</b></td><td><select name="t1">'
    for i in range(len(arr)):
        output+='<option value='+arr[i]+'>'+arr[i]+'</option>'
    output+='</select></td></tr>'
    return render_template("AccessRecord.html",error=output)   

@app.route("/Patients")
def Patients():
    return render_template("Patients.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/Login")
def Login():
    return render_template("Login.html")

@app.route('/UserLogin', methods =['GET', 'POST'])
def UserLogin():
    if request.method == 'POST':
        username = request.form['t1']
        password = request.form['t2']
        if username == 'admin' and password == 'admin':
            return render_template("AdminScreen.html",error='Welcome '+username)
        else:
            return render_template("Login.html",error='Invalid Login')
            

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999, debug=True)
