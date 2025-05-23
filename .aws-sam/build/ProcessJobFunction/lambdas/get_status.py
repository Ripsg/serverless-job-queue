import json
import os
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from models.job import Job

logger = Logger()
dynamodb = boto3.resource('dynamodb')

JOBS_TABLE = os.environ['JOBS_TABLE']
table = dynamodb.Table(JOBS_TABLE)

@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> dict:
    try:
        # Get job_id from path parameters
        job_id = event['pathParameters']['job_id']
        
        # Get job from DynamoDB
        response = table.get_item(Key={'job_id': job_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': f'Job {job_id} not found'
                })
            }
        
        # Convert DynamoDB item to Job model
        job = Job.from_dynamo_dict(response['Item'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'job_id': job.job_id,
                'status': job.status,
                'job_type': job.job_type,
                'created_at': job.created_at.isoformat(),
                'updated_at': job.updated_at.isoformat() if job.updated_at else None,
                'result': job.result,
                'error': job.error
            })
        }
        
    except Exception as e:
        logger.exception('Error getting job status')
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 