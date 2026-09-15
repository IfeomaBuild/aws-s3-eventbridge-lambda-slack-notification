# Architecture

## Event-Driven Workflow

```text
+------------------+
|    Amazon S3     |
|   Object Upload  |
+--------+---------+
         |
         | Object Created event
         v
+------------------+
| Amazon           |
| EventBridge      |
|                  |
| Rule:            |
| s3-object-       |
| created-rule     |
+--------+---------+
         |
         | Invoke target
         v
+------------------+
| AWS Lambda       |
|                  |
| s3-slack-        |
| notification     |
+--------+---------+
         |
         | HTTPS POST
         v
+------------------+
| Slack Incoming   |
| Webhook          |
+--------+---------+
         |
         v
+------------------+
| #s3-notification |
+------------------+
```

## Component Responsibilities

### Amazon S3

Amazon S3 stores the uploaded files. EventBridge integration is enabled on the bucket so S3 events can be delivered to Amazon EventBridge.

### Amazon EventBridge

EventBridge acts as the routing layer between S3 and Lambda. The rule matches S3 events where the detail type is `Object Created` and forwards matching events to the Lambda target.

This intermediary design makes the architecture easier to extend. Additional rules or targets can be introduced without putting notification logic directly into S3.

### AWS Lambda

The Python Lambda function reads the EventBridge event and extracts:

- Bucket name
- Object key/file name
- Object size
- Event timestamp

It then builds a human-readable message and sends a JSON HTTP POST request to Slack.

### Slack

A Slack Incoming Webhook receives the request from Lambda and posts the formatted message to the configured channel.

### Amazon CloudWatch

Lambda execution logs are written to CloudWatch. These logs are the primary source for diagnosing configuration, runtime, and integration errors.

## Security Boundary

The Slack webhook URL is not included in this repository. It is supplied to Lambda through the `SLACK_WEBHOOK_URL` environment variable. Credentials and webhook secrets should never be hard-coded or committed to source control.

## Event Sequence

```text
User uploads file
      ↓
S3 stores object
      ↓
S3 publishes Object Created event
      ↓
EventBridge matches rule
      ↓
EventBridge invokes Lambda
      ↓
Lambda parses event
      ↓
Lambda POSTs message to Slack webhook
      ↓
Slack displays notification
```

## Observed End-to-End Result

The project was verified with a real image upload. After the object was uploaded to S3, the workflow automatically delivered a Slack message containing the bucket name, file name, file size, and event timestamp. This confirmed that the complete S3 → EventBridge → Lambda → Slack path was functioning.
