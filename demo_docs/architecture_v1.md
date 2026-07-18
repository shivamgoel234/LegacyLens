# System Architecture — Q1 2023

## Database
We use MySQL 5.7 as our primary database. All services connect directly.
The DBA is Priya Sharma who manages backups and replication.
Backup schedule: Daily full backup at 2 AM IST, hourly incrementals.

## Deployment
We deploy using Jenkins CI/CD pipeline to AWS EC2 instances.
Deployments happen every Tuesday and Thursday.
Rollback process: SSH into EC2, run rollback.sh script manually.

## Payment Service
The payment service is a monolith written in Java Spring Boot.
It handles Stripe and Razorpay integrations.
Contact: Priya Sharma (priya@company.com)

## Authentication
We use JWT tokens with 24-hour expiry.
Auth service runs on a separate EC2 instance.
Secret rotation is done manually by the infra team quarterly.

## Monitoring
We use Datadog for APM and CloudWatch for infrastructure alerts.
On-call rotation is managed in PagerDuty.
Priya handles the database alerts channel.
