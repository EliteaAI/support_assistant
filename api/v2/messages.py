from tools import api_tools, auth, config as c, rpc_tools, serialize

from ...utils.decorators import add_support_project_id


class API(api_tools.APIBase):
    url_params = ['<string:conversation_uuid>']

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.messages.delete"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": True},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": True},
        },
    })
    @api_tools.endpoint_metrics
    def delete(self, project_id: int, conversation_uuid: str, **kwargs):
        """Clear all messages from a conversation while keeping the conversation."""
        user_id = auth.current_user().get("id")

        conversation = rpc_tools.RpcMixin().rpc.timeout(2).chat_get_conversation_by_uuid_rpc(
            project_id=project_id,
            conversation_uuid=conversation_uuid,
            user_id=user_id,
            check_ownership=True,
        )

        if not conversation:
            return {"error": "Conversation not found"}, 404

        result = rpc_tools.RpcMixin().rpc.timeout(5).chat_delete_all_messages_rpc(
            project_id=project_id,
            conversation_id=conversation['id'],
            user_id=user_id,
        )

        if not result.get('success'):
            error = result.get('error', 'Failed to clear messages')
            return {"error": error}, 400

        return serialize({"success": True}), 200
