from pylon.core.tools import web, log


class RPC:
    @web.rpc("support_assistant_get_config", "support_get_config")
    def support_get_config(self, user_id: int | None = None) -> dict:
        """
        Get support assistant configuration for FE.
        Returns enabled status and feature flags.
        """
        from tools import this
        module = this.for_module("support_assistant").module

        config = {
            'enabled': module.is_enabled,
            'project_id': module.support_project_id,
        }

        if module.is_enabled and module.support_project_id:
            config['agent_configured'] = bool(
                module.descriptor.config.get('agent_id')
            )

        return config

    @web.rpc("support_assistant_ensure_enrolled", "support_ensure_enrolled")
    def support_ensure_enrolled(self, user_id: int) -> dict:
        """
        Ensure user is enrolled in support project.
        Called lazily on first support interaction.
        """
        from tools import this
        module = this.for_module("support_assistant").module

        if not module.is_enabled:
            return {'success': False, 'error': 'Support Assistant not enabled'}

        if not module.support_project_id:
            return {'success': False, 'error': 'Support project not configured'}

        success = module.ensure_user_enrolled(user_id)
        return {
            'success': success,
            'project_id': module.support_project_id if success else None,
        }
