
from django.db import models

OPTIONS_CLASS = "StateModelMeta"

class StateModelBase(models.base.ModelBase):
    def __new__(mcs, name, bases, attrs):
        # Look at Options for information about the StateModel states
        options = attrs.pop(OPTIONS_CLASS, {})

        # state_map contains the mapping of states values to their attribute
        # names. Empty/No state_map, we still create the field, using the
        # 'field_type'.
        state_map = options.get('state_map', [])

        # field_type is, by default, PosInt or Char depending on statemap. Can
        # be overridden.
        field_type = options.get('field_type')
        if field_type is None:
            if mcs._contains_non_integers(state_map):
                field_type = models.CharField
            else:
                field_type = models.IntegerField
        elif field_type == models.IntegerField \
                and mcs._contains_non_integers(state_map):
            raise ValueError("The 'field_type' was declared as Integer, but "
                             "there are non-integers in the state_map")

        # maximum_length only matters if field_type is Char. Default max len is
        # the longest state value in the state_map. Can be overridden.
        maximum_length = options.get('maximum_length')
        if maximum_length:
            pass # TODO: Do this

        # default_state is either the first state in the map, or as overridden
        default_state = options.get('default_state')
        if default_state is None:
            default_state = state_map[0][0]

        # db_index boolean to add an index to the state. Defaults to True
        db_index = options.get('db_index', True)

        return super(StateModelBase, mcs).__new__(mcs, name, bases, attrs)

    def _build_options(self, state_map, field_type, maximum_length,
                             default_state, db_index):
        pass

    def _contains_non_integers(self, state_map):
        for row in state_map:
            try:
                state, name = row
            except ValueError:
                raise ValueError("state_map must be an iterable containing "
                                 "tuples of the following format: "
                                 "(state_value, state_name)")
            # Attempt to cast each state variable into an int. If there are any
            # non-integers, a value error will raise
            try:
                int(state)
                if isinstance(state, float):
                    raise ValueError
            except ValueError:
                return True
        return False




class StateModel(models.Model):
    __metaclass__ = StateModelBase
