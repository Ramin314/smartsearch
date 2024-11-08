#!/usr/bin/env bash
awslocal s3 mb s3://smart-search-inputs

awslocal s3api put-bucket-cors --bucket smart-search-inputs --cors-configuration '{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
            "AllowedHeaders": ["*"],
            "ExposeHeaders": []
        }
    ]
}'

awslocal s3 mb s3://smart-search-outputs

awslocal s3api put-bucket-cors --bucket smart-search-outputs --cors-configuration '{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
            "AllowedHeaders": ["*"],
            "ExposeHeaders": []
        }
    ]
}'
