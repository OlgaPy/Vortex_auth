import jinja2

templates = jinja2.Environment(
    loader=jinja2.PackageLoader("app", "templates"),
    autoescape=jinja2.select_autoescape(["html", "txt"]),
)
