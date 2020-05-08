import re

class SubscriptionTopicMatch:

    def subscription_matching(topic, subscription):
        if re.match(subscription.translate({43:"[^/]+",35:".+", 36:"\$"}), topic):
            return True
        else:
            return False

