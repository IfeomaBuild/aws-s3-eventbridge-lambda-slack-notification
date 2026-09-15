import json
import os
import urllib.request
import urllib.parse


def lambda_handler(event, context):
    """Process an S3 Object Created event from EventBridge and notify Slack."""
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]

    detail = event.get("detail", {})
    bucket_name = detail.get("bucket", {}).get("name", "Unknown")
    object_detail = detail.get("object", {})
    object_key = urllib.parse.unquote_plus(object_detail.get("key", "Unknown"))
    object_size = object_detail.get("size", "Unknown")
    event_time = event.get("time", "Unknown")

    message = (
        "🔔 New S3 Object Uploaded!\n"
        f"Bucket: {bucket_name}\n"
        f"File: {object_key}\n"
        f"Size: {object_size} bytes\n"
        f"Time: {event_time}"
    )

    payload = json.dumps({"text": message}).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        response_body = response.read().decode("utf-8")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Slack notification sent successfully",
                "slack_response": response_body,
            }
        ),
    }
