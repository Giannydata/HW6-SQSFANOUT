from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
    BundlingOptions
)
import aws_cdk as cdk
from constructs import Construct


class SqsFanoutStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        #Defining input and output S3 buckets
        # The input bucket is used to store the input files
        input_bucket = s3.Bucket(self, "InputBucket",versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # The output bucket is used to store the output files
        output_bucket = s3.Bucket(self, "OutputBucket",versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # Defining sns topic
        img_notif = sns.Topic(self, "S3ImageUploadNotification")
        # Defining sns queue
        img_lam_queue = sqs.Queue(self, "ImageToThumbnailQueue")
        
        
        # Creating links between Input bucket -> sns topic -> sns queue
        
        # This will send a notification to the sns topic when an image is uploaded to input bucket
        input_bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3n.SnsDestination(img_notif))
        
        # This will send a notification to the sns queue when a message is sent to the sns topic
        img_notif.add_subscription(subs.SqsSubscription(img_lam_queue))
        
        


        # Define Lambda function with local bundling
        
        #For the bundling options, I am using a Python 3.9 runtime (which came with the DevContainer)
        #as well as Pillow version 11.2.1
        thumbnail_lambda = _lambda.Function(self, "ThumbnailLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda", bundling=BundlingOptions(
                image=_lambda.Runtime.PYTHON_3_9.bundling_image, 
                command=[
                "bash", "-c",
                "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
            ],
            working_directory="/asset-input"
        )
                                         ),
    environment={
        # Instead of hardcoding the output bucket name, I am creating an environment variable to
        # allow the lambda function to access it when loaded into AWS Lambda instance
        "OUTPUT_BUCKET": output_bucket.bucket_name
    }
)

        
        # Granting permissions to the lambda function to read from input bucket and write to output bucket
        input_bucket.grant_read(thumbnail_lambda)
        output_bucket.grant_write(thumbnail_lambda)
        # Granting permissions to the lambda function to read from sns queue
        img_lam_queue.grant_consume_messages(thumbnail_lambda)
        # Adding the sns queue as an event source for the lambda function
        thumbnail_lambda.add_event_source(lambda_event_sources.SqsEventSource(img_lam_queue))
