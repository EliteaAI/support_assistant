from flask import request
from tools import api_tools, auth, config as c

from ...utils.transforms import to_fe_config
from ...utils.decorators import add_support_project_id


class API(api_tools.APIBase):
    url_params = ['']

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.config.read"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": True},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": True},
        },
    })
    @api_tools.endpoint_metrics
    def get(self, project_id: int, **kwargs):
        """Get support assistant config for FE widget"""
        from tools import this
        module = this.for_module("support_assistant").module

        return to_fe_config(module.descriptor.config, module.is_enabled), 200

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.config.update"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": False, "viewer": False},
        },
    })
    @api_tools.endpoint_metrics
    def put(self, project_id: int, **kwargs):
        """Update support assistant config (admin only)"""
        from tools import this
        module = this.for_module("support_assistant").module

        data = request.json or {}

        if 'enabled' in data:
            module.descriptor.config['enabled'] = bool(data['enabled'])

        if 'agent_id' in data:
            module.descriptor.config['agent_id'] = data['agent_id']

        if 'agent_project_id' in data:
            module.descriptor.config['agent_project_id'] = data['agent_project_id']

        module.descriptor.config.save()

        return to_fe_config(module.descriptor.config, module.is_enabled), 200
