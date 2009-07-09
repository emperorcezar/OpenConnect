"""
Tags for performing basic value comparisons in templates.

"""


from django import template
from django.template import Library, TemplateSyntaxError, Node, NodeList, Variable, VariableDoesNotExist


COMPARISON_DICT = {
    'less': lambda x: x < 0,
    'less_or_equal': lambda x: x <= 0,
    'greater_or_equal': lambda x: x >= 0,
    'greater': lambda x: x > 0,
    }


class ComparisonNode(template.Node):
    def __init__(self, var1, var2, comparison, nodelist_true, nodelist_false):
        self.var1 = template.Variable(var1)
        self.var2 = template.Variable(var2)
        self.comparison = comparison
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
    
    def render(self, context):
        try:
            result = cmp(self.var1.resolve(context),
                         self.var2.resolve(context))
            if COMPARISON_DICT[self.comparison](result):
                return self.nodelist_true.render(context)
        # If either variable fails to resolve, return nothing.
        except template.VariableDoesNotExist:
            return ''
        # If the types don't permit comparison, return nothing.
        except TypeError:
            return ''
        return self.nodelist_false.render(context)


def do_comparison(parser, token):
    """
    Compares two values.
    
    Syntax::
    
        {% if_[comparison] [var1] [var2] %}
        ...
        {% else %}
        ...
        {% endif_[comparison] %}

    The {% else %} block is optional, and ``var1`` and ``var2`` may be
    variables or literal values.
    
    Supported comparisons are ``less``, ``less_or_equal``, ``greater``
    and ``greater_or_equal``.
    
    Examples::
    
        {% if_less some_object.id 3 %}
        <p>{{ some_object }} has an id less than 3.</p>
        {% endif_less %}
    
        {% if_greater_or_equal forloop.counter 4 %}
        <p>This is at least the fifth time through the loop.</p>
        {% else %}
        <p>This is one of the first four trips through the loop.</p>
        {% endif_greater_or_equal %}
    
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    comparison = bits[0].split('if_')[1]
    return ComparisonNode(bits[1], bits[2], comparison, nodelist_true, nodelist_false)

register = template.Library()
for tag_name in ('if_less', 'if_less_or_equal', 'if_greater_or_equal', 'if_greater'):
    register.tag(tag_name, do_comparison)

class IfInNode(Node):
    def __init__(self, var1, var2, nodelist_true, nodelist_false, negate):
        self.var1, self.var2 = Variable(var1), Variable(var2)
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfInNode>"

    def render(self, context):
        try:
            val1 = self.var1.resolve(context)
        except VariableDoesNotExist:
            val1 = None
        try:
            val2 = self.var2.resolve(context)
        except VariableDoesNotExist:
            val2 = None
        try:
            if (self.negate and val1 not in val2) or (not self.negate and val1 in val2):
                return self.nodelist_true.render(context)
            return self.nodelist_false.render(context)
        except TypeError:
            raise ValueError, "Second arg to ifin or ifnotin must be iterable"

def do_ifin(parser, token, negate):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfInNode(bits[1], bits[2], nodelist_true, nodelist_false, negate)

def ifin(parser, token):
   return do_ifin(parser, token, False)
register.tag('ifin', ifin)

def ifnotin(parser, token):
    return do_ifin(parser, token, True)
register.tag('ifnotin', ifnotin)
