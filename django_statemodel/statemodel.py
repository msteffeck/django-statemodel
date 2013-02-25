from datetime import datetime

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import curry

from django_statemodel.signals import save_timestamp_cache, set_default_state


OPTIONS_CLASS = "StateModelMeta"


class StateModelBase(models.base.ModelBase):
    def __new__(mcs, name, bases, attrs):
        # Look at Options for information about the StateModel states
        options = attrs.pop(OPTIONS_CLASS, {})

        # Get the field name for state from the meta options
        state_field_name = options.get('state_field_name', 'state')

        # state_map contains the mapping of states values to their attribute
        # names.
        state_map = options.get('state_map', [])

        if state_map:
            # default_state is either the first state in the map, or as
            # overridden
            default_state = options.get('default_state')
            if default_state is None:
                default_state = state_map[0][0]

            # Assign the states as attributes to the model
            if options.get('add_states_to_model', True):
                for key, value in state_map:
                    attrs[value] = key

        # db_index boolean to add an index to the state field. Defaults to True
        db_index = options.get('db_index', True)

        # Get a Django field from the given model's _meta object
        def get_field(model, field):
            if hasattr(model, "_meta"):
                try:
                    return model._meta.get_field(field)
                except models.fields.FieldDoesNotExist:
                    return None
            return None

        # Check if any of the inherited models have the state field
        parent_has_state = False
        for parent in bases:
            if bool(get_field(parent, state_field_name)):
                parent_has_state = True
                break

        # Check if this is an abstract model
        is_abstract_model = getattr(attrs.get('Meta', {}), "abstract", False)

        # If this model is abstract and the state field isn't inherited, add it
        if is_abstract_model and not parent_has_state:
            attrs['state'] = models.IntegerField("State", null=True,
                                                 db_index=db_index)

        #TODO: build 'options' meta object

        cls = super(StateModelBase, mcs).__new__(mcs, name, bases, attrs)

        # Add signals to the inheriting models to save the state transitions
        if not is_abstract_model:
            models.signals.post_save.connect(save_timestamp_cache,
                                             sender=cls)
            models.signals.post_init.connect(set_default_state,
                                             sender=cls)

        state_field = get_field(cls, state_field_name)
        if state_map and state_field:
            # Set up the choices on the state field
            state_field._choices = state_map
            # state_field.default = state_map[0][0]

            # Add in the django 'get_<field>_display' method. This is done
            # in the django metaclass, which has run already, but needs choices
            # to work.
            setattr(cls, 'get_%s_display' % state_field.name,
                    curry(cls._get_FIELD_display, field=state_field))
        return cls

    def _build_options(self, state_map, default_state, db_index):
        pass


class StateTransitionTimestamp(models.Model):
    state = models.IntegerField(
                blank=False,
                null=False,
                help_text="The state of this transition")

    utc_state_time = models.DateTimeField(
                blank=False,
                null=False,
                default=datetime.utcnow,
                help_text="The time this state was entered")

    content_type = models.ForeignKey(
                ContentType,
                blank=True,
                null=True,
                related_name="statetransitiontimestamp_object")

    content_id = models.PositiveIntegerField(
                blank=False,
                null=False)

    content = generic.GenericForeignKey(
                ct_field="content_type",
                fk_field="content_id")

    def __unicode__(self):
        return "%s: %s" % (self.state, self.utc_state_time)


class StateModel(models.Model):
    __metaclass__ = StateModelBase

    class Meta:
        abstract = True

    statetimestamps = generic.GenericRelation(
                StateTransitionTimestamp,
                content_type_field='content_type',
                object_id_field='content_id')

    def __setattr__(self, key, value):
        # TODO: Add 'state' name to meta object and lookup here
        if key == "state":
            self.setState(value, save=False)
        super(StateModel, self).__setattr__(key, value)
        print "Setattr", key, value
