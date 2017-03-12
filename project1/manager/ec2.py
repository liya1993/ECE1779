from flask import render_template, redirect, url_for, request, g
import boto3
import config
from datetime import datetime, timedelta
from operator import itemgetter
from manager import admin
import mysql.connector
from config import db_config
from app.forms import connect_to_database, get_db

ec2 = boto3.setup_default_session(region_name='us-east-1')

@admin.route('/ec2',methods=['GET'])
# Display an HTML list of all ec2 instances
def ec2_list():

    # create connection to ec2
    ec2 = boto3.resource('ec2')

#    instances = ec2.instances.filter(
#        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    instances = ec2.instances.all()

    return render_template("ec2/list.html",title="EC2 Instances",instances=instances)


@admin.route('/ec2/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    ##    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System


    namespace = 'AWS/EC2'
    statistic = 'Average'                   # could be Sum,Maximum,Minimum,SampleCount,Average



    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
    #print (cpu)
    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))
    #print(cpu_stats)

    statistic = 'Sum'  # could be Sum,Maximum,Minimum,SampleCount,Average

    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_in_stats.append([time,point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))



    network_out = client.get_metric_statistics(
        Period=5 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkOut',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )


    net_out_stats = []

    for point in network_out['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_out_stats.append([time,point['Sum']])

        net_out_stats = sorted(net_out_stats, key=itemgetter(0))


    return render_template("ec2/view.html",title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           net_out_stats=net_out_stats)


@admin.route('/ec2/create',methods=['POST'])
# Start a new EC2 instance
def ec2_create():

    ec2 = boto3.resource('ec2')

    ec2.create_instances(ImageId=config.ami_id, MinCount=1, MaxCount=1, InstanceType='t2.small')

    return redirect(url_for('ec2_list'))



@admin.route('/ec2/delete/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_destroy(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).terminate()

    return redirect(url_for('ec2_list'))

@admin.route('/ec2/terminate',methods=['POST'])
#An option for deleting all data. Executing this function should delete application data stored on the database as well as all images stored on S3.
def project_terminate():
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''TRUNCATE TABLE users
            '''
    cursor.execute(query)
    query = '''TRUNCATE TABLE images
                '''
    cursor.execute(query)
    cnx.commit()
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

    s3 = boto3.resource('s3')
    objects_to_delete = s3.meta.client.list_objects(Bucket="ece1779project")
    delete_keys = {'Objects': []}
    delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
    s3.meta.client.delete_objects(Bucket="ece1779project", Delete=delete_keys)

    return redirect(url_for('ec2_list'))

# @admin.route('/ec2/config',methods=['GET','POST'])
# def project_config():

# An option for configuring the auto-scaling policy by setting the following parameters:
# CPU threshold for growing the worker pool
# CPU threshold for shrinking the worker pool
# Ratio by which to expand the worker pool (e.g., a ratio of 2 doubles the number of workers).
# Ratio by which to shrink the worker pool (e.g., a ratio of 4 shuts down 75% of the current workers).