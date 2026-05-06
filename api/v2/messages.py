from flask import request
from tools import api_tools, auth, config as c, rpc_tools

from ...models.pd.message import MessageCreateRequest
from ...utils.decorators import add_support_project_id


class API(api_tools.APIBase):
    url_params = ['<string:conversation_uuid>']

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.messages.create"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": True},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": True},
        },
    })
    @api_tools.endpoint_metrics
    def post(self, project_id: int, conversation_uuid: str, **kwargs):
        user_id = auth.current_user().get("id")

        try:
            data = MessageCreateRequest(**request.json)
        except Exception as e:
            return {"error": str(e)}, 400

        result = rpc_tools.RpcMixin().rpc.timeout(10).support_assistant_send_message(
            project_id=project_id,
            conversation_uuid=conversation_uuid,
            user_input=data.content,
            user_id=user_id,
            attachments=data.attachments,
        )

        if not result.get('success'):
            error = result.get('error', 'Failed to send message')
            return {"error": error}, 400

        return {
            "status": "queued",
            "conversation_uuid": conversation_uuid,
        }, 202
