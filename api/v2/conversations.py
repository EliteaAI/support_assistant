from flask import request
from pylon.core.tools import log
from tools import api_tools, auth, config as c, rpc_tools

from ...models.pd.conversation import ConversationCreateRequest
from ...utils.transforms import to_fe_conversation
from ...utils.decorators import add_support_project_id


class API(api_tools.APIBase):
    url_params = ['']

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.conversations.list"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": True},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": True},
        },
    })
    @api_tools.endpoint_metrics
    def get(self, project_id: int, **kwargs):
        user_id = auth.current_user().get("id")
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)

        result = rpc_tools.RpcMixin().rpc.timeout(5).chat_list_conversations_rpc(
            project_id=project_id,
            user_id=user_id,
            source='support',
            include_hidden=True,
            limit=limit,
            offset=offset,
            sort_by='created_at',
            sort_order='desc',
        )

        items = [to_fe_conversation(conv) for conv in result.get('rows', [])]
        return {"items": items, "total": result.get('total', 0)}, 200

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.conversations.create"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": True},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": True},
        },
    })
    @api_tools.endpoint_metrics
    def post(self, project_id: int, **kwargs):
        user_id = auth.current_user().get("id")

        try:
            data = ConversationCreateRequest(**request.json) if request.json else ConversationCreateRequest()
        except Exception as e:
            return {"error": str(e)}, 400

        result = rpc_tools.RpcMixin().rpc.timeout(2).chat_create_conversation_rpc(
            project_id=project_id,
            user_id=user_id,
            name=data.name or "Support Chat",
            source='support',
            is_private=True,
            meta={
                'is_hidden': True,
                'conversation_type': 'support',
            },
        )

        return to_fe_conversation(result), 201
