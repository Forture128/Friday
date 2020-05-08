from utils.object_utils import is_object_has_method


def build_mapper_subscribe_handlers(handler_list):
    """

    :type handler_list: Array
    """
    result = {}

    for handler in handler_list:

        topic_list = []
        if is_object_has_method(handler, "get_subscription"):
            topic_list = handler.get_subscription()

        for topic in topic_list:
            result.setdefault(topic, [])
            result[topic].append(handler)
    return result
__all__ = ['build_mapper_subscribe_handlers']
