from .warning import template_warning
from .info import template_info
from .success import template_success
from .alert import template_alert
from .status import template_status
from .simple import template_simple
from .html import template_html
from .message import template_message

TEMPLATES = {
    "warning": template_warning,
    "info": template_info,
    "success": template_success,
    "alert": template_alert,
    "status": template_status,
    "simple": template_simple,
    "html": template_html,
    "message": template_message
}
