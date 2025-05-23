# Get the API endpoint from us-east-2
$API_ENDPOINT = aws cloudformation describe-stacks --stack-name serverless-job-queue --region us-east-2 --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text
Write-Host "API Endpoint: $API_ENDPOINT"

# Test the API
$jobRequest = @{
    job_type = "image_processing"
    payload = @{
        image_url = "https://i.blogs.es/5ec849/thumb_772294_default_big/450_1000.jpeg"
        operations = @("resize", "grayscale")
    }
} | ConvertTo-Json

Write-Host "`nRequest body:"
Write-Host $jobRequest

try {
    # Submit the job
    Write-Host "`nSubmitting test job..."
    $response = Invoke-RestMethod -Uri "$API_ENDPOINT/jobs" -Method Post -Body $jobRequest -ContentType "application/json" -ErrorAction Stop
    
    # Display the response
    Write-Host "`nJob submitted successfully:"
    $response | ConvertTo-Json

    # Get the job ID
    $jobId = $response.job_id
    Write-Host "`nJob ID: $jobId"

    # Check job status
    Write-Host "`nChecking job status..."
    Start-Sleep -Seconds 5
    $status = Invoke-RestMethod -Uri "$API_ENDPOINT/jobs/$jobId" -Method Get
    Write-Host "`nJob status:"
    $status | ConvertTo-Json
}
catch {
    Write-Host "`nError occurred:"
    Write-Host "Status code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Status description: $($_.Exception.Response.StatusDescription)"
    Write-Host "Error message: $($_.Exception.Message)"
}
