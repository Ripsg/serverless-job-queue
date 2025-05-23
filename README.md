# Serverless Job Queue System

A serverless job queue system built with AWS Lambda, SQS, and DynamoDB. This system allows you to submit jobs via an HTTP API and process them asynchronously.

## Architecture

```
  Client
    ↓
  API Gateway
    ↓
[POST /submit-job] ──▶ Lambda (submit_job) ──▶ DynamoDB (store metadata)
                                                  ↓
                                               SQS Queue
                                                  ↓
                                         Lambda (process_job)
                                                  ↓
                                          DynamoDB (store result)
    ↑                                            ↓
  [GET /job/{id}] ◀── Lambda (get_status) ◀───────┘
```

## Features

- Submit jobs via HTTP API
- Asynchronous job processing
- Job status tracking
- Scalable and serverless architecture
- Built-in error handling and retries
- CloudWatch logging and monitoring

## Prerequisites

1. AWS Account
2. AWS CLI installed and configured
3. Python 3.9 or higher
4. AWS SAM CLI installed

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd serverless-job-queue
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Deploy to AWS:
```bash
sam build
sam deploy --guided
```

During the guided deployment, you'll be asked to provide:
- Stack name
- AWS Region
- Confirmation of IAM role creation

## API Usage

### Submit a Job

```bash
curl -X POST https://your-api-endpoint/prod/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "image_resize",
    "payload": {
      "dimensions": [800, 600]
    }
  }'
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "PENDING",
  "message": "Job submitted successfully"
}
```

### Check Job Status

```bash
curl https://your-api-endpoint/prod/jobs/123e4567-e89b-12d3-a456-426614174000
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "COMPLETED",
  "job_type": "image_resize",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:01:00Z",
  "result": {
    "processed": true,
    "dimensions": [800, 600]
  },
  "error": null
}
```

## Supported Job Types

Currently supported job types:

1. `image_resize`
   - Payload: `{"dimensions": [width, height]}`
   
2. `data_analysis`
   - Payload: `{"data": [...array of data points...]}`

## Monitoring and Logging

- CloudWatch Logs are automatically created for each Lambda function
- CloudWatch Metrics track:
  - Number of jobs processed
  - Processing time
  - Error rates
  - Queue length

## Development

To run the functions locally:

```bash
# Start local API
sam local start-api

# Invoke specific function
sam local invoke SubmitJobFunction --event events/submit-job.json
```

## Testing

Run the tests:

```bash
pytest
```

## Security

- All functions use IAM roles with least privilege
- DynamoDB uses encryption at rest
- API Gateway can be configured with authentication
- SQS uses server-side encryption

## License

MIT 