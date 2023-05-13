# aws-infrastructure-list-resource-tagging

You can use the following resources to get a list of all aws resources in your AWS account that have been previously tagged. To do this:

- Create a lambda function and use the infrastructure-list-dev.py code to get all the tagged resources in your account. Modify the bucket name and folder name to match a bucket in your aws account.
- Make sure to have the correct permissions added. Lambda execution permissions are needed, as well as permissions to write to s3 and to tag resources. 
- If your resources have not been tagged, you could use the tag-aws-resources.py code to tag all the resources in your aws environment with any tags of your choice.