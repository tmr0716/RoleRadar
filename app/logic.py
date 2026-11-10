# State transition matrix
VALID_TRANSITIONS = {
    "APPLIED": ["OA_RECEIVED", "INTERVIEWING", "REJECTED"],
    "OA_RECEIVED": ["INTERVIEWING", "REJECTED"],
    "INTERVIEWING": ["OFFER", "REJECTED"],
    "OFFER": [],      # Terminal state
    "REJECTED": []   # Terminal state
}

def validate_status_transition(current_status: str, new_status: str) -> bool:
    if current_status == new_status:
        return True
    allowed_next_states = VALID_TRANSITIONS.get(current_status, [])
    return new_status in allowed_next_states

def validate_application_input(data: dict) -> tuple[bool, str]:
    if not data.get("company_name"):
        return False, "Company name is required."
    if not data.get("role_title"):
        return False, "Role title is required."
    if not data.get("applied_date"):
        return False, "Applied date is required."
    return True, ""