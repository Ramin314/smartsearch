# Smart Search

## Local setup

Add a .env file to the root of the repo with env vars found in .env.example but add a value for the `OPENAI_API_KEY` which you can obtain from [OpenAI](https://openai.com/blog/openai-api).

Run `docker-compose up` and visit the application at `localhost:8000`

## Deployment

Add the secrets from the .env file (except `POSTGRES_HOST` and `OPENSEARCH_HOST`) to an AWS Secrets Manager secret called `smart-search`.

Store `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` within the GitHub repo secrets.

Create an AWS ECR repository called `smart-search`.

Run the pipeline.
