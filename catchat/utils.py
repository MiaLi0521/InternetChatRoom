from flask import flash
from bleach import clean, linkify
from markdown import markdown


def to_html(raw):
    allowed_tags = ['div', 'a', 'abbr', 'b', 'br', 'blockquote', 'code', 'del', 'em', 'img', 'p', 'pre', 'strong',
                    'span', 'ul', 'li', 'ol']
    allowed_attributes = {'a': ['href', 'title'], 'abbr': ['title'], 'acronym': ['title'], 'div': ['class'],
                          'span': ['class']}
    html = markdown(
        raw,
        output_format='html',
        extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite'])
    clean_html = clean(html, tags=allowed_tags, attributes=allowed_attributes)
    return linkify(clean_html)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the {} field - {}".format(getattr(form, field).label.text, error))

