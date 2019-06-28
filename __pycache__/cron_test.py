import boto
import twitter_credentials
# crontab -e
# crontab -l
# dont do this: sudo service cron start


# aws stuff
# import os
# aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
# aws_access_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']

def test_cron():

    conn = boto.connect_s3(aws_access_key, aws_access_secret_key)

    bucket_name = 'emoji-tweets'

    b = conn.get_bucket(bucket_name)

    file_object = b.new_key('tweets/cron_test.md')#where to save in S3
    file_object.set_contents_from_filename('/home/ubuntu/emoji-tweets/README.md')
