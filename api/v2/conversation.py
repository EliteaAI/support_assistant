from tools import api_tools, auth, config as c, rpc_tools

from ...utils.decorators import add_support_project_id


class API(api_tools.APIBase):
    url_params = ['<string:conversation_uuid>']

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.conversations.details"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": True},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": True},
        },
    })
    @api_tools.endpoint_metrics
    def get(self, project_id: int, conversation_uuid: str, **kwargs):
        user_id = auth.current_user().get("id")

        conversation = rpc_tools.RpcMixin().rpc.timeout(2).chat_get_conversation_by_uuid_rpc(
            project_id=project_id,
            conversation_uuid=conversation_uuid,
            user_id=user_id,
            check_ownership=True,
        )

        if not conversation:
            return {"error": "Conversation not found"}, 404

        return conversation, 200

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.conversations.delete"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": True},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": True},
        },
    })
    @api_tools.endpoint_metrics
    def delete(self, project_id: int, conversation_uuid: str, **kwargs):
        user_id = auth.current_user().get("id")

        result = rpc_tools.RpcMixin().rpc.timeout(2).chat_delete_conversation_rpc(
            project_id=project_id,
            conversation_uuid=conversation_uuid,
            user_id=user_id,
            check_ownership=True,
        )

        if not result.get('success'):
            error = result.get('error', 'Conversation not found')
            return {"error": error}, 404

        return {"success": True}, 200
