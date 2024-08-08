import jinja2
from jinja2 import StrictUndefined


def render_template(template: str, **kwargs):
    env = jinja2.Environment(loader=jinja2.PackageLoader("exasol.ds.sandbox"),
                             autoescape=jinja2.select_autoescape(), keep_trailing_newline=True,
                             undefined=StrictUndefined)
    t = env.get_template(template)
    return t.render(**kwargs)


class TemplateRenderer:
    def render(self, template: str, **kwargs):
        return render_template(template, **kwargs)
