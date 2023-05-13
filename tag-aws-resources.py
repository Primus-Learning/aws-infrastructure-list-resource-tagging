import boto3

# Initialize the AWS clients
resourcegroupstaggingapi = boto3.client('resourcegroupstaggingapi')

# Tag user-defined resources if not already tagged
try:
    response = resourcegroupstaggingapi.get_resources()
    resources = response['ResourceTagMappingList']

    # Define the user-defined tags to be added
    tags_to_add = [
        {'Key': 'env', 'Value': 'dev'}
    ]

    # Process the first page of results
    for resource in resources:
        resource_arn = resource['ResourceARN']
        tags = resource.get('Tags', [])

        # Filter out system tags
        user_tags = [tag for tag in tags if not tag['Key'].startswith('aws:')]

        # Add new tags to the user-defined tags
        updated_tags = user_tags + tags_to_add

        # Convert the list of tags to a dictionary
        tags_dict = {tag['Key']: tag['Value'] for tag in updated_tags}

        # Add tags to the resource
        resourcegroupstaggingapi.tag_resources(ResourceARNList=[resource_arn], Tags=tags_dict)
        print(f"Tags added to resource: {resource_arn}")

    # Check if there are more pages
    while 'PaginationToken' in response and response['PaginationToken']:
        next_token = response['PaginationToken']
        response = resourcegroupstaggingapi.get_resources(PaginationToken=next_token)
        resources = response['ResourceTagMappingList']

        # Process the next page of results
        for resource in resources:
            resource_arn = resource['ResourceARN']
            tags = resource.get('Tags', [])

            # Filter out system tags
            user_tags = [tag for tag in tags if not tag['Key'].startswith('aws:')]

            # Add new tags to the user-defined tags
            updated_tags = user_tags + tags_to_add

            # Convert the list of tags to a dictionary
            tags_dict = {tag['Key']: tag['Value'] for tag in updated_tags}

            # Add tags to the resource
            resourcegroupstaggingapi.tag_resources(ResourceARNList=[resource_arn], Tags=tags_dict)
            print(f"Tags added to resource: {resource_arn}")
except Exception as e:
    print(f"Error: {e}")