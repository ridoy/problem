### Local development

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8080 create-mp3:app
```

Then visit localhost:8080 in your browser.

Also requires you set these variables in your environment: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

Set up an AWS account with S3, DynamoDB
