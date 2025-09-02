**Serverless Translator (AWS Capstone Project)**


Clear, step-by-step guide so anyone can understand, deploy, test, and extend this project.
This repo implements an event-driven, serverless translation pipeline on AWS using CloudFormation, Lambda (Python + Boto3), Amazon Translate, and S3.



🔎 **Project summary **

Upload a JSON file to a request S3 bucket; an S3 event triggers a Lambda function that uses Amazon Translate and writes the translated JSON to a response S3 bucket.

📂** Repository layout (what’s in this repo)
serverless-translator/
**

├─ template.yaml              # CloudFormation template
├─ .gitignore
├─ README.md                  # <-- you are here
├─ src/
│  └─ translate_handler.py    # Lambda function code
├─ samples/
│  ├─ english_to_french.json
│  └─ english_to_spanish.json
└─ docs/
   └─ project-doc.pdf         # Full project write-up


   

**🧰 Tools & technologies**

AWS services: Amazon S3, AWS Lambda, Amazon Translate, IAM, CloudFormation, CloudWatch

Language: Python 3.9

SDK: Boto3

🏗 System architecture (step-by-step)

User uploads a JSON file into the Request S3 Bucket.

S3 generates an event for the new object and triggers the Lambda function.

Lambda reads the uploaded JSON, extracts text and language details.

Lambda calls Amazon Translate, receives the translated text.

Lambda writes the translated JSON file to the Response S3 Bucket.

User retrieves the translated file from the response bucket.




✅ **Console step-by-step guide (exact actions you can follow)
Step 0 — Prepare**

Region: use us-east-1 (N. Virginia) for testing if you followed the project notes.
Make sure your AWS account has permissions to create S3 buckets, Lambda, IAM roles, and to use Amazon Translate. Enable Amazon Translate in the account if required.





**Step 1 — Create S3 buckets (request and response)**

In the S3 console, create two buckets:

request-bucket-demo-yourname (input)

response-bucket-demo-yourname (output)
Keep default settings for now. Note the exact names — you will use them in Lambda or CloudFormation.




**Step 2 — Create IAM role for Lambda (console)**

Open IAM → Roles → Create role.

Trusted entity: AWS service → Lambda.

Attach minimal policies required (recommendations below):

AmazonS3ReadOnlyAccess or scoped S3 read/write to your two buckets

TranslateReadOnly or scoped Translate actions the function needs (or TranslateFullAccess for test accounts)

AWSLambdaBasicExecutionRole (for CloudWatch logs)

Name the role LambdaTranslateRole and create it.

Recommendation: For production, scope S3 and Translate permissions to exact resources (least privilege). Do not use * unless it’s a separate test account.




**Step 3 — Create the Lambda function**

Lambda → Create function → Author from scratch.

Function name: TranslateFunction (or your preferred name)

Runtime: Python 3.9

Execution role: Use existing role LambdaTranslateRole

Replace default code with the function in src/translate_handler.py.

Add environment variables (Lambda configuration):

REQUEST_BUCKET = your request bucket name

RESPONSE_BUCKET = your response bucket name

Optional: DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG




**Step 4 — Add S3 trigger to Lambda**

On the Lambda function page → Triggers → Add trigger.

Select S3 and set:

Bucket: your request bucket

Event: PUT (All object create events)

Allow permission to be added to Lambda role (check the box)

Add the trigger.

Now Lambda is invoked automatically when an object is uploaded.




**Step 5 — Manual end-to-end test (console)**

Upload samples/english_to_spanish.json to your request bucket via the S3 console.

Confirm Lambda was invoked by checking CloudWatch Logs for the function.

Open the response bucket and verify there is a translated file (for example sample-translated.json) with the translated text included.







**⚙️ CloudFormation (Infrastructure as Code) — deploy from this repo
**

The CloudFormation file in this repo is template.yaml.

Create a deployment artifact bucket (CloudFormation needs it):

aws s3 mb s3://your-unique-deployment-bucket


**Package the CloudFormation template**

aws cloudformation package \
  --template-file template.yaml \
  --s3-bucket your-unique-deployment-bucket \
  --output-template-file packaged.yaml


**Deploy the packaged template**

aws cloudformation deploy \
  --template-file packaged.yaml \
  --stack-name serverless-translator-stack \
  --capabilities CAPABILITY_IAM


**Notes:**

CAPABILITY_IAM is required because the stack creates an IAM role.

If hardcoded bucket names cause conflicts, use CloudFormation parameters or let CloudFormation generate unique names.







**🔬 Sample input and expected output**

Sample input JSON (upload to request bucket):

{
  "source_language": "en",
  "target_language": "es",
  "text": "Hello, good morning"
}


Expected output JSON (in response bucket):

{
  "source_language": "en",
  "target_language": "es",
  "original_text": "Hello, good morning",
  "translated_text": "Hola, buenos días"

  
}






**🧪 Testing & validation checklist**

Upload test files for language pairs (English↔Spanish, English↔French).

Check CloudWatch logs for Lambda invocation and errors.

Ensure response JSON includes both original_text and translated_text.

Verify S3 lifecycle policies (request files 30 days, response files 60 days).






**🛠 Troubleshooting (common issues and fixes)**

SubscriptionRequiredException from Amazon Translate

Fix: Enable Amazon Translate subscription in your AWS account console and retry.

CloudFormation rollback due to bucket name conflicts

Fix: Don’t hardcode public/global bucket names. Use parameters or allow CloudFormation to generate unique names.

**Access denied errors**

Fix: Ensure the Lambda execution role includes specific S3 access to the request and response buckets and proper Translate permissions.







**🧹 Cleanup (avoid ongoing charges)**

Delete the CloudFormation stack:

aws cloudformation delete-stack --stack-name serverless-translator-stack


Empty and delete any S3 buckets created by the stack (CloudFormation won’t delete non-empty buckets).







🔒 **Security considerations (what I applied)**

Least privilege IAM for Lambda role.

No hardcoded credentials in code; Lambda uses its execution role.

CloudWatch logging enabled for visibility and audits.

Lifecycle policies to limit data retention.






📦** Deliverables (what to look for in the repo)**

template.yaml — CloudFormation template provisioning buckets and IAM role.

src/translate_handler.py — Lambda translation logic (Python + Boto3).

samples/*.json — Example input files.

docs/project-doc.pdf — Full write-up and step-by-step report.







📝 **Lessons learned (short and bold)**

Start manual, then automate. Console setup helped me learn service relationships before switching to IaC.

IaC is valuable. CloudFormation makes deployments repeatable and consistent.

Permissions matter. IAM scoping and service subscriptions can break workflows if not handled early.

Observability is critical. CloudWatch logs saved time during debugging.

Iterate in milestones. Breaking the project into phases prevented big failures.







🚀** Roadmap / future improvements**

Add API Gateway for real-time REST translation requests.

Add a CloudWatch dashboard for metrics and alarms.

Add S3 Glacier lifecycle rules for long-term archiving.

Add CI/CD pipeline (CodePipeline) for automated Lambda deployments.

[📄 Project Documentation (PDF)](docs/project-doc.pdf)
