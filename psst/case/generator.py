import traitlets as T


class Generator(T.HasTraits):

    '''Generator Model'''

    capacity = T.CFloat(default_value=0, min=0, help='Capacity of Generator (MW)')
    noload_cost = T.CFloat(default_value=0, min=0, help='No-Load Cost of a Generator ($/hr)')
    startup_cost = T.CFloat(default_value=0, min=0, help='Startup Cost of a Generator ($/hr)')
    minimum_up_time = T.CInt(default_value=0, min=0, help='Minimum up time (hrs)')
    minimum_down_time = T.CInt(default_value=0, min=0, help='Minimum down time (hrs)')
    ramp_up_rate = T.CFloat(default_value=0, min=0, help='Ramp up rate (MW/hr)')
    ramp_down_rate = T.CFloat(default_value=0, min=0, help='Ramp down rate (MW/hr)')
    minimum_generation = T.CFloat(default_value=0, min=0, help='Minimum generation (MW)')
    generation_type = T.Enum([
        'COAL',
        'GAS',
        'WIND'
    ])
    startup_time = T.CInt(default_value=0, min=0, help='Startup time (hrs)')
    shutdown_time = T.CInt(default_value=0, min=0, help='Shutdown time (hrs)')
    initial_status = T.CBool(default_value=True, min=0, help='Initial status (bool)')

    @T.validate(
        'ramp_up_rate',
        'ramp_down_rate'
    )
    def _less_than_capacity_check(self, proposal):
        if proposal['value'] > self.capacity:
            raise T.TraitError(
                '{class_name}().{trait_name} must be a less than or equal to capacity.'.format(
                    class_name=proposal['owner'].__class__.__name__,
                    trait_name=proposal['trait'].name
                )
            )
        else:
            return proposal['value']
