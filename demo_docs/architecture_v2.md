# Architecture Decision Record — Q3 2023

## Database Migration
We migrated from MySQL 5.7 to PostgreSQL 15 in August 2023.
Reason: Better JSON support, JSONB indexing, and open-source licensing.
The migration was led by Priya Sharma and the backend team.
All data was migrated using pgloader with zero downtime.

## New Deployment Process
Moved from Jenkins to GitHub Actions with ArgoCD for Kubernetes.
Deployments are now continuous (on merge to main branch).
Canary deployments enabled for production with 10% traffic split.
Jenkins server has been decommissioned.

## Payment Service Update
Payment service has been split into 3 microservices:
- payment-gateway (handles Stripe/Razorpay routing)
- billing-engine (invoicing, subscriptions, tax calculation)
- fraud-detection (ML-based anomaly detection, new in Q3)

Each microservice runs in its own Kubernetes pod.
Inter-service communication uses gRPC.

## Authentication Upgrade
Migrated from custom JWT to Auth0 managed service.
SSO enabled for internal tools via SAML 2.0.
Token expiry reduced to 1 hour with refresh token rotation.

## Known Issues
- PostgreSQL connection pooling needs tuning (PgBouncer not yet configured)
- Fraud detection model has 12% false positive rate — needs retraining
- Old MySQL backup scripts still running on cron — need cleanup
