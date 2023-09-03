from jinja2 import TemplateNotFound

from app.core.common import templates
from app.schemas.email_schema import EmailContents


async def get_email_contents(email_type: str, context: dict = None) -> EmailContents:
    """Based on ``email_type`` render template with the same name, passing ``context``."""
    context = context or {}
    subject = templates.get_template(f"email/{email_type}.subject.txt").render(
        **context
    )
    message = templates.get_template(f"email/{email_type}.txt").render(**context)
    try:
        html_message = templates.get_template(f"email/{email_type}.html").render(
            **context
        )
    except TemplateNotFound:
        html_message = None

    return EmailContents(
        subject=subject,
        message=message,
        html_message=html_message or None,
    )
