
def save_timestamp_cache(sender, instance, **kwargs):
    """Save the State transition timestamp if there is one

    pre_save signal for statemodel.
    """
    from .models import OPTIONS_ATTR_NAME

    # Get the cache where the current state's timestamp was added
    meta_options = getattr(instance, OPTIONS_ATTR_NAME)
    state_timestamp_cache = getattr(instance,
                                    meta_options.state_timestamps_cache_name,
                                    None)

    # If the cache is None, that means there were no state changes
    if state_timestamp_cache:
        # Get the field where we store the state timestamps
        state_timestamps = getattr(instance,
                                   meta_options.state_timestamps_field_name)

        # If the timestamp list is empty or missing, create it. Otherwise
        # append the new timestamp to the list
        if not isinstance(state_timestamps, list):
            setattr(instance,
                    meta_options.state_timestamps_field_name,
                    [state_timestamp_cache])
        else:
            state_timestamps.append(state_timestamp_cache)

        # Clear the cache
        setattr(instance, meta_options.state_timestamps_cache_name, None)


def set_default_state(sender, instance, **kwargs):
    """Set the default state so it is correctly tracked

    When a model inheriting the StateModel is initialized, we need to prime
    the timestamp cache with the default state.

    post_init signal for statemodel.
    """
    from .models import OPTIONS_ATTR_NAME, DONE_INITIALIZING

    # Set the done_initializing flag to True. That means the __init__() method
    # is done running. This is used in __setattr__()
    setattr(instance, DONE_INITIALIZING, True)
    meta_options = getattr(instance, OPTIONS_ATTR_NAME)

    # If this is a new instance (never been saved), then we need set the default
    if instance.pk is None:
        setattr(instance, meta_options.state_field_name,
                meta_options.default_state)
