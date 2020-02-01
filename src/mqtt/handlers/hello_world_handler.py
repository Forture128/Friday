"""
Project:
Author:
"""


class HelloWorldHandler:
    """ This handler does the basic listen to hello topic"""

    def get_subscriptions(self):
        return [
            "hello",
        ]

    def handle_for(self, mqttc, obj, msg):
        print("Holla!")
