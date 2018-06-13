
from google.cloud import pubsub

class Pusher:
    publisher = pubsub.PublisherClient()
    topic_path = None
    
    def __init__(self, project, topic_name):
        self.topic_path = self.publisher.topic_path(project, topic_name)

    def publish(self, data):
        print(data)
        self.publisher.publish(self.topic_path, data=data)

