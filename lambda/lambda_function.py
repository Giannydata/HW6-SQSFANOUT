import boto3, os, sys, uuid, json
from PIL import Image

s3_client = boto3.client('s3')

#My modifications to access Output bucket name
# Note: In full disclosure, I used a combination of ChatGPT and AWS documentation to 
# implement this part of the code
OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']

def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        image.thumbnail((128,128))
        image.save(resized_path)

def lambda_handler(event, context):
    for record in event['Records']:
        
        # If the event is fan-out from SQS, use line 19-26
        # Parse the SQS message body
        message_body = json.loads(record['body'])
        # Parse the s3 event wrapped in SNS message body
        s3_events = json.loads(message_body['Message'])['Records']
        # Extract the S3 bucket name from the message body
        for s3_event in s3_events:
                bucket = s3_event['s3']['bucket']['name']
                key = s3_event['s3']['object']['key']

        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        upload_path = '/tmp/resized-{}'.format(key)

        s3_client.download_file(bucket, key, download_path)
        resize_image(download_path, upload_path)
        s3_client.upload_file(upload_path, OUTPUT_BUCKET, 'resized-{}'.format(key))