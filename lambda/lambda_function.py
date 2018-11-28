import json
import datetime
import random
import boto3
import csv
import io

kinesis = boto3.client('kinesis', region_name='us-west-2') #<--- change region if not in us-west-2

def lambda_handler(event, context):

    bigdataStreamName = "gc_bigdata_stream"
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket="prc-reinvent-2018", Key="data/partial-load/ratings-partial-load.csv")
    tsv =  str(response['Body'].read().decode('UTF-8'))
    lines = tsv.split("\n")
    for line in tsv.split("\n"):
        val = line.split(",")
        data = json.dumps(getRating(val[0], val[1], val[2], val[3]))
        kinesis.put_record(StreamName=bigdataStreamName, Data=data, PartitionKey="rating")
    return "complete"

def getRating(userId, itemId, ratingId, timestamp):
    data = {}
    data['userid'] = userId
    data['movieid'] = itemId
    data['ratingid'] = ratingId
    data['timestamp'] = timestamp
    return data
