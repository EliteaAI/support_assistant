"""Unit tests for pydantic models in models/pd/."""
import sys
import pytest
from pydantic import ValidationError


@pytest.fixture(scope='module')
def support_module(models_path):
    """Load the support module."""
    pd_path = models_path / "pd"
    sys.path.insert(0, str(pd_path))
    try:
        import support
        return support
    finally:
        sys.path.remove(str(pd_path))


@pytest.fixture(scope='module')
def message_module(models_path):
    """Load the message module."""
    pd_path = models_path / "pd"
    sys.path.insert(0, str(pd_path))
    try:
        import message
        return message
    finally:
        sys.path.remove(str(pd_path))


@pytest.fixture(scope='module')
def config_module(models_path):
    """Load the config module."""
    pd_path = models_path / "pd"
    sys.path.insert(0, str(pd_path))
    try:
        import config
        return config
    finally:
        sys.path.remove(str(pd_path))


@pytest.fixture(scope='module')
def conversation_module(models_path):
    """Load the conversation module."""
    pd_path = models_path / "pd"
    sys.path.insert(0, str(pd_path))
    try:
        import conversation
        return conversation
    finally:
        sys.path.remove(str(pd_path))


class TestSupportAssistantContext:
    """Tests for SupportAssistantContext model."""

    def test_all_fields_optional(self, support_module):
        SupportAssistantContext = support_module.SupportAssistantContext
        ctx = SupportAssistantContext()
        assert ctx.assistant_name is None
        assert ctx.project_id is None
        assert ctx.current_page is None

    def test_with_all_fields(self, support_module):
        SupportAssistantContext = support_module.SupportAssistantContext
        ctx = SupportAssistantContext(
            assistant_name="ELITEA Support",
            assistant_version="1.0.0",
            project_id=42,
            project_name="Test Project",
            current_page="/agents",
            current_entity_type="agent",
            current_entity_id=123,
            current_entity_name="My Agent",
            selected_provider="openai",
            selected_model="gpt-4o",
            meta={"key": "value"}
        )
        assert ctx.assistant_name == "ELITEA Support"
        assert ctx.project_id == 42
        assert ctx.meta == {"key": "value"}


class TestSupportPredictPayload:
    """Tests for SupportPredictPayload model."""

    def test_valid_payload(self, support_module):
        SupportPredictPayload = support_module.SupportPredictPayload
        payload = SupportPredictPayload(
            conversation_uuid="abc-123",
            content="Hello, I need help"
        )
        assert payload.conversation_uuid == "abc-123"
        assert payload.content == "Hello, I need help"
        assert payload.attachments is None

    def test_content_required(self, support_module):
        SupportPredictPayload = support_module.SupportPredictPayload
        with pytest.raises(ValidationError):
            SupportPredictPayload(conversation_uuid="abc-123")

    def test_content_min_length(self, support_module):
        SupportPredictPayload = support_module.SupportPredictPayload
        with pytest.raises(ValidationError):
            SupportPredictPayload(conversation_uuid="abc-123", content="")

    def test_conversation_uuid_required(self, support_module):
        SupportPredictPayload = support_module.SupportPredictPayload
        with pytest.raises(ValidationError):
            SupportPredictPayload(content="Hello")

    def test_with_attachments(self, support_module):
        SupportPredictPayload = support_module.SupportPredictPayload
        payload = SupportPredictPayload(
            conversation_uuid="abc-123",
            content="Check this file",
            attachments=["file1.txt", "file2.png"]
        )
        assert payload.attachments == ["file1.txt", "file2.png"]

    def test_with_context(self, support_module):
        SupportPredictPayload = support_module.SupportPredictPayload
        SupportAssistantContext = support_module.SupportAssistantContext
        ctx = SupportAssistantContext(project_id=42, current_page="/chat")
        payload = SupportPredictPayload(
            conversation_uuid="abc-123",
            content="Help",
            support_assistant_context=ctx
        )
        assert payload.support_assistant_context.project_id == 42


class TestMessageCreateRequest:
    """Tests for MessageCreateRequest model."""

    def test_valid_message(self, message_module):
        MessageCreateRequest = message_module.MessageCreateRequest
        msg = MessageCreateRequest(content="Hello!")
        assert msg.content == "Hello!"
        assert msg.attachments is None

    def test_content_required(self, message_module):
        MessageCreateRequest = message_module.MessageCreateRequest
        with pytest.raises(ValidationError):
            MessageCreateRequest()

    def test_content_min_length(self, message_module):
        MessageCreateRequest = message_module.MessageCreateRequest
        with pytest.raises(ValidationError):
            MessageCreateRequest(content="")

    def test_with_attachments(self, message_module):
        MessageCreateRequest = message_module.MessageCreateRequest
        msg = MessageCreateRequest(
            content="See attached",
            attachments=["doc.pdf"]
        )
        assert msg.attachments == ["doc.pdf"]


class TestConfigUpdateRequest:
    """Tests for ConfigUpdateRequest model."""

    def test_all_fields_optional(self, config_module):
        ConfigUpdateRequest = config_module.ConfigUpdateRequest
        cfg = ConfigUpdateRequest()
        assert cfg.enabled is None
        assert cfg.agent_id is None

    def test_partial_update(self, config_module):
        ConfigUpdateRequest = config_module.ConfigUpdateRequest
        cfg = ConfigUpdateRequest(enabled=True, welcome_message="Hi!")
        assert cfg.enabled is True
        assert cfg.welcome_message == "Hi!"
        assert cfg.agent_id is None

    def test_full_config(self, config_module):
        ConfigUpdateRequest = config_module.ConfigUpdateRequest
        cfg = ConfigUpdateRequest(
            enabled=True,
            agent_id="agent-xyz",
            agent_project_id=42,
            welcome_message="Welcome!",
            assistant_name="Support Bot",
            support_project_id=7,
            placeholder="Ask me anything..."
        )
        assert cfg.agent_id == "agent-xyz"
        assert cfg.agent_project_id == 42
        assert cfg.support_project_id == 7


class TestConversationCreateRequest:
    """Tests for ConversationCreateRequest model."""

    def test_name_optional(self, conversation_module):
        ConversationCreateRequest = conversation_module.ConversationCreateRequest
        conv = ConversationCreateRequest()
        assert conv.name is None

    def test_with_name(self, conversation_module):
        ConversationCreateRequest = conversation_module.ConversationCreateRequest
        conv = ConversationCreateRequest(name="My Chat")
        assert conv.name == "My Chat"

    def test_name_max_length(self, conversation_module):
        ConversationCreateRequest = conversation_module.ConversationCreateRequest
        long_name = "x" * 256
        with pytest.raises(ValidationError):
            ConversationCreateRequest(name=long_name)

    def test_name_at_max_length(self, conversation_module):
        ConversationCreateRequest = conversation_module.ConversationCreateRequest
        max_name = "x" * 255
        conv = ConversationCreateRequest(name=max_name)
        assert len(conv.name) == 255
