"""
Custom Django template tags

Written by John Smith 2010-2012 | http://www.john-smith.me
Copyright Menboku Ltd 2010-2012 | http://www.menboku.co.uk
Licenced under GPL v2

"""

from django.template import Library
register = Library()

from django.template import Node, VariableDoesNotExist, \
    TemplateSyntaxError, NodeList, resolve_variable

import logging

def iflengthequal(parser, token):
    """
    Usage {% iflengthequal list 1 %}Only 1 member{% endiflengthequal %}
    Loosely derived from http://djangosnippets.org/snippets/302/
    """

    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes 2 arguments" % (bits[0])
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfLengthEqualNode(bits[1], bits[2], nodelist_true, nodelist_false)

class IfLengthEqualNode(Node):
    def __init__(self, listarg, numarg, nodelist_true, nodelist_false):
        self.listarg = listarg
        self.numarg = numarg
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def __repr__(self):
        return "<IfLengthEqualNode>"

    def render(self, context):
        try:
            list_val = resolve_variable(self.listarg, context)
        except VariableDoesNotExist:
            list_val = self.listarg
        try:
            num_val = resolve_variable(self.numarg, context)
        except VariableDoesNotExist:
            num_val = int(self.numarg)

        # logging.debug("list_val='%s'" % (list_val))
        # logging.debug("type(list_val)=%s" % (type(list_val)))
        # logging.debug("len(list_val)=%d" % (len(list_val)))
        # logging.debug("num_val=%d" % (num_val))

        if len(list_val) == num_val:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

iflengthequal = register.tag(iflengthequal)

def ifpackagefamily(parser, token):
    """
    Usage {% ifpackagefamily thing %}Only 1 member{% endifpackagefamily %}
    Convenience function when iterating through the list of Packages/
    PackageFamilies
    """

    bits = list(token.split_contents())
    if len(bits) != 2:
        raise TemplateSyntaxError, "%r takes 1 argument" % (bits[0])
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfPackageFamilyNode(bits[1], nodelist_true, nodelist_false)

class IfPackageFamilyNode(Node):
    def __init__(self, thingarg, nodelist_true, nodelist_false):
        self.thingarg = thingarg
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def __repr__(self):
        return "<IfPackageFamilyNode>"

    def render(self, context):
        try:
            thing_val = resolve_variable(self.thingarg, context)
        except VariableDoesNotExist:
            thing_val = self.thingarg

        # logging.debug("list_val='%s'" % (list_val))
        # logging.debug("type(list_val)=%s" % (type(list_val)))
        # logging.debug("len(list_val)=%d" % (len(list_val)))
        # logging.debug("num_val=%d" % (num_val))

        if hasattr(thing_val, "packages"):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
ifpackagefamily = register.tag(ifpackagefamily)

def ifindaterange(parser, token):
    """
    Usage:
    {% ifindaterange year month day startdate enddate%}yes{% endifindaterange %}
    startdate and enddate are yyyymmdd, the others are ints (or strings that
    can be converted to ints).
    """
    bits = list(token.split_contents())
    if len(bits) != 6:
        raise TemplateSyntaxError, "%r takes 5 arguments" % (bits[0])
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfInDateRangeNode(bits[1], bits[2], bits[3], bits[4], bits[5],
                               nodelist_true, nodelist_false)

class IfInDateRangeNode(Node):
    def __init__(self, year, month, day, startdate, enddate,
                 nodelist_true, nodelist_false):
        self.year = year
        self.month = month
        self.day = day
        self.startdate = startdate
        self.enddate = enddate
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def __repr__(self):
        return "<IfInDateRangeNode>"

    def render(self, context):
        try:
            year_val = resolve_variable(self.year, context)
        except VariableDoesNotExist:
            year_val = self.year
        try:
            month_val = resolve_variable(self.month, context)
        except VariableDoesNotExist:
            month_val = self.month
        try:
            day_val = resolve_variable(self.day, context)
        except VariableDoesNotExist:
            day_val = self.day
        try:
           start_val = resolve_variable(self.startdate, context)
        except VariableDoesNotExist:
           start_val = self.startdate
        try:
            end_val = resolve_variable(self.enddate, context)
        except VariableDoesNotExist:
            end_val = self.enddate

        yyyymmdd = "%04d%02d%02d" % (int(year_val), int(month_val), 
                                     int(day_val))
        start_val = str(start_val)
        end_val = str(end_val)

        if start_val <= yyyymmdd <= end_val:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
ifindaterange = register.tag(ifindaterange)
