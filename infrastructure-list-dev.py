from datetime import datetime
import boto3
import csv
import json
import os

def lambda_handler(event, context):
    # Initialize AWS clients
    resource_groups = boto3.client('resource-groups')
    s3 = boto3.client('s3')
    sts_client = boto3.client('sts')

    # Get the account ID
    response = sts_client.get_caller_identity()
    account_id = response['Account']

    # Get current date
    current_date = datetime.now().date()

    # Define the tag filter and resources types
    tag_key = "env"
    tag_value = "dev"
    resource_types = ["AWS::EC2::Instance", "AWS::EC2::Subnet", "AWS::ApiGateway::RestApi", "AWS::CertificateManager::Certificate", "AWS::ECS::Cluster",
                    "AWS::ECS::ContainerInstance", "AWS::ECS::Service", "AWS::ECS::Task", "AWS::ECS::TaskDefinition", "AWS::EC2::VPC",
                    "AWS::ElasticLoadBalancingV2::LoadBalancer", "AWS::ElasticLoadBalancingV2::TargetGroup", "AWS::SNS::Topic", "AWS::SQS::Queue",
                    "AWS::S3::Bucket", "AWS::Lambda::Function", "AWS::ApiGateway::Stage", "AWS::AppStream::Fleet", "AWS::AppStream::ImageBuilder",
                    "AWS::AppStream::Stack", "AWS::BillingConductor::BillingGroup", "AWS::BillingConductor::CustomLineItem",
                    "AWS::BillingConductor::PricingPlan", "AWS::BillingConductor::PricingRule", "AWS::Braket::Job", "AWS::Braket::QuantumTask",
                    "AWS::ACMPCA::CertificateAuthority", "AWS::Cloud9::Environment", "AWS::CloudFormation::Stack", "AWS::CloudFront::Distribution",
                    "AWS::CloudFront::StreamingDistribution", "AWS::CloudTrail::Trail", "AWS::Logs::LogGroup",
                    "AWS::Synthetics::Canary", "AWS::CodeArtifact::Domain", "AWS::CodeArtifact::Repository","AWS::CodeBuild::Project",
                    "AWS::CodeCommit::Repository", "AWS::CodeGuruReviewer::RepositoryAssociation", "AWS::CodePipeline::CustomActionType",
                    "AWS::CodePipeline::Pipeline", "AWS::CodePipeline::Webhook", "AWS::Cognito::IdentityPool", "AWS::Cognito::UserPool",
                    "AWS::DataPipeline::Pipeline","AWS::DMS::Certificate","AWS::DMS::Endpoint",
                    "AWS::DMS::EventSubscription", "AWS::DMS::ReplicationInstance", "AWS::DMS::ReplicationSubnetGroup","AWS::DMS::ReplicationTask",
                    "AWS::DynamoDB::Table" ,"AWS::EMR::Cluster", "AWS::EMRContainers::JobRun", "AWS::EMRContainers::VirtualCluster", "AWS::EMRServerless::Application",
                    "AWS::EMRServerless::JobRun", "AWS::ElastiCache::CacheCluster", "AWS::ElastiCache::Snapshot", "AWS::ElasticBeanstalk::Application", "AWS::ElasticBeanstalk::ApplicationVersion",
                    "AWS::ElasticBeanstalk::ConfigurationTemplate","AWS::ElasticBeanstalk::Environment", "AWS::EC2::TransitGatewayRouteTable", "AWS::EC2::VPCPeeringConnection",
                    "AWS::EC2::VPNConnection", "AWS::EC2::VPNGateway", "AWS::ECR::Repository", 
                    "AWS::EFS::FileSystem", "AWS::ElasticInference::ElasticInferenceAccelerator", "AWS::EKS::Cluster",
                    "AWS::ElasticLoadBalancing::LoadBalancer", "AWS::Elasticsearch::Domain", "AWS::Events::Rule", "AWS::IAM::InstanceProfile", "AWS::IAM::ManagedPolicy", "AWS::IAM::OpenIDConnectProvider",
                    "AWS::IAM::SAMLProvider", "AWS::IAM::VirtualMFADevice", "AWS::Inspector::AssessmentTemplate", "AWS::KMS::Key", "AWS::Kinesis::Stream", "AWS::KinesisAnalytics::Application", "AWS::KinesisFirehose::DeliveryStream"]

    # Create a query-based resource group
    group_name = f'{account_id}-{current_date}.csv'

    # set s3 bucket
    bucket_name = 'primuslearning-aws-resources'
    s3_folder = 'export-aws-resources/'
    file_name = f'{account_id}-{current_date}.csv'
    file_name_lambda = f'/tmp/{account_id}-{current_date}.csv'

    resource_query = {
        "ResourceTypeFilters": resource_types,
        "TagFilters": [
            {
                "Key": tag_key,
                "Values": [tag_value]
            }
        ]
    }
    resource_query_str = json.dumps(resource_query)
    response = resource_groups.create_group(
        Name=group_name,
        Description='Group of getting aws resources',
        ResourceQuery={
            'Type': 'TAG_FILTERS_1_0',
            'Query': resource_query_str
        }
    )

    # Get the ARN of the resource group
    group_arn = response['Group']['GroupArn']
    print(f"Resource Group ARN: {group_arn}")

    # Get all the resources in the group
    resources = []
    next_token = ''
    while True:
        response = resource_groups.list_group_resources(
            Group=group_arn,
            MaxResults=50,
            NextToken=next_token
        )
        resources.extend(response['ResourceIdentifiers'])
        if 'NextToken' in response:
            next_token = response['NextToken']
        else:
            break

    # Write the resources to a CSV file
    with open(file_name_lambda, mode='w', newline='') as csv_file:
        fieldnames = ['Resource Name', 'Resource Type', 'ARN',
                    'Region', 'Tag Key', 'Tag Value']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header row to the CSV file
        writer.writeheader()

        # Write each resource to the CSV file
        for resource in resources:
            resource_arn = resource['ResourceArn']
            arn_parts = resource_arn.split(':')
            writer.writerow({
                'Resource Name': resource_arn.split('/')[-1],
                'Resource Type': arn_parts[2],
                'ARN': resource_arn,
                'Region': arn_parts[3],
                'Tag Key': tag_key,
                'Tag Value': tag_value
            })
            
    # upload csv file to s3 bucket
    object_key = s3_folder + file_name
    s3.upload_file(file_name_lambda, bucket_name, object_key)
    print("File Uploaded successfully to S3 bucket")