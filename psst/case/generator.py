import warnings
import ipywidgets as ipyw
import traitlets as T

M = 1e10


class Generator(T.HasTraits):

    '''Generator Model'''

    name = T.CUnicode(default_value='GenCo0', help='Name of Generator (str)')
    capacity = T.CFloat(default_value=0, min=0, help='Capacity of Generator (MW)')
    noload_cost = T.CFloat(default_value=0, min=0, help='No-Load Cost of a Generator ($/hr)')
    startup_cost = T.CFloat(default_value=0, min=0, help='Startup Cost of a Generator ($/hr)')
    minimum_up_time = T.CInt(default_value=0, min=0, help='Minimum up time (hrs)')
    minimum_down_time = T.CInt(default_value=0, min=0, help='Minimum down time (hrs)')
    ramp_up_rate = T.CFloat(default_value=0, min=0, help='Ramp up rate (MW/hr)')
    ramp_down_rate = T.CFloat(default_value=0, min=0, help='Ramp down rate (MW/hr)')
    minimum_generation = T.CFloat(default_value=0, min=0, help='Minimum generation (MW)')
    generation_type = T.Enum(
        [
            'COAL',
            'NATURALGAS',
            'WIND'
        ],
        default_value='COAL'
    )
    bid_offer_type = T.Enum(
        [
            'PIECEWISELINEAR',
            'POLYNOMIAL'
        ],
        default_value='POLYNOMIAL'
    )
    startup_time = T.CInt(default_value=0, min=0, help='Startup time (hrs)')
    shutdown_time = T.CInt(default_value=0, min=0, help='Shutdown time (hrs)')
    initial_status = T.CBool(default_value=True, min=0, help='Initial status (bool)')
    initial_generation = T.CFloat(default_value=0, min=0, help='Initial power generation (MW)')
    ncost = T.CInt(default_value=2, min=2, help='number of cost coefficients for polynomial cost function, or number of data points for piecewise linear')
    _points = T.List(T.Float(), default_value=[0, 0], minlen=2)
    _values = T.List(T.Float(), default_value=[0, 0], minlen=2)
    inertia = T.CFloat(allow_none=True, default_value=None, min=0, help='Inertia of generator (NotImplemented)')
    droop = T.CFloat(allow_none=True, default_value=None, min=0, help='Droop of generator (NotImplemented)')
    _max_ncost = T.CInt(
        default_value=3,
        max=50,
        help='Maximum number of cost coefficients for polynomial cost function or number of data points for piecewise linear'
    )

    @T.observe('ncost')
    def _callback_ncost(self, change):

        if len(self._points) > self.ncost:
            warnings.warn("Number of points greater than ncost, trimming higher values")
            self._points = self._points[:self.ncost]

        if len(self._values) > self.ncost:
            warnings.warn("Number of values greater than ncost, trimming higher values")
            self._values = self._values[:self.ncost]

    @T.validate('_points', '_values')
    def _validate_max_length(self, proposal):
        if len(proposal['value']) > self.ncost:
            raise T.TraitError(
                '{class_name}().{trait_name} must be a less than or equal to {class_name}().ncost.'.format(
                    class_name=proposal['owner'].__class__.__name__,
                    trait_name=proposal['trait'].name
                )
            )
        if sorted(proposal['value']) != proposal['value']:
            raise T.TraitError(
                '{class_name}().{trait_name} must be a sorted list of floats.'.format(
                    class_name=proposal['owner'].__class__.__name__,
                    trait_name=proposal['trait'].name
                )
            )

        return proposal['value']

    @T.observe('bid_offer_type')
    def _callback_bid_offer_type(self, change):
        if change['new'] == 'POLYNOMIAL':
            if self.ncost > 3:
                self.ncost = 3
            self._max_ncost = 3
        else:
            self._max_ncost = 50

    @T.validate(
        'ramp_up_rate',
        'ramp_down_rate',
        'initial_generation'
    )
    def _less_than_capacity_check(self, proposal):
        if proposal['value'] > self.capacity:
            raise T.TraitError(
                '{class_name}().{trait_name} must be a less than or equal to {class_name}().capacity.'.format(
                    class_name=proposal['owner'].__class__.__name__,
                    trait_name=proposal['trait'].name
                )
            )
        else:
            return proposal['value']


