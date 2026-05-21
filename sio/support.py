from pylon.core.tools import web, log
from tools import auth, db

from ..models.pd.support import SupportPredictPayload


def _emit_error(context, sid: str, message: str, code: str):
    context.sio.emit(
        'support_error',
        {'error': message, 'code': code},
        to=sid
    )


def _get_agent_llm_settings(project_id: int, agent_id: int) -> dict | None:
    """
    Extract LLM settings from the support agent's default version.
    Required for processing document attachments (non-image files).
    """
    try:
        from plugins.elitea_core.models.all import Application
        with db.get_session(project_id) as session:
            application = session.query(Application).filter(
                Application.id == agent_id
            ).first()
            if not application:
                log.warning(f"Support agent {agent_id} not found in project {project_id}")
                return None

            default_version = application.get_default_version()
            if not default_version:
                log.warning(f"No default version found for support agent {agent_id}")
                return None

            llm_settings = default_version.llm_settings
            if not llm_settings:
                log.warning(f"No LLM settings found for support agent {agent_id} version {default_version.id}")
                return None

            return llm_settings
    except Exception as e:
        log.error(f"Failed to get LLM settings for support agent: {e}")
        return None


class SIO:
    @web.sio("support_predict")
    def support_predict(self, sid: str, data: dict) -> None:
        """
        Handle support message prediction.

        Flow:
        1. Validate payload and user
        2. Get conversation by UUID and add application participant
        3. Delegate to chat_predict_sio RPC which handles:
           - Creating user message group
           - Emitting events to chat room
           - Triggering agent prediction

        Frontend should:
        - Join room using chat_enter_room with {project_id, conversation_id}
        - Listen for chat_predict events
        """
        from tools import this
        module = this.for_module("support_assistant").module

        if not module.is_enabled:
            _emit_error(self.context, sid, "Support Assistant not available", "SERVICE_UNAVAILABLE")
            return

        try:
            parsed = SupportPredictPayload.model_validate(data)
        except Exception as e:
            _emit_error(self.context, sid, str(e), "VALIDATION_ERROR")
            return

        current_user = auth.current_user(auth_data=auth.sio_users.get(sid))
        if not current_user:
            _emit_error(self.context, sid, "Unauthorized", "UNAUTHORIZED")
            return

        user_id = current_user['id']
        module.ensure_user_enrolled(user_id)

        agent_id = module.descriptor.config.get('agent_id')
        if not agent_id:
            _emit_error(self.context, sid, "Support agent not configured", "NOT_CONFIGURED")
            return

        agent_project_id = module.descriptor.config.get('agent_project_id') or module.support_project_id

        conversation = self.context.rpc_manager.call.chat_get_conversation_by_uuid_rpc(
            project_id=module.support_project_id,
            conversation_uuid=parsed.conversation_uuid,
            user_id=user_id,
            check_ownership=True,
        )

        if not conversation:
            _emit_error(self.context, sid, "Conversation not found", "NOT_FOUND")
            return

        participant = self.context.rpc_manager.call.chat_add_application_participant_rpc(
            project_id=module.support_project_id,
            conversation_id=conversation['id'],
            application_id=agent_id,
            application_project_id=agent_project_id,
        )

        if not participant:
            _emit_error(self.context, sid, "Failed to setup support agent", "AGENT_ERROR")
            return

        # Extract LLM settings from the support agent for document attachment processing
        llm_settings = _get_agent_llm_settings(agent_project_id, agent_id)

        predict_payload = {
            'project_id': module.support_project_id,
            'conversation_uuid': parsed.conversation_uuid,
            'participant_id': participant['id'],
            'user_input': parsed.content,
            'attachments_info': [{'filepath': fp} for fp in (parsed.attachments or [])],
            'runtime_context': parsed.support_assistant_context.model_dump() if parsed.support_assistant_context else None,
            'llm_settings': llm_settings,
            'question_id': parsed.question_id,
        }

        self.context.rpc_manager.call.chat_predict_sio(
            sid=sid,
            data=predict_payload
        )


