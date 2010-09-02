from django import template
from django.core.urlresolvers import reverse


register = template.Library()


class AdminLink(template.Node):

    def __init__(self, obj_str):
        self.obj_var = template.Variable(obj_str)

    def render(self, context):
        obj = self.obj_var.resolve(context)
        url = reverse('admin:%s_%s_change' %
                (obj._meta.app_label, obj._meta.module_name), args=(obj.id,))

        return u'<a href="%s">Edit %s in admin</a>' % (url, obj.__unicode__())


@register.tag('edit_link')
def get_app_module(parser, token):
    tag, obj_str = token.split_contents()

    return AdminLink(obj_str)
