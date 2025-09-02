import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialize AWS clients outside the handler for better performance
# This allows the Lambda execution environment to reuse these clients across invocations.
s3_client = boto3.client('s3')
translate_client = boto3.client('translate')

# Get the output bucket name from an environment variable set by CloudFormation/Terraform
OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET_NAME']

def lambda_handler(event, context):
    """
    This function is triggered by an S3 event when a .json file is uploaded.
    It reads the file, translates the text using AWS Translate, and saves the
    result to another S3 bucket.
    """
    try:
        # 1. Validate event structure and get S3 event details
        if not event.get('Records') or not event['Records']:
            raise ValueError("Invalid event: No Records found")
        
        record = event['Records'][0]
        if 's3' not in record:
            raise ValueError("Invalid event: Not an S3 event")
        
        source_bucket = record['s3']['bucket']['name']
        source_key = record['s3']['object']['key']

        print(f"Processing file {source_key} from bucket {source_bucket}")

        # 2. Read the JSON file content from the source S3 bucket
        try:
            response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
            content = response['Body'].read().decode('utf-8')
            data = json.loads(content)
        except ClientError as e:
            print(f"Error reading from S3: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            raise ValueError(f"Invalid JSON format in file {source_key}")

        # 3. Extract required fields from the JSON payload
        source_language = data.get('source_language')
        target_language = data.get('target_language')
        text_to_translate = data.get('text')

        # Basic validation to ensure all required keys are present
        if not all([source_language, target_language, text_to_translate]):
            raise ValueError("Input JSON is missing one or more required keys: 'source_language', 'target_language', 'text'")

        # 4. Call the AWS Translate service to perform the translation
        print(f"Translating text from '{source_language}' to '{target_language}'...")
        try:
            translation_response = translate_client.translate_text(
                Text=text_to_translate,
                SourceLanguageCode=source_language,
                TargetLanguageCode=target_language
            )
        except ClientError as e:
            print(f"Error calling AWS Translate: {e}")
            raise

        translated_text = translation_response.get('TranslatedText')
        print("Translation successful.")

        # 5. Prepare the output JSON object
        output_data = {
            'source_language': source_language,
            'original_text': text_to_translate,
            'target_language': target_language,
            'translated_text': translated_text
        }

        # 6. Write the output JSON to the destination S3 bucket
        # We'll prepend "translated-" to the original filename
        output_key = f"translated-{source_key}"

        try:
            s3_client.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=output_key,
                Body=json.dumps(output_data, indent=2, ensure_ascii=False),
                ContentType='application/json'
            )
        except ClientError as e:
            print(f"Error writing to S3: {e}")
            raise

        print(f"Successfully saved translated file to s3://{OUTPUT_BUCKET}/{output_key}")
        
        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps('Translation completed successfully!')
        }

    except Exception as e:
        # Log the full error for debugging in CloudWatch
        print(f"Error processing file: {str(e)}")
        # Raise the exception to mark the Lambda invocation as failed
        raise e