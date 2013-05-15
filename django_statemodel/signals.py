
def save_timestamp_cache(sender, instance, **kwargs):
    """Save the StateTransitionTimestamp if there is one

    post_save signal for statemodel.
    """
    from .statemodel import OPTIONS_ATTR_NAME

    meta_options = getattr(instance, OPTIONS_ATTR_NAME)
    state_timestamp_cache = getattr(instance,
                                    meta_options.state_timestamps_cache_name,
                                    None)
    if state_timestamp_cache:
        state_timestamp_cache.content = instance
        state_timestamp_cache.save()


def set_default_state(sender, instance, **kwargs):
    """Set the default state so it is correctly tracked

    When a model inheriting the StateModel is initialized, we need to prime
    the timestamp cache with the default state.

    post_init signal for statemodel.
    """
    from .statemodel import OPTIONS_ATTR_NAME, DONE_INITIALIZING

    # Set the done_initializing flag to True. That means the __init__() method
    # is done running. This is used in __setattr__()
    setattr(instance, DONE_INITIALIZING, True)
    meta_options = getattr(instance, OPTIONS_ATTR_NAME)

    # If this is a new instance (never been saved), then we need set the default
    if instance.pk is None:
        setattr(instance, meta_options.state_field_name,
                meta_options.default_state)
