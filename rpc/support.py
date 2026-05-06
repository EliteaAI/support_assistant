from pylon.core.tools import web, log
from tools import auth


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

    @web.rpc("support_assistant_send_message", "support_send_message")
    def support_send_message(
        self,
        project_id: int,
        conversation_uuid: str,
        user_input: str,
        user_id: int,
        attachments: list = None,
    ) -> dict:
        """
        Send a message in a support conversation.
        Handles adding agent participant and calling chat_predict_sio.
        """
        from tools import this, rpc_tools

        module = this.for_module("support_assistant").module

        if not module.is_enabled:
            return {'success': False, 'error': 'Support Assistant not enabled'}

        agent_id = module.descriptor.config.get('agent_id')
        agent_project_id = module.descriptor.config.get('agent_project_id') or project_id

        if not agent_id:
            return {'success': False, 'error': 'Support agent not configured'}

        rpc = rpc_tools.RpcMixin().rpc

        conversation = rpc.timeout(2).chat_get_conversation_by_uuid_rpc(
            project_id=project_id,
            conversation_uuid=conversation_uuid,
            user_id=user_id,
            check_ownership=True,
        )

        if not conversation:
            return {'success': False, 'error': 'Conversation not found'}

        participant = rpc.timeout(2).chat_add_application_participant_rpc(
            project_id=project_id,
            conversation_id=conversation['id'],
            application_id=agent_id,
            application_project_id=agent_project_id,
        )

        if not participant:
            return {'success': False, 'error': 'Failed to add agent participant'}

        rpc.timeout(5).chat_predict_sio(
            sid=None,
            data={
                'project_id': project_id,
                'conversation_uuid': conversation_uuid,
                'participant_id': participant['id'],
                'user_input': user_input,
                'attachments_info': attachments or [],
            },
        )

        return {
            'success': True,
            'conversation_uuid': conversation_uuid,
        }
