import json
from .pysimpleurl import request


class Client(object):
    def __init__(self, api_url, api_key, site_id):
        self.api_url = api_url[:-1] if api_url.endswith("/") else api_url
        self.api_key = api_key
        self.site_id = site_id

    def _get_incoming_url(self):
        return (
            self.api_url
            + "/sites/"
            + str(self.site_id)
            + "/device_messages/v3/incoming"
        )

    def publish_device_message_list(self, device_message_list):
        """
        Publishes a list of device messages
        """

        incoming_url = self._get_incoming_url()
        data = device_message_list
        headers = {"Authorization": "Bearer %s" % self.api_key}

        response = request(incoming_url, headers=headers, data=data, method="post")
        if response.status != 200:
            ctx = {
                "url": incoming_url,
                "status": response.status,
                "body": response.body,
            }
            raise Exception("could not publish message: " + str(ctx))

    def publish_device_message(self, device_message):
        """
        Publishes a device message
        """
        device_message_list = [device_message]
        self.publish_device_message_list(device_message_list)
