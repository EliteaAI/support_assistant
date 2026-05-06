from pylon.core.tools import web, log
from tools import auth

from ..models.pd.support import SupportPredictPayload
from ..utils.participant_utils import get_or_create_application_participant


def get_event_room(prefix: str, conversation_uuid: str) -> str:
    return f"{prefix}_{conversation_uuid}"


class SIO:
    @web.sio("support_enter_room")
    def support_enter_room(self, sid: str, data: dict) -> None:
        """Join support conversation room"""
        conversation_uuid = data.get('conversation_uuid')
        if not conversation_uuid:
            return

        room = get_event_room('support', conversation_uuid)
        self.context.sio.enter_room(sid, room)
        log.info(f"Socket {sid} joined support room {room}")

    @web.sio("support_leave_room")
    def support_leave_room(self, sid: str, data: dict) -> None:
        """Leave support conversation room"""
        conversation_uuid = data.get('conversation_uuid')
        if not conversation_uuid:
            return

        room = get_event_room('support', conversation_uuid)
        self.context.sio.leave_room(sid, room)

    @web.sio("support_predict")
    def support_predict(self, sid: str, data: dict) -> None:
        """Handle support message - delegates to chat_predict_sio"""
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

        participant = get_or_create_application_participant(
            project_id=module.support_project_id,
            application_id=agent_id,
            application_project_id=agent_project_id,
        )

        predict_payload = {
            'project_id': module.support_project_id,
            'conversation_uuid': parsed.conversation_uuid,
            'participant_id': participant['id'],
            'content': parsed.content,
            'attachments_info': parsed.attachments,
            'stream_event': 'support_predict',
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
