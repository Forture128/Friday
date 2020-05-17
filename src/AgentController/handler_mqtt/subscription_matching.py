import re


# This method check matching between 2 topic.
def subscription_matching(topic, subscription):
    if re.match(subscription.translate({43: "[^/]+", 35: ".+", 36: "\$"}), topic):
        return True
    else:
        return False
