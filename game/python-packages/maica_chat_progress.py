SUCCESSFUL_CHAT_RESULTS = frozenset(("canceled", "mtrigger_triggering"))


def is_successful_chat_result(return_code):
    """Return whether a maica_talking call completed without an error."""
    return return_code in SUCCESSFUL_CHAT_RESULTS


def next_successful_chat_count(current_count, return_code):
    """Increment a non-negative chat count only for a successful result."""
    current_count = max(0, current_count or 0)
    if is_successful_chat_result(return_code):
        return current_count + 1
    return current_count
