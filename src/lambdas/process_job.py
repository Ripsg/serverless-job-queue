import json
import os
import boto3
from datetime import datetime
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from models.job import Job, JobStatus

logger = Logger()
dynamodb = boto3.resource('dynamodb')

JOBS_TABLE = os.environ['JOBS_TABLE']
table = dynamodb.Table(JOBS_TABLE)

def process_job_payload(job_type: str, payload: dict) -> dict:
    """
    Process the job payload based on job type.
    This is where you would implement different job processing logic.
    """
    # Example processing - you would replace this with actual processing logic
    if job_type == "image_resize":
        # Simulate image processing
        return {"processed": True, "dimensions": payload.get("dimensions", [800, 600])}
    elif job_type == "data_analysis":
        # Simulate data analysis
        return {"analyzed": True, "records_processed": len(payload.get("data", []))}
    else:
        return {"processed": True, "job_type": job_type}

@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> dict:
    try:
        # Process each message from SQS
        for record in event['Records']:
            message = json.loads(record['body'])
            job_id = message['job_id']
            
            # Get job from DynamoDB
            response = table.get_item(Key={'job_id': job_id})
            if 'Item' not in response:
                logger.error(f"Job {job_id} not found")
                continue
                
            job = Job.from_dynamo_dict(response['Item'])
            
            try:
                # Update status to processing
                job.status = JobStatus.PROCESSING
                job.updated_at = datetime.utcnow()
                table.put_item(Item=job.to_dynamo_dict())
                
                # Process the job
                result = process_job_payload(job.job_type, job.payload)
                
                # Update job with success
                job.status = JobStatus.COMPLETED
                job.result = result
                job.updated_at = datetime.utcnow()
                
            except Exception as e:
                logger.exception(f"Error processing job {job_id}")
                # Update job with error
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.updated_at = datetime.utcnow()
            
            # Save final job state
            table.put_item(Item=job.to_dynamo_dict())
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing completed'
            })
        }
        
    except Exception as e:
        logger.exception('Error in job processor')
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 