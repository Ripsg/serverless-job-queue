import json
import os
import boto3
from datetime import datetime
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from models.job import Job, JobRequest

logger = Logger()
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

JOBS_TABLE = os.environ['JOBS_TABLE']
JOBS_QUEUE = os.environ['JOBS_QUEUE']

table = dynamodb.Table(JOBS_TABLE)

@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> dict:
    try:
        # Parse request body
        body = json.loads(event['body'])
        job_request = JobRequest(**body)
        
        # Create new job
        job = Job(
            job_type=job_request.job_type,
            payload=job_request.payload
        )
        
        # Save to DynamoDB
        table.put_item(Item=job.to_dynamo_dict())
        
        # Send to SQS
        sqs.send_message(
            QueueUrl=JOBS_QUEUE,
            MessageBody=json.dumps({
                'job_id': job.job_id,
                'job_type': job.job_type,
                'payload': job.payload
            })
        )
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'job_id': job.job_id,
                'status': job.status,
                'message': 'Job submitted successfully'
            })
        }
        
    except Exception as e:
        logger.exception('Error submitting job')
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 