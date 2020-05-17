from src.AgentController.forwarder_controller import ForwarderController


class PublishHandler:

    def __init__(self, topic):
        self._for_client = ForwarderController()
        self._topic_ = topic

    def update_topic(self, topic):
        self._topic_ = topic

    def call_forwarder(self, topic):
        self._for_client.update_topic(topic)
        self._for_client.run()

    def run(self):
        self.call_forwarder(self._topic_)
