Django StateModel
=================

An abstract model that simplifies the management and history of state for a
django model. This is not an FSM implementation.

This tool simplifies the tracking of state transitions of a model by recording
the state and datetime every time the state is changed.

There are two versions of this project:

1. A standard Django version designed for relational databases
    * Under the master branch
2. A django-nonrel, mongodb-engine version for mongodb
    * Under the mongodb branch

#### For the correct documentation, switch to the branch you intend to use; there are slight differences.


## Installation

##### For the mongodb version:
pip install git+git://github.com/MobileSpinach/django-statemodel@mongodb


## Basic Usage

The Django StateModel requires two things:

1. Inherit into a model
2. Add a StateModelMeta class to the model

```python
from django_statemodel.models import StateModel

class Email(StateModel):
    class StateModelMeta:
        state_map = (       # Not required, but not very useful without
            (1, "Created"),
            (2, "Sent"),
            (3, "Opened"),
            (4, "Bounced"),
            (5, "Failed"),
        )
```

Now you can start using the state field.

```python
e = Email()
print e.state
1
print e.Created
1
print e.get_state_display()
Created
print e.state_timestamps
[]
```

Notice, in the code above, the `state_timestamps` are empty. Timestamps are stored
in a cache field and saved when the model is saved. This is to ensure only the
final state-transition is saved (in case the state is switched before saving).
See example below:

```python
print e._state_timestamps_cache
2: 2013-05-20 23:46:44.372016

e.save()
print e.state_timestamps
[<StateTransitionTimestamp: 1: 2013-05-20 23:36:16.944109>]

# Cache is cleared during the save. This is to prevent duplication on subsequent saves
print e._state_timestamps_cache
None
```

When we switch states, the new state is appended to the list of timestamps:

```python
e.state = e.Sent
print e.state
2

e.save()
print e.state_timestamps
[<StateTransitionTimestamp: 1: 2013-05-20 23:36:16.944109>, <StateTransitionTimestamp: 2: 2013-05-20 23:46:44.37
2016>]
```

#### Important Note:

The default state assignment and the timestamp saving happen
through Django signals. If you are doing something that circumvents the Django
signals, this tool will not work for you.

## Options

#### state_map
* Defines the states values and names
* Default: []
* The `state_map` is added as the *choices* option to the `state` field

```python
    class StateModelMeta:
        state_map = (
            (1, "Created"),
            (2, "Sent"),
            (3, "Opened"),
            (4, "Bounced"),
            (5, "Failed"),
        )

Email._meta.get_field_by_name("state")[0].choices
((1, 'Created'), (2, 'Sent'), (3, 'Opened'), (4, 'Bounced'), (5, 'Failed'))
```

#### default_state
* Defines the default state value. I.E. the state value that is assigned to a
  new instance when no other value is given.
* Default: The first item in the `state_map`, if specified, otherwise None

```python
        default_state = 2

e = Email()
print e.state
2
```

#### use_utc
* Boolean to determine if the timestamp should be stored in UTC or the local time.
* Default: True (use UTC)

#### allow_none_state
* Boolean to determine if a state value of None should be allowed. If False,
  an error will be raised if the user attempts to assign None to the state field.
  Also, if False, the `state_map` option must be specified.
* Default: True (None is allowed)

#### db_index
* Boolean to determine if we should add the *db_index* argument to the generated
  `state` *IntegerField*.
* Default: True (index is added)
* Does not add an index to the `state_timestamp` field

#### add_states_to_model
* Boolean to determine if the state names defined in `state_map` should be added as
  attributes to the model.
* Default: True (add the state names to the model)

```python
        add_states_to_model = True

print e.Created
1
```
```python
        add_states_to_model = False

print e.Created
AttributeError: 'Email' object has no attribute 'Created'
```

#### state_field_name
* The name of the state field
* Default: *state*

```python
        state_field_name = "custom_state_name"

print e.custom_state_name
1
```

#### state_timestamps_field_name
* The name of the state timestamps field
* Default: *state_timestamps*

```python
        state_timestamps_field_name = "custom_timestamp_name"

print e.custom_timestamp_name
[]
```
