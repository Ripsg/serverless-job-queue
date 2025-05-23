# Clean up existing .aws-sam directory
Remove-Item -Recurse -Force .aws-sam -ErrorAction SilentlyContinue

# Create layer directory structure
New-Item -ItemType Directory -Force -Path .aws-sam/layers/dependencies/python

# Install dependencies
pip install -r requirements.txt -t .aws-sam/layers/dependencies/python

# Create layer zip file
Compress-Archive -Path .aws-sam/layers/dependencies/python/* -DestinationPath .aws-sam/layers/dependencies/python.zip -Force

# Clean up temporary files
Remove-Item -Recurse -Force .aws-sam/layers/dependencies/python

# Build SAM application
sam build 