class GeneratorView(ipyw.Box):

    model = T.Instance(Generator)

    def __init__(self, model=None, *args, **kwargs):

        if model is not None:
            self.model = model
        else:
            self.model = Generator()

        super(GeneratorView, self).__init__(*args, **kwargs)

        self._title = ipyw.HTML('Generator:')

        self._name = ipyw.Text(
            value='GenCo0',
            description='Name',
            style={'description_width': 'initial'}
        )

        self._capacity = ipyw.BoundedFloatText(
            value=self.model.capacity,
            min=0,
            max=M,
            description='Capacity (MW):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._generation_type = ipyw.Dropdown(
            value=self.model.generation_type,
            options=Generator.generation_type.values,
            description='Generation Type:',
            style={'description_width': 'initial'}
        )

        self._initial_status = ipyw.Checkbox(
            value=self.model.initial_status,
            description='Initial Status:',
            style={'description_width': 'initial'}
        )

        self._initial_generation = ipyw.BoundedFloatText(
            value=self.model.initial_generation,
            min=0,
            max=0,
            description='Initial Generation (MW):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._minimum_up_time = ipyw.BoundedFloatText(
            value=self.model.minimum_up_time,
            min=0,
            max=24,
            description='Minimum Up Time (hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._minimum_down_time = ipyw.BoundedFloatText(
            value=self.model.minimum_down_time,
            min=0,
            max=24,
            description='Minimum Down Time (hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._minimum_generation = ipyw.BoundedFloatText(
            value=self.model.minimum_generation,
            min=0,
            max=0,
            description='Minimum Generation (MW):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._noload_cost = ipyw.BoundedFloatText(
            value=self.model.noload_cost,
            min=0,
            max=M,
            description='No-Load Cost ($/hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._startup_cost = ipyw.BoundedFloatText(
            value=self.model.startup_cost,
            min=0,
            max=M,
            description='Startup Cost ($/hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._ramp_up_rate = ipyw.BoundedFloatText(
            value=self.model.ramp_up_rate,
            min=0,
            max=0,
            description='Ramp Up Rate (MW/hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._ramp_down_rate = ipyw.BoundedFloatText(
            value=self.model.ramp_down_rate,
            min=0,
            max=0,
            description='Ramp Down Rate (MW/hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._startup_time = ipyw.BoundedFloatText(
            value=self.model.startup_time,
            min=0,
            max=24,
            description='Startup Time (hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._shutdown_time = ipyw.BoundedFloatText(
            value=self.model.shutdown_time,
            min=0,
            max=24,
            description='Shutdown Time (hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._bid_offer_type = ipyw.Dropdown(
            value=self.model.bid_offer_type,
            options=Generator.bid_offer_type.values,
            description='Bid Offer Type:',
            style={'description_width': 'initial'}
        )

        self._ncost = ipyw.IntSlider(
            value=self.model.ncost,
            min=2,
            max=self.model._max_ncost,
            step=1,
            description='Number Cost Coeff',
            disabled=False,
            style={'description_width': 'initial'}
        )

        children = [
            self._title,
            self._name,
            self._initial_status,
            self._generation_type,
            self._capacity,
            self._minimum_generation,
            self._initial_generation,
            self._minimum_up_time,
            self._minimum_down_time,
            self._ramp_down_rate,
            self._ramp_up_rate,
            self._startup_time,
            self._shutdown_time,
            self._noload_cost,
            self._startup_cost,
            self._bid_offer_type,
            self._ncost,
        ]

        self.children = children

        T.link((self._capacity, 'value'), (self._initial_generation, 'max'), )
        T.link((self._capacity, 'value'), (self._minimum_generation, 'max'), )
        T.link((self._capacity, 'value'), (self._ramp_up_rate, 'max'), )
        T.link((self._capacity, 'value'), (self._ramp_down_rate, 'max'), )
        T.link((self.model, 'capacity'), (self._capacity, 'value'), )
        T.link((self.model, 'name'), (self._name, 'value'), )
        T.link((self.model, 'generation_type'), (self._generation_type, 'value'), )
        T.link((self.model, 'initial_status'), (self._initial_status, 'value'), )
        T.link((self.model, 'minimum_generation'), (self._minimum_generation, 'value'), )
        T.link((self.model, 'initial_generation'), (self._initial_generation, 'value'), )
        T.link((self.model, 'minimum_up_time'), (self._minimum_up_time, 'value'), )
        T.link((self.model, 'minimum_down_time'), (self._minimum_down_time, 'value'), )
        T.link((self.model, 'bid_offer_type'), (self._bid_offer_type, 'value'), )
        T.link((self.model, 'ncost'), (self._ncost, 'value'), )
        T.link((self.model, '_max_ncost'), (self._ncost, 'max'), )


class GeneratorRowView(GeneratorView):

    _model_name = T.Unicode('HBoxModel').tag(sync=True)
    _view_name = T.Unicode('HBoxView').tag(sync=True)


class GeneratorColumnView(GeneratorView):

    _model_name = T.Unicode('VBoxModel').tag(sync=True)
    _view_name = T.Unicode('VBoxView').tag(sync=True)

