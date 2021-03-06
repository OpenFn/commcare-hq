import re
from contextlib import contextmanager

from crispy_forms.bootstrap import AccordionGroup, InlineField, FormActions as OriginalFormActions
from crispy_forms.layout import LayoutObject, MultiField, Field as OldField
from crispy_forms.utils import render_field, get_template_pack, flatatt
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext

from corehq.util.soft_assert import soft_assert

_soft_assert_dict = soft_assert(
    to='{}@{}'.format('npellegrino', 'dimagi.com'),
    exponential_backoff=False,
)


def _get_dict_from_context(context):
    if isinstance(context, RequestContext):
        return context.flatten()
    else:
        # TODO - remove by Nov 1 2017 if soft assert is never sent
        _soft_assert_dict(False, "context is type %s" % str(type(context)))
        return context


class BootstrapMultiField(MultiField):
    template = "hqwebapp/crispy/layout/multifield.html"
    field_template = "hqwebapp/crispy/field/multifield.html"

    def __init__(self, *args, **kwargs):
        super(BootstrapMultiField, self).__init__(*args, **kwargs)
        self.help_bubble_text = None
        if 'help_bubble_text' in kwargs:
            self.help_bubble_text = kwargs.pop('help_bubble_text')

    def render(self, form, form_style, context, template_pack=None):
        template_pack = template_pack or get_template_pack()
        fields_output = u''
        for field in self.fields:
            fields_output += render_field(
                field, form, form_style, context,
                self.field_template, self.label_class, layout_object=self,
                template_pack=template_pack
            )

        errors = self._get_errors(form, self.fields)
        if len(errors) > 0:
            self.css_class += " error"

        context.update({
            'multifield': self,
            'fields_output': fields_output,
            'error_list': errors,
            'help_bubble_text': self.help_bubble_text,
        })
        return render_to_string(self.template, _get_dict_from_context(context))

    def _get_errors(self, form, fields):
        errors = []
        for field in fields:
            if isinstance(field, OldField) or issubclass(field.__class__, OldField):
                fname = field.fields[0]
                error = form[fname].errors
                if error:
                    errors.append(error)
            else:
                try:
                    errors.extend(self._get_errors(form, field.fields))
                except AttributeError:
                    pass
        return errors


class HiddenFieldWithErrors(OldField):
    template = "hqwebapp/crispy/field/hidden_with_errors.html"


class TextField(OldField):
    """
    Layout object.
    Contains text specified in place of the field's normal input.
    """
    template = "hqwebapp/crispy/field/field_with_text.html"

    def __init__(self, field_name, text, *args, **kwargs):
        self.text = text
        super(TextField, self).__init__(field_name, *args, **kwargs)

    def render(self, form, form_style, context, template_pack=None):
        template_pack = template_pack or get_template_pack()
        context.update({
            'field_text': self.text,
        })
        return super(TextField, self).render(form, form_style, context, template_pack=template_pack)


class InlineColumnField(InlineField):

    def __init__(self, *args, **kwargs):
        self.block_css_class = kwargs.pop('block_css_class')
        super(InlineColumnField, self).__init__(*args, **kwargs)

    def render(self, form, form_style, context, template_pack=None):
        template_pack = template_pack or get_template_pack()
        context.update({
            'block_css_class': self.block_css_class,
        })
        return super(InlineColumnField, self).render(form, form_style, context, template_pack=template_pack)


class ErrorsOnlyField(OldField):
    template = 'hqwebapp/crispy/field/errors_only_field.html'


def _get_offsets(context):
    label_class = context.get('label_class', '')
    return re.sub(r'(xs|sm|md|lg)-', '\g<1>-offset-', label_class)


class FormActions(OriginalFormActions):
    """Overrides the crispy forms template to include the gray box around
    the form actions.
    """
    template = 'hqwebapp/crispy/form_actions.html'

    def render(self, form, form_style, context, template_pack=None):
        template_pack = template_pack or get_template_pack()
        html = u''
        for field in self.fields:
            html += render_field(
                field, form, form_style, context,
                template_pack=template_pack,
            )
        offsets = _get_offsets(context)
        return render_to_string(self.template, {
            'formactions': self,
            'fields_output': html,
            'offsets': offsets,
            'field_class': context.get('field_class', '')
        })


class Field(OldField):
    """Overrides the logic behind choosing the offset class for the field to
    actually be responsive (col-lg-offset-*, col-md-offset-*, etc). Also includes
    support for static controls.
    todo since we forked crispy forms, this class is no longer necessary.
    http://manage.dimagi.com/default.asp?186372
    """
    template = 'hqwebapp/crispy/field.html'

    def __init__(self, *args, **kwargs):
        self.is_static = False
        if 'is_static' in kwargs:
            self.is_static = kwargs.pop('is_static')
        super(Field, self).__init__(*args, **kwargs)

    def render(self, form, form_style, context, template_pack=None):
        template_pack = template_pack or get_template_pack()
        offsets = _get_offsets(context)
        context.update({
            'offsets': offsets,
        })
        return super(Field, self).render(form, form_style, context, template_pack)


class StaticField(LayoutObject):
    template = 'hqwebapp/crispy/static_field.html'

    def __init__(self, field_label, field_value):
        self.field_label = field_label
        self.field_value = field_value

    def render(self, form, form_style, context, template_pack=None):
        template_pack = template_pack or get_template_pack()
        context.update({
            'field_label': self.field_label,
            'field_value': self.field_value,
        })
        return render_to_string(self.template, _get_dict_from_context(context))


