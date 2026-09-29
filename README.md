# Incident Assistant CI/CD Demo

Flow:

Git push -> GitHub Actions -> tests/lint -> Docker build -> Trivy scan -> ECR push -> SSM deploy -> EC2 Docker -> CloudWatch Logs.

Required GitHub repository variables:

- AWS_ACCOUNT_ID
- AWS_BUILD_ROLE_ARN
- AWS_DEPLOY_ROLE_ARN
- DEV_EC2_INSTANCE_ID

The workflow uses GitHub OIDC, so no long-lived AWS access key is stored in GitHub.
