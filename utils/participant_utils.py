from tools import db
from pylon.core.tools import log


def get_or_create_application_participant(
    project_id: int,
    application_id: int,
    application_project_id: int = None,
) -> dict:
    """
    Get or create an application participant for the support agent.

    This ensures the configured support agent has a participant entry
    in the support project's participant table.
    """
    from ...elitea_core.models.participants import Participant
    from ...elitea_core.models.enums.all import ParticipantTypes

    effective_project_id = application_project_id or project_id

    with db.get_session(project_id) as session:
        participant = session.query(Participant).filter(
            Participant.entity_name == ParticipantTypes.application.value,
            Participant.entity_meta['id'].astext == str(application_id),
            Participant.entity_meta['project_id'].astext == str(effective_project_id),
        ).first()

        if participant:
            return {
                'id': participant.id,
                'entity_name': participant.entity_name,
                'entity_meta': participant.entity_meta,
            }

        participant = Participant(
            entity_name=ParticipantTypes.application.value,
            entity_meta={
                'id': application_id,
                'project_id': effective_project_id,
            },
        )
        session.add(participant)
        session.commit()

        log.info(f"Created application participant for agent {application_id}")

        return {
            'id': participant.id,
            'entity_name': participant.entity_name,
            'entity_meta': participant.entity_meta,
        }