class FormStepNumber(LayoutObject):
    template = 'hqwebapp/crispy/form_step_number.html'

    def __init__(self, step_num, total_steps):
        self.step_label = ugettext("Step {} of {}".format(step_num, total_steps))

    def render(self, form, form_style, context, template_pack=None):
        context.update({
            'step_label': self.step_label,
        })

        return render_to_string(self.template, _get_dict_from_context(context))


class ValidationMessage(LayoutObject):
    template = 'hqwebapp/crispy/validation_message.html'

    def __init__(self, ko_observable):
        self.ko_observable = ko_observable

    def render(self, form, form_style, context, template_pack=None):
        context.update({
            'ko_observable': self.ko_observable,
        })

        return render_to_string(self.template, _get_dict_from_context(context))


@contextmanager
def edited_classes(context, label_class, field_class):
    original_label_class = context.get('label_class')
    original_field_class = context.get('field_class')
    try:
        context['label_class'] = label_class or context.get('label_class')
        context['field_class'] = field_class or context.get('field_class')
        yield
    finally:
        context['label_class'] = original_label_class
        context['field_class'] = original_field_class


class B3MultiField(LayoutObject):
    template = 'hqwebapp/crispy/multi_field.html'

    def __init__(self, field_label, *fields, **kwargs):
        self.fields = list(fields)
        self.label_html = field_label
        self.css_class = kwargs.pop('css_class', '')
        self.css_id = kwargs.pop('css_id', '')
        self.field_class = kwargs.pop('field_class', None)
        self.label_class = kwargs.pop('label_class', None)
        self.help_bubble_text = kwargs.pop('help_bubble_text', '')
        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, template_pack=None):
        template_pack = template_pack or get_template_pack()
        html = u''

        errors = self._get_errors(form, self.fields)
        if len(errors) > 0:
            self.css_class += " has-error"

        for field in self.fields:
            html += render_field(field, form, form_style, context, template_pack=template_pack)
        context.update({
            'label_html': mark_safe(self.label_html),
            'field_html': mark_safe(html),
            'multifield': self,
            'error_list': errors,
            'help_bubble_text': self.help_bubble_text,
        })

        context_dict = _get_dict_from_context(context)

        if not (self.field_class or self.label_class):
            return render_to_string(self.template, context_dict)

        with edited_classes(context, self.label_class, self.field_class):
            rendered_view = render_to_string(self.template, context_dict)
        return rendered_view

    def _get_errors(self, form, fields):
        errors = []
        for field in fields:
            if isinstance(field, OldField) or issubclass(field.__class__, OldField):
                fname = field.fields[0]
                if fname not in form.fields:
                    continue
                error_list = form[fname].errors
                if error_list:
                    errors.extend(error_list)
            else:
                try:
                    errors.extend(self._get_errors(form, field.fields))
                except AttributeError:
                    pass
        return errors


class MultiInlineField(InlineField):
    """
    An InlineField to be used within a B3MultiField.

    (Bootstrap 3 Crispy's InlineField adds the form-group class to
    the field's containing div, which is redundant because
    B3MultiField adds form-group at a higher level, and that makes
    the field not render properly.)
    """
    template = 'hqwebapp/crispy/multi_inline_field.html'


class CrispyTemplate(object):

    def __init__(self, template, context):
        self.template = template
        self.context = context

    def render(self, form, form_style, context, template_pack=None):
        context.update(self.context)
        return render_to_string(self.template, _get_dict_from_context(context))


class FieldWithHelpBubble(Field):
    template = "hqwebapp/crispy/field_with_help_bubble.html"

    def __init__(self, *args, **kwargs):
        super(FieldWithHelpBubble, self).__init__(*args, **kwargs)
        self.help_bubble_text = kwargs.pop('help_bubble_text')

    def render(self, form, form_style, context, template_pack=None):
        template_pack = template_pack or get_template_pack()
        context.update({
            'help_bubble_text': self.help_bubble_text,
        })
        return super(FieldWithHelpBubble, self).render(form, form_style, context, template_pack=template_pack)


class LinkButton(LayoutObject):
    template = "hqwebapp/crispy/link_button.html"

    def __init__(self, button_text, button_url, **kwargs):
        self.button_text = button_text
        self.button_url = button_url

        if not hasattr(self, 'attrs'):
            self.attrs = {}

        if 'css_class' in kwargs:
            if 'class' in self.attrs:
                self.attrs['class'] += " %s" % kwargs.pop('css_class')
            else:
                self.attrs['class'] = kwargs.pop('css_class')

    def render(self, form, form_style, context, template_pack=None):
        context.update({
            'button_text': self.button_text,
            'button_url': self.button_url,
            'button_attrs': flatatt(self.attrs if isinstance(self.attrs, dict) else {}),
        })
        return render_to_string(self.template, _get_dict_from_context(context))


class B3TextField(OldField):

    def __init__(self, field_name, text, *args, **kwargs):
        self.text = text
        super(B3TextField, self).__init__(field_name, *args, **kwargs)
        self.template = 'hqwebapp/crispy/text_field.html'

    def render(self, form, form_style, context, template_pack=None):
        context.update({
            'field_text': self.text,
        })
        if hasattr(self, 'wrapper_class'):
            context['wrapper_class'] = self.wrapper_class

        html = ''
        for field in self.fields:
            html += render_field(field, form, form_style, context,
                                 template=self.template, attrs=self.attrs,
                                 template_pack=template_pack)
        return html


class FieldsetAccordionGroup(AccordionGroup):
    template = "hqwebapp/crispy/accordion_group.html"


class B3HiddenFieldWithErrors(Field):
    template = "hqwebapp/crispy/hidden_with_errors.html"
