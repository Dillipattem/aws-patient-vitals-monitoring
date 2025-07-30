import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

# AWS service clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sns = boto3.client('sns')

# Configurations (Replace with your actual names)
DYNAMO_TABLE = 'patient_vitals'
S3_BUCKET = 'patient-historical-data'
SNS_TOPIC_ARN = 'arn:aws:sns:eu-north-1:302263053048:medical_alerts'

# Thresholds for triggering alerts
CRITICAL_RANGES = {
    "heart_rate": {"min": 60, "max": 100},
    "temperature": {"min": 96.0, "max": 100.4},
    "oxygen_saturation": {"min": 95, "max": 100}
}

# Helper to recursively convert floats to Decimals for DynamoDB
def convert_floats(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats(elem) for elem in obj]
    else:
        return obj

# Helper to detect abnormal vitals
def is_critical(vitals):
    alerts = {}
    for key, range_ in CRITICAL_RANGES.items():
        if key in vitals:
            value = vitals[key]
            if value < range_["min"] or value > range_["max"]:
                alerts[key] = value
    return alerts

# Lambda entry point
def lambda_handler(event, context):
    try:
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)

        patient_id = body["patient_id"]
        timestamp = body.get("timestamp", datetime.utcnow().isoformat())
        vitals = body["vitals"]
        location = body.get("location", "unknown")

        reading_id = f"{patient_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        item = convert_floats({
            "reading_id": reading_id,
            "patient_id": patient_id,
            "timestamp": timestamp,
            "vitals": vitals,
            "location": location
        })

        # Store in DynamoDB
        table = dynamodb.Table(DYNAMO_TABLE)
        table.put_item(Item=item)

        # Store in S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=f"archive/{reading_id}.json",
            Body=json.dumps(item, default=str),
            ContentType='application/json'
        )

        # Publish alert if critical
        critical_alerts = is_critical(vitals)
        if critical_alerts:
            alert_msg = f"CRITICAL ALERT for patient {patient_id} in {location}!\nAbnormal values: {json.dumps(critical_alerts)}"
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=alert_msg,
                Subject="Patient Vital Signs Alert"
            )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Recorded successfully",
                "reading_id": reading_id
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

