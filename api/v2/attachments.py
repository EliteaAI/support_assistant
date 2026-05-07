from flask import request
from werkzeug.datastructures import FileStorage
from tools import api_tools, auth, config as c, rpc_tools, serialize

from ...utils.decorators import add_support_project_id


class API(api_tools.APIBase):
    url_params = ['<string:conversation_uuid>', 'attachments']

    @add_support_project_id
    @auth.decorators.check_api({
        "permissions": ["models.support_assistant.attachments.create"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": True},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": True},
        },
    })
    @api_tools.endpoint_metrics
    def post(self, project_id: int, conversation_uuid: str, **kwargs):
        """Upload file attachments to a support conversation."""
        user_id = auth.current_user().get("id")

        conversation = rpc_tools.RpcMixin().rpc.timeout(2).chat_get_conversation_by_uuid_rpc(
            project_id=project_id,
            conversation_uuid=conversation_uuid,
            user_id=user_id,
            check_ownership=True,
        )

        if not conversation:
            return {"error": "Conversation not found"}, 404

        overwrite = bool(request.form.get("overwrite", 0, type=int))

        # Check if this is a chunked upload request
        file_id = request.form.get("file_id")
        chunk_index = request.form.get("chunk_index")
        total_chunks = request.form.get("total_chunks")
        file_name = request.form.get("file_name")

        if all([file_id, chunk_index is not None, total_chunks, file_name]):
            chunk_file = request.files.get("file")
            if not chunk_file:
                return {"error": "No chunk file provided"}, 400

            chunk_file.seek(0)
            chunk_data = chunk_file.read()

            return rpc_tools.RpcMixin().rpc.timeout(30).chat_upload_chunk_rpc(
                project_id=project_id,
                conversation_id=conversation['id'],
                file_id=file_id,
                chunk_index=int(chunk_index),
                total_chunks=int(total_chunks),
                file_name=file_name,
                chunk_data=chunk_data,
                overwrite=overwrite,
                user_id=user_id,
            )

        # Regular file upload via RPC
        form_files: list[FileStorage] = request.files.getlist("file")
        if not form_files:
            return {"error": "No files provided"}, 400

        files_data = []
        for form_file in form_files:
            form_file.seek(0)
            file_data = form_file.read()
            files_data.append({
                'filename': form_file.filename,
                'data': file_data,
            })

        result = rpc_tools.RpcMixin().rpc.timeout(30).chat_upload_attachments_rpc(
            project_id=project_id,
            conversation_id=conversation['id'],
            files=files_data,
            overwrite=overwrite,
        )

        if 'error' in result:
            return {"error": result['error']}, 400

        return serialize(result['attachments']), 201
