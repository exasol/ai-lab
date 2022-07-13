import jinja2


def render_template(template: str, **kwargs):
    env = jinja2.Environment(loader=jinja2.PackageLoader("exasol_script_languages_developer_sandbox"),
                             autoescape=jinja2.select_autoescape(), keep_trailing_newline=True)
    t = env.get_template(template)
    return t.render(**kwargs)
