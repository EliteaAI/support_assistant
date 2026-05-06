from flask import request
from tools import api_tools, auth, config as c, serialize

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
        config: dict = module.descriptor.config

        return serialize({
            'enabled': True,
            'title': config.get('assistant_name', 'ELITEA Support'),
            'welcome_message': config.get('welcome_message', ''),
            'placeholder': config.get('placeholder', 'Type a message...'),
            'support_project_id': module.support_project_id,
        }), 200

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
        config: dict = module.descriptor.config

        return serialize({
            'enabled': True,
            'title': config.get('assistant_name', 'ELITEA Support'),
            'welcome_message': config.get('welcome_message', ''),
            'placeholder': config.get('placeholder', 'Type a message...'),
        }), 200
