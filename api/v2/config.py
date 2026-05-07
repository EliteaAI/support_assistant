from queue import Empty

from flask import request
from tools import api_tools, auth, config as c, serialize, rpc_tools

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

        current_user = auth.current_user()
        user_id = current_user.get('id')
        user_name = current_user.get('name', '')
        user_avatar = None

        if user_id:
            try:
                social_data = rpc_tools.RpcMixin().rpc.timeout(2).social_get_user(user_id)
                user_avatar = social_data.get('avatar') if social_data else None
            except (Empty, KeyError):
                pass

        return serialize({
            'enabled': True,
            'title': config.get('assistant_name', 'ELITEA Support'),
            'welcome_message': config.get('welcome_message', ''),
            'placeholder': config.get('placeholder', 'Type a message...'),
            'support_project_id': module.support_project_id,
            'agent_id': config.get('agent_id', ''),
            'user': {
                'id': user_id,
                'name': user_name,
                'avatar': user_avatar,
            },
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
