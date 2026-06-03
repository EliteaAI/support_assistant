from tools import api_tools, auth, config as c, rpc_tools, serialize, register_openapi

from ...utils.decorators import add_support_project_id


class API(api_tools.APIBase):
    url_params = ['<string:conversation_uuid>']

    @register_openapi(
        name="Get Support Conversation",
        description="Get details of a support assistant conversation by UUID.",
        parameters=[
            {"name": "conversation_uuid", "in": "path", "schema": {"type": "string"},
             "description": "Conversation UUID."},
        ],
    )
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

        conversation_basic = rpc_tools.RpcMixin().rpc.timeout(2).chat_get_conversation_by_uuid_rpc(
            project_id=project_id,
            conversation_uuid=conversation_uuid,
            user_id=user_id,
            check_ownership=True,
        )

        if not conversation_basic:
            return {"error": "Conversation not found"}, 404

        conversation_details = rpc_tools.RpcMixin().rpc.timeout(5).chat_get_conversation_details(
            project_id=project_id,
            conversation_id=conversation_basic['id'],
            user_id=user_id,
            include_participants=True,
            include_message_groups=True,
        )

        if not conversation_details:
            return {"error": "Failed to load conversation details"}, 500

        return serialize(conversation_details), 200

    @register_openapi(
        name="Delete Support Conversation",
        description="Delete a support assistant conversation by UUID.",
        parameters=[
            {"name": "conversation_uuid", "in": "path", "schema": {"type": "string"},
             "description": "Conversation UUID."},
        ],
    )
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

        return serialize({"success": True}), 200
