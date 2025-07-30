# 🩺 Patient Vitals Monitoring System (AWS Serverless)

This project demonstrates a real-time **patient vitals monitoring system** using **AWS serverless architecture**. It allows medical IoT devices to send patient vitals data via an API, which is then stored, archived, and monitored for anomalies.

---

## 📌 Key Features

- Accepts vital signs data through a RESTful API
- Stores structured readings in **DynamoDB**
- Archives all readings in **S3** for historical analysis
- Sends **SNS alerts** for critical health values (e.g., abnormal heart rate or temperature)

---

## 🛠️ Tech Stack

- **AWS Lambda** – Backend compute logic (Python)
- **API Gateway** – Expose HTTP endpoints
- **Amazon DynamoDB** – Store structured vital records
- **Amazon S3** – Archive JSON data
- **Amazon SNS** – Trigger alerts for abnormal readings
- **IAM & KMS** – Secure access and optional encryption

---

## 🧪 Sample Input

```json
{
  "patient_id": "PT001",
  "vitals": {
    "heart_rate": 110,
    "temperature": 101.5,
    "oxygen_saturation": 92
  },
  "location": "Ward-7"
}

