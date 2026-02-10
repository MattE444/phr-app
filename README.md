
# Personal Health Records API (PHR)

A secure, cost-efficient, serverless backend for aggregating personal medical data
from multiple providers into a single system.

## Motivation
Managing health data across multiple providers and portals is fragmented.
This project explores how to design a secure, scalable personal health record
system while remaining cost-conscious for individual users.

## Architecture
- AWS API Gateway (HTTP API)
- AWS Lambda (Python)
- Amazon Cognito (JWT-based authentication)
- DynamoDB (on-demand)
- Infrastructure as Code via AWS SAM
- CI/CD with GitHub Actions (OIDC, no long-lived AWS keys)

> The architecture intentionally avoids always-on infrastructure
> (e.g., EC2, ALB, RDS) to minimize cost during early development.

## Security
- JWT validation via Cognito user pools
- IAM least-privilege for Lambda
- No credentials stored in the repository

## Cost Controls
- Serverless, pay-per-request services only
- No NAT Gateway, no load balancers
- AWS Budgets configured to prevent surprise charges

## Current Status
- API authentication implemented
- Health and identity endpoints live
- Serverless infrastructure deployed
- Data model in progress

## Roadmap
- Provider / visit / lab record modeling
- DynamoDB access patterns
- Optional frontend UI
- Production hardening

## Why This Project
This project emphasizes architectural decision-making, security, and cost
awareness over UI polish, reflecting real-world cloud engineering tradeoffs.







