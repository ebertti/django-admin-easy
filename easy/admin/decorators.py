# coding: utf-8


def smart(**kwargs):
    """
    Simple decorator to get custom fields on admin class, using this you will use less line codes

    :param short_description: description of custom field
    :type str:

    :param admin_order_field: field to order on click
    :type str :

    :param allow_tags: allow html tags
    :type bool:

    :param boolean: if field is True, False or None
    :type bool:

    :return: method decorated
    :rtype: method
    """

    def decorator(func):
        for key, value in kwargs.items():
            setattr(func, key, value)
        return func

    return decorator
