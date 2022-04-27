from django.shortcuts import render
from flask import Flask, request, jsonify ,redirect, url_for,render_template
import boto3
from botocore.exceptions import ClientError
import os
import json

app = Flask(__name__)

#BASIC ROUTES
@app.route('/')
def index():
    return render_template("home.html")

@app.route('/ec2')
def ec2():
    return render_template("ec2.html")

@app.route('/s3')
def s3():
    return render_template("s3.html")

#EC2 ROUTES
#Return list of all ec2 instances
@app.route('/listec2')
def list_ec2():
    ec2 = boto3.resource('ec2',region_name='us-east-1',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
    instances = ec2.instances.all()
    ec2Instances = []
    
    for instance in instances:
        ec2Instance = {
        "id":instance.id , 
        "instance_type":instance.instance_type,
        "public_ip_address":instance.public_ip_address,
        "state":instance.state
        }

        ec2Instances.append(ec2Instance)
    return render_template('list.html', data=ec2Instances)

#creates ec2 instance
@app.route('/createec2',methods=['POST','GET'])
def createec2():
    if request.method=='GET':
        return render_template("ec2form.html")
    if request.method=='POST':
        ImageId = "ami-04505e74c0741db8d"
        MinCount = 1
        MaxCount = 1
        InstanceType = "t2.micro"        
        KeyName=request.form.get("keyName")

        ec2 = boto3.resource('ec2',region_name='us-east-1',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
        instance = ec2.create_instances(
        ImageId=ImageId,
        MinCount=MinCount,
        MaxCount=MaxCount,
        InstanceType=InstanceType
    )
    return redirect(url_for('list_ec2'))

#Terminates ec2 instance
@app.route('/terminateec2',methods=['POST'])
def terminateec2():
    if request.method=='POST':
        id=request.form.get("idToBeStopped")
        ec2 = boto3.resource('ec2',region_name='us-east-1',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
        instance = ec2.Instance(id)
        response = instance.terminate()
    return redirect(url_for('list_ec2'))        

# S3 ROUTES

#lists al S3 buckets
@app.route('/lists3')
def list_s3():
    s3 = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))

    buckets = s3.buckets.all()

    bucketlist = []
    for bucket in buckets:
        bucketlist.append(bucket.name)
    return render_template('lists3.html', data=bucketlist)


#creates s3 bucket
@app.route('/creates3',methods=['POST','GET'])
def create_s3():
    if request.method=='GET':
        return render_template("s3form.html")
    if request.method == 'POST':
        bucketName=request.form.get("bucketName")
        bucketRegion = request.form.get('bucketLocation')

        try:
            s3 = boto3.resource('s3',region_name=bucketRegion,aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
            s3.create_bucket(Bucket=bucketName)
        except ClientError as e:
            print(e)

    return redirect(url_for('list_s3'))

#deletes s3 bucket
@app.route('/deletes3',methods=['POST'])
def delete_s3():
    # if request.method=='GET':
    #     return render_template("s3delform.html")
    if request.method == 'POST':
        bucket_name=request.form.get("bucketToBeDeleted")
        # print(bucket_name)
        s3 = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=os.getenv("ACCESS_ID"),
            aws_secret_access_key= os.getenv("ACCESS_KEY"))

        s3_bucket = s3.Bucket(bucket_name)
        s3_bucket.delete()
        #print("{} has been deleted successfully !!!".format(bucket_name))
        return redirect(url_for('list_s3'))
    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)