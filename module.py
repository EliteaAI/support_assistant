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
        self._ensure_default_credentials()
        self._ensure_default_agents()
        self._ensure_default_artifacts()
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

    def _get_system_user_id(self) -> int | None:
        try:
            return self.context.rpc_manager.call.auth_get_user(email="system@centry.user")["id"]
        except Exception:
            log.warning("Support Assistant: system user not found")
            return None

    def _ensure_default_credentials(self):
        """Create anonymous default credentials in the support project if not already present."""
        if not self.is_enabled or not self.support_project_id:
            return
        if self.descriptor.state.get('credentials_provisioned'):
            return

        default_credentials = [
            {
                "elitea_title": "ugithub",
                "type": "github",
                "section": "credentials",
                "label": "GitHub (Anonymous)",
                "data": {
                    "app_id": None,
                    "base_url": "https://api.github.com",
                    "password": None,
                    "username": None,
                    "access_token": None,
                    "app_private_key": None,
                },
            },
            {
                "elitea_title": "githubissues",
                "type": "openapi",
                "section": "credentials",
                "label": "GitHub Issues API (Anonymous)",
                "data": {},
            },
        ]

        try:
            from plugins.configurations.models.configuration import Configuration

            with db.get_session(self.support_project_id) as session:
                for cred in default_credentials:
                    existing = session.query(Configuration).filter_by(
                        elitea_title=cred['elitea_title']
                    ).first()
                    if existing:
                        continue
                    session.add(Configuration(
                        project_id=self.support_project_id,
                        elitea_title=cred['elitea_title'],
                        type=cred['type'],
                        section=cred['section'],
                        label=cred['label'],
                        data=cred['data'],
                        shared=False,
                        meta={},
                    ))
                    log.info(f"Support Assistant: created credential '{cred['elitea_title']}'")
                session.commit()

            self.descriptor.state['credentials_provisioned'] = True
            self.descriptor.save_state()
            log.info("Support Assistant: default credentials provisioned")
        except Exception as e:
            import traceback
            log.error(f"Support Assistant: failed to provision credentials: {e}\n{traceback.format_exc()}")

    def _ensure_default_agents(self):
        """Create default support assistant agents if not provisioned."""
        if not self.is_enabled:
            return
        if not self.support_project_id:
            log.warning("Support Assistant: cannot provision agents without project")
            return
        if self.descriptor.state.get('agents_provisioned'):
            log.debug(f'Support Assistant: agents_provisioned={self.descriptor.state["agents_provisioned"]},')
            log.info("Support Assistant: agents already provisioned, skipping")
            return

        system_user_id = self._get_system_user_id()
        if not system_user_id:
            return

        try:
            from .utils.provisioning import build_import_data, ORCHESTRATOR_NAME
            import_data = build_import_data(self.support_project_id, system_user_id)
            if not import_data:
                log.warning("Support Assistant: no import data built")
                return

            result, errors = self.context.rpc_manager.call.applications_import_wizard(
                import_data=import_data,
                project_id=self.support_project_id,
                author_id=system_user_id,
            )

            for entity, errs in errors.items():
                for err in errs:
                    log.warning(f"Support Assistant: import warning [{entity}]: {err.get('msg', err)}")

            orchestrator_id = None
            for agent_result in result.get('agents', []):
                if agent_result.get('name') == ORCHESTRATOR_NAME:
                    orchestrator_id = agent_result['id']
                    break

            if orchestrator_id:
                self.descriptor.config['agent_id'] = orchestrator_id
                self.descriptor.config['agent_project_id'] = self.support_project_id
                self.descriptor.save_config()
                log.info(f"Support Assistant: set orchestrator agent_id={orchestrator_id}")

            self.descriptor.state['agents_provisioned'] = True
            self.descriptor.save_state()
            log.info("Support Assistant: agents provisioned successfully")
        except Exception as e:
            import traceback
            log.error(f"Support Assistant: failed to provision agents: {e}\n{traceback.format_exc()}")

    def _ensure_default_artifacts(self):
        """Create initial artifact files in the support assistant bucket."""
        if not self.is_enabled:
            return
        if not self.support_project_id:
            return
        if self.descriptor.state.get('artifacts_provisioned'):
            log.info("Support Assistant: artifacts already provisioned, skipping")
            return

        try:
            from .utils.provisioning import ARTIFACT_BUCKET, load_initial_artifacts

            for filename, content in load_initial_artifacts().items():
                try:
                    file_data = content if isinstance(content, bytes) else content.encode('utf-8')
                    self.context.rpc_manager.call.artifacts_upload(
                        project_id=self.support_project_id,
                        bucket=ARTIFACT_BUCKET,
                        filename=filename,
                        file_data=file_data,
                        create_if_not_exists=True,
                        check_duplicates=True,
                        overwrite=False,
                    )
                    log.info(f"Support Assistant: created artifact {filename}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        pass
                    else:
                        log.warning(f"Support Assistant: failed to create artifact {filename}: {e}")

            self.descriptor.state['artifacts_provisioned'] = True
            self.descriptor.save_state()
            log.info("Support Assistant: artifacts provisioned")
        except Exception as e:
            log.error(f"Support Assistant: failed to provision artifacts: {e}")

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
