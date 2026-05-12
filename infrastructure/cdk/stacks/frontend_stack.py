import aws_cdk as cdk
from aws_cdk import aws_s3 as s3, aws_cloudfront as cf, aws_cloudfront_origins as origins
from constructs import Construct


class FrontendStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, api, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self, "FrontendBucket",
            bucket_name=f"training-manager-frontend-{self.account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        distribution = cf.Distribution(
            self, "Distribution",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
            error_responses=[
                cf.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                )
            ],
        )

        cdk.CfnOutput(self, "FrontendUrl", value=f"https://{distribution.domain_name}")
        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
