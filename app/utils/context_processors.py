from flask import session


def inject_globals():
    """Inject global variables into templates"""
    return {
        'active_event_id': session.get('active_event_id'),
        'active_event_name': session.get('active_event_name')
    }
