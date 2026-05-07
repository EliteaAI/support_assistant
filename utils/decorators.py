from functools import wraps
from typing import Callable


def add_support_project_id(f: Callable) -> Callable:
    """
    Decorator to add support project_id to kwargs and ensure user enrollment.

    This mimics the @add_public_project_id pattern from elitea_core.
    It automatically:
    1. Gets the support project ID from module config/state
    2. Adds it to kwargs as 'project_id'
    3. Ensures the current user is enrolled in the support project
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        from tools import this, auth
        from pylon.core.tools import log

        try:
            module = this.for_module("support_assistant").module

            if not module.is_enabled:
                return {'error': 'Support Assistant not enabled'}, 503

            if not module.support_project_id:
                return {'error': 'Support Assistant project not initialized'}, 503

            # Get current user and ensure enrolled
            user_id = auth.current_user().get("id")
            module.ensure_user_enrolled(user_id)

            # Inject support project_id
            kwargs.update({'project_id': module.support_project_id})
            return f(*args, **kwargs)

        except Exception as e:
            log.error(f"@add_support_project_id failed: {e}", exc_info=True)
            return {'error': f'Support assistant error'}, 500

    return wrapper
