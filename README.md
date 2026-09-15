# Event-Driven S3 Notifications with Amazon EventBridge, Lambda & Slack

A serverless, event-driven AWS project that automatically sends a Slack notification whenever a new object is uploaded to an Amazon S3 bucket.

## Architecture

```text
Amazon S3
    |
    | Object Created event
    v
Amazon EventBridge
    |
    | Matching rule
    v
AWS Lambda (Python)
    |
    | HTTPS POST
    v
Slack Incoming Webhook
    |
    v
#s3-notification
```

**Event flow:** `S3 → EventBridge → Lambda → Slack`

## Project Overview

The goal of this project was to build an event-driven notification system using Amazon EventBridge as the intermediary between Amazon S3 and AWS Lambda. When a file is uploaded to the S3 bucket, S3 publishes an event to EventBridge. An EventBridge rule matches the `Object Created` event and invokes a Lambda function. The Lambda function extracts information about the uploaded object and sends a formatted notification to Slack.

## AWS Services & Technologies

- **Amazon S3** — stores uploaded objects and publishes events.
- **Amazon EventBridge** — filters and routes S3 `Object Created` events.
- **AWS Lambda** — processes the event using Python.
- **Amazon CloudWatch** — provides Lambda execution logs and troubleshooting information.
- **Slack Incoming Webhooks** — receives notifications from Lambda.
- **Python 3** — Lambda runtime and notification logic.

## Resources Used in My Implementation

- AWS Region: `eu-north-1` (Europe - Stockholm)
- Lambda function: `s3-slack-notification`
- EventBridge rule: `s3-object-created-rule`
- Slack channel: `#s3-notification`

> Bucket names are globally unique. Create your own bucket rather than copying a bucket name from this repository.

## How It Works

1. A user uploads a file to the S3 bucket.
2. Amazon S3 generates an `Object Created` event.
3. EventBridge receives the event and evaluates configured rules.
4. `s3-object-created-rule` matches the event.
5. EventBridge invokes the `s3-slack-notification` Lambda function.
6. Lambda reads the bucket name, object key, object size, and event time.
7. Lambda sends the information to Slack through an Incoming Webhook.
8. The notification appears in the configured Slack channel.

## EventBridge Event Pattern

The rule uses the pattern in [`eventbridge-pattern.json`](eventbridge-pattern.json):

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"]
}
```

For tighter filtering, you can add a specific bucket name under `detail.bucket.name`.

## Lambda Configuration

Create a Python Lambda function and add an environment variable:

```text
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/REPLACE_WITH_YOUR_WEBHOOK
```

**Never commit the real Slack webhook URL to GitHub.** Treat it as a secret. For production workloads, consider AWS Secrets Manager or another dedicated secrets-management solution.

The function implementation is available in [`lambda_function.py`](lambda_function.py).

## Testing

A sample EventBridge event is provided in [`test-event.json`](test-event.json). Update the example values if required and use it as a Lambda test event.

For an end-to-end test, upload an object to the S3 bucket, open the Slack channel, and confirm that a notification appears automatically. If it does not arrive, inspect the Lambda logs in CloudWatch.

Example notification:

```text
🔔 New S3 Object Uploaded!
Bucket: example-bucket
File: cat image.jpeg
Size: 23288 bytes
Time: 2026-09-14T11:25:03Z
```

## Troubleshooting & Challenges

### Missing `SLACK_WEBHOOK_URL`

During testing, Lambda returned:

```text
KeyError: 'SLACK_WEBHOOK_URL'
```

The environment variable had not been configured. Adding `SLACK_WEBHOOK_URL` to the Lambda environment variables resolved the issue.

### Incorrect webhook value

Another failure produced an error similar to:

```text
URLError: <urlopen error unknown url type: curl ...>
```

The environment variable contained an entire `curl` command instead of the webhook URL. The fix was to store **only** the raw Slack Incoming Webhook URL.

### EventBridge configuration

Configuring the S3 event through the EventBridge console required selecting the correct S3 event type and `Object Created` event. The final rule routes matching events to Lambda.

### Permissions

EventBridge needs permission to invoke the Lambda target. The target configuration must therefore include the appropriate invocation permissions.

### Debugging with CloudWatch

CloudWatch Logs were essential for identifying the exact Lambda errors. This reinforced the importance of checking logs and tracing each stage of an event-driven workflow rather than guessing where a failure occurred.

## What I Learned

This project gave me practical experience with serverless and event-driven architecture. I learned how AWS services exchange JSON events, how EventBridge can decouple event producers from consumers, how Lambda integrates with external services through HTTP webhooks, and how environment variables and permissions affect application behavior.

The troubleshooting process also strengthened my understanding of CloudWatch logging and systematic cloud debugging. Testing each component independently before performing an end-to-end S3 upload made it easier to isolate configuration and integration problems.

## Security Considerations

- Never commit Slack webhook URLs, AWS access keys, tokens, or passwords.
- Use IAM least-privilege permissions.
- Keep secrets out of source code and test events.
- Rotate a webhook immediately if it is accidentally exposed.
- Consider AWS Secrets Manager for production secret storage.

## Repository Structure

```text
.
├── README.md
├── lambda_function.py
├── eventbridge-pattern.json
├── test-event.json
├── .gitignore
└── docs/
    └── architecture.md
```

## Future Improvements

Potential extensions include filtering notifications by file type or S3 prefix, using multiple EventBridge targets, adding a dead-letter queue for failed processing, storing secrets in AWS Secrets Manager, adding infrastructure as code, and sending richer Slack Block Kit messages.

## Author

Built as a hands-on AWS cloud project demonstrating event-driven architecture, serverless computing, monitoring, troubleshooting, and third-party integration.

## License

This project is provided for educational and portfolio purposes.
