from django import template

register = template.Library()

@register.filter
def cut(value, arg):
    return value.replace(arg, "")

@register.simple_tag
def call_method(obj, method_name, **kwargs):
    method = getattr(obj, method_name)
    return method(**kwargs)

@register.filter
def contains(value, arg):
    if value.find(arg) == 0:
        return True
    else:
        return None
    