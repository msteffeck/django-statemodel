
from django.db import models


class StateModelBase(models.base.ModelBase):
    pass
    # Look at 'StateModelMeta' for information about the StateModel states

    # state_map contains the mapping of states values to their attribute names.
    # Empty/No state_map, we still create the field, using the 'field_type'.

    # field_type is, by default, PosInt or Char depending on statemap. Can be
    # overridden.

    # maximum_length only matters if field_type is Char. Default max len is the
    # longest state value in the state_map. Can be overridden.

    # default_state is either the first state in the map, or as overridden


class StateModel(models.Model):
    __metaclass__ = StateModelBase
