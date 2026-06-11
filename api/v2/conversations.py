from flask import request
from pylon.core.tools import log
from tools import api_tools, auth, config as c, rpc_tools, register_openapi, serialize
from ...models.pd.conversation import ConversationCreateRequest
from ...utils.decorators import add_support_project_id


class API(api_tools.APIBase):
    url_params = ['']

    @register_openapi(
        name="List Support Conversations",
        description="List support assistant conversations for the current user with pagination and search.",
        parameters=[
            {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20},
             "description": "Number of conversations to return."},
            {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0},
             "description": "Pagination offset."},
            {"name": "q", "in": "query", "schema": {"type": "string"},
             "description": "Search query string."},
            {"name": "sort_by", "in": "query", "schema": {"type": "string", "default": "created_at"},
             "description": "Field to sort by."},
            {"name": "sort_order", "in": "query", "schema": {"type": "string", "default": "desc"},
             "description": "Sort order (asc or desc)."},
        ],
    )
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

        # Pagination
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)

        # Search
        query = request.args.get('q', default=None, type=str)

        # Sorting
        sort_by = request.args.get('sort_by', default='created_at', type=str)
        sort_order = request.args.get('sort_order', default='desc', type=str)

        result = rpc_tools.RpcMixin().rpc.timeout(5).chat_list_conversations_rpc(
            project_id=project_id,
            user_id=user_id,
            source='support',
            include_hidden=True,
            query=query,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return serialize({
            "items": result.get('rows', []),
            "total": result.get('total', 0),
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < result.get('total', 0),
        }), 200

    @register_openapi(
        name="Create Support Conversation",
        description="Create a new support assistant conversation.",
        request_body=ConversationCreateRequest,
    )
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
            name=data.name or "New conversation",
            source='support',
            is_private=True,
            meta={
                'is_hidden': True,
                'conversation_type': 'support',
                'internal_tools': ['internal_mcp'],
            },
        )

        return serialize(result), 201
