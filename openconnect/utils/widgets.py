from django.utils.encoding import StrAndUnicode, force_unicode
from django.forms.widgets import Widget
from django import forms
from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.contrib.localflavor.us.forms import USStateSelect
from django.forms.util import flatatt
from django.utils.html import conditional_escape


class DojoForm(forms.Form):
    legend = ""
    def as_dojoform(self):
        try:
            return self._as_dojoform()
        except Exception, ex:
            import traceback
            import sys
            print "<PRE>"
            traceback.print_exc()
            print "/PRE>"
            return "<PRE>" + traceback.format_exc() + "</PRE>"
            
    def _as_dojoform(self):
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []
        output.append("<fieldset>")
        output.append("<legend>%s</legend>"%force_unicode(self.legend))
        output.append("<ol>")
        
        for name, field in self.fields.items():
            bf = forms.forms.BoundField(self, field, name)
            elist = [escape(force_unicode(error)) for error in bf.errors]
            bf_errors = self.error_class(elist) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend(['(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                output.append("<li>");
                label_content = []
                label_content.append(force_unicode(bf.label))
                if bf.errors:
                    label_content.append("<strong>")
                    label_content.append(", ".join(bf_errors))
                    label_content.append("</strong>")
                    label_content.append("<em>")
                    label_content.append("<img src='/its/testmgmt/static/images/stop.png' alt='" + _("Input Error") + "' />")
                    label_content.append("</em>")
                    
                if field.required:
                    label_content.append("<em>");
                    label_content.append("<img src='/its/testmgmt/static/images/sphere.png' alt='" + _("Input Required") + "' />")
                    label_content.append("</em>")
                output.append(bf.label_tag("\n".join(label_content)))
                output.append(force_unicode(bf))
                output.append("</li>")

        output.append("</ol>")

        if top_errors:
            output.insert(0, top_errors)
        
        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                output.append(str_hidden)
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)

        output.append("</fieldset>")
        return mark_safe(u'\n'.join(output))



class DojoNumberSpinner(forms.TextInput):
    def __init__(self, *args, **kwargs):
        constraints = []
        for constraint in ["min", "max", "places"]:
            value = kwargs.pop(constraint, None)
            if value is not None:
                constraints.append(constraint + ":" + unicode(value))

        kwargs.setdefault('attrs', {}).update({'dojoType': "dijit.form.NumberSpinner",
                                               'required': kwargs.pop('required', False),
                                               'constraints': "{" + ",".join(constraints) + "}",
                                               'isValid': 'customIsValid',
                                              })
        attrs = kwargs['attrs']
        if kwargs.get('promptMessage', None) is not None:
            attrs['promptMessage'] =  kwargs.pop('promptMessage')    
        super(DojoNumberSpinner, self).__init__(*args, **kwargs)                                      

class DojoTextareaWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'dojoType': "dijit.form.Textarea",
                                              'required': kwargs.pop('required', False),
                                               'isValid': 'customIsValid',
                                              })
        attrs = kwargs['attrs']
        
        if kwargs.get('promptMessage', None) is not None:
            attrs['promptMessage'] =  kwargs.pop('promptMessage')
            
        super(DojoTextareaWidget, self).__init__(*args, **kwargs)
        
class DojoTextWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'dojoType': "dijit.form.ValidationTextBox",
                                               'isValid': 'customIsValid',
                                               'required': kwargs.pop('required', False),
                                              })
        attrs = kwargs['attrs']
        
        if kwargs.get('promptMessage', None) is not None:
            attrs['promptMessage'] =  kwargs.pop('promptMessage')
            
        super(DojoTextWidget, self).__init__(*args, **kwargs)


class DojoRegexTextWidget(DojoTextWidget):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'dojoType': "dijit.form.ValidationTextBox",
                                               'regExp': kwargs.pop('regExp', '.*'), 
                                               'invalidMessage': kwargs.pop('invalidMessage', _('Input not valid')),
                                               'isValid': 'customIsValid',
                                               })
        super(DojoRegexTextWidget, self).__init__(*args, **kwargs)
        
class DojoFilterSelectWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'dojoType': "dijit.form.FilteringSelect",
                                               'isValid': 'customIsValid',
                                               'required': kwargs.pop('required', False),
                                              })            
        super(DojoFilterSelectWidget, self).__init__(*args, **kwargs)

class DojoComboBoxWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'dojoType': "dijit.form.ComboBox",
                                               'required': kwargs.pop('required', False),
                                              })            
        super(DojoComboBoxWidget, self).__init__(*args, **kwargs)


class DojoStateSelectWidget(USStateSelect):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'dojoType': "dijit.form.FilteringSelect",
                                               'required': kwargs.pop('required', False),
                                               'isValid': 'customIsValid',
                                               })            
        super(DojoStateSelectWidget, self).__init__(*args, **kwargs)


class DojoJsonSelectWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'dojoType': "dijit.form.FilteringSelect",
                                               'store': kwargs.pop('store', 'No Such Store'),
                                               'searchAttr': kwargs.pop('searchAttr', 'No Such Attribute'),
                                               'isValid': 'customIsValid',
                                               'autocomplete': kwargs.pop('autocomplete', False)})

        attrs = kwargs['attrs']
        
        if kwargs.get('promptMessage', None) is not None:
            attrs['promptMessage'] =  kwargs.pop('promptMessage')
        
        super(DojoJsonSelectWidget, self).__init__(*args, **kwargs)

class DojoDivWidget(Widget):
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        value = force_unicode(value)
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<input type="hidden" name="%s" id="%s_hidden" value="%s"><div class="dijit dijitTextBox" dojoType="dijit.InlineEditBox" editor="dijit.Editor" renderAsHtml="true" autoSave="false" onChange="messageHandler(this.id, arguments[0])"%s>%s</div>' % (final_attrs['name'],
                                                                        final_attrs['id'],
                                                                        force_unicode(value),
                                                                        flatatt(final_attrs),
                                                                        force_unicode(value)
                                                                        )
                        )

class DivWidget(Widget):
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        value = force_unicode(value)
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<div%s>%s</div>' % (flatatt(final_attrs), force_unicode(value)))
