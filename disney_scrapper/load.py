import boto3


def load_to_sns(message, subject, sns_topic):
    print(f'Sending message {sns_topic=} {message=}')
    client = boto3.client('sns')
    client.publish(TopicArn = sns_topic, Subject = subject, Message = message)
