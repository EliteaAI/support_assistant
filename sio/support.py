from pylon.core.tools import web, log
from tools import auth, db

from ..models.pd.support import SupportPredictPayload


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
            self._emit_error(sid, "Support Assistant not available", "SERVICE_UNAVAILABLE")
            return

        try:
            parsed = SupportPredictPayload.model_validate(data)
        except Exception as e:
            self._emit_error(sid, str(e), "VALIDATION_ERROR")
            return

        current_user = auth.current_user(auth_data=auth.sio_users.get(sid))
        if not current_user:
            self._emit_error(sid, "Unauthorized", "UNAUTHORIZED")
            return

        user_id = current_user['id']
        module.ensure_user_enrolled(user_id)

        agent_id = module.descriptor.config.get('agent_id')
        if not agent_id:
            self._emit_error(sid, "Support agent not configured", "NOT_CONFIGURED")
            return

        agent_project_id = module.descriptor.config.get('agent_project_id') or module.support_project_id

        conversation = self.context.rpc_manager.call.chat_get_conversation_by_uuid_rpc(
            project_id=module.support_project_id,
            conversation_uuid=parsed.conversation_uuid,
            user_id=user_id,
            check_ownership=True,
        )

        if not conversation:
            self._emit_error(sid, "Conversation not found", "NOT_FOUND")
            return

        participant = self.context.rpc_manager.call.chat_add_application_participant_rpc(
            project_id=module.support_project_id,
            conversation_id=conversation['id'],
            application_id=agent_id,
            application_project_id=agent_project_id,
        )

        if not participant:
            self._emit_error(sid, "Failed to setup support agent", "AGENT_ERROR")
            return

        predict_payload = {
            'project_id': module.support_project_id,
            'conversation_uuid': parsed.conversation_uuid,
            'participant_id': participant['id'],
            'user_input': parsed.content,
            'attachments_info': [{'filepath': fp} for fp in (parsed.attachments or [])],
            'runtime_context': parsed.support_assistant_context.model_dump() if parsed.support_assistant_context else None,
        }

        self.context.rpc_manager.call.chat_predict_sio(
            sid=sid,
            data=predict_payload
        )

    def _emit_error(self, sid: str, message: str, code: str):
        self.context.sio.emit(
            'support_error',
            {'error': message, 'code': code},
            to=sid
        )
