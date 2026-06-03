from pylon.core.tools import module, log, web
from tools import auth, db, config as c, openapi_registry


class Module(module.ModuleModel):
    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor
        self._support_project_id = None

    def init(self):
        self.descriptor.init_all()

    def ready(self):
        self._ensure_support_project()
        self._register_openapi()

    def _register_openapi(self):
        from .api import v2 as api_v2
        openapi_registry.register_plugin(
            plugin_name="support_assistant",
            version=self.descriptor.metadata.get("version", "1.0.0"),
            description="Support assistant conversations and configuration",
            api_module=api_v2,
        )

    def deinit(self):
        self.descriptor.deinit_all()

    @property
    def support_project_id(self) -> int | None:
        if self._support_project_id:
            return self._support_project_id
        self._support_project_id = (
            self.descriptor.state.get('support_project_id') or
            self.descriptor.config.get('support_project_id')
        )
        return self._support_project_id

    @property
    def is_enabled(self) -> bool:
        return self.descriptor.config.get('enabled', False)

    def _ensure_support_project(self):
        """Bootstrap hidden support project if not exists"""
        log.info(f"Support Assistant: checking project (enabled={self.is_enabled}, project_id={self.support_project_id})")

        if self.support_project_id:
            log.info(f"Support Assistant: project already exists ID={self.support_project_id}")
            return

        if not self.is_enabled:
            log.info("Support Assistant: disabled, skipping project creation")
            return

        system_user = "system@centry.user"
        try:
            system_user_id = self.context.rpc_manager.call.auth_get_user(
                email=system_user,
            )["id"]
        except Exception:
            log.warning("Support Assistant: system user not found, deferring project creation")
            return

        try:
            project_name = 'Support Assistant'
            project_id = self.context.rpc_manager.call.projects_create_project(
                project_name=project_name,
                plugins=['elitea_core'],
                admin_email=system_user,
                owner_id=system_user_id,
                roles=['system'],
            )

            if project_id:
                self.descriptor.state['support_project_id'] = project_id
                self.descriptor.save_state()
                self._support_project_id = project_id
                log.info(f"Support Assistant: created project ID={project_id}")
            else:
                log.error("Support Assistant: project creation returned None")
        except Exception as e:
            log.error(f"Support Assistant: failed to create project: {e}")

    def ensure_user_enrolled(self, user_id: int) -> bool:
        """Lazy-enroll user in support project as viewer if they have no existing role"""
        if not self.support_project_id:
            return False

        try:
            user_roles = self.context.rpc_manager.call.admin_get_user_roles(
                project_id=self.support_project_id,
                user_id=user_id
            )
            if user_roles:
                return True

            self.context.rpc_manager.call.admin_add_user_to_project(
                project_id=self.support_project_id,
                user_id=user_id,
                role_names=['viewer']
            )
            return True
        except Exception as e:
            log.warning(f"User enrollment failed: {e}")
            return True
