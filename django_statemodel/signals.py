

def save_timestamp_cache(sender, instance, **kwargs):
    """Save the StateTransitionTimestamp if there is one"""
    if instance._state_transition_cache:
        instance._state_transition_cache.content = instance
        instance._state_transition_cache.save()


def set_default_state(sender, instance, **kwargs):
    """Set the default state so it is correctly tracked

    When a model inheriting the StateModel is initialized, we need to prime
    the timestamp cache with the default state
    """
    #TODO: this may not work. Tried leaving default off 'state'; investigate
    instance._state_transition_cache = None
    if instance.state is None and instance.statemap:
        instance.state = instance.statemap_default
