import ipywidgets as ipyw
import traitlets as T
import numpy as np
import bqplot as bq
import traittypes as tt

M = 1e10
MAXIMUM_COST_CURVE_SEGMENTS = 50
MINIMUM_COST_CURVE_SEGMENTS = 1


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
    startup_time = T.CInt(default_value=0, min=0, help='Startup time (hrs)')
    shutdown_time = T.CInt(default_value=0, min=0, help='Shutdown time (hrs)')
    initial_status = T.CBool(default_value=True, min=0, help='Initial status (bool)')
    initial_generation = T.CFloat(default_value=0, min=0, help='Initial power generation (MW)')
    nsegments = T.CInt(default_value=2, min=MINIMUM_COST_CURVE_SEGMENTS, max=MAXIMUM_COST_CURVE_SEGMENTS, help='Number of data points for piecewise linear')
    _points = tt.Array(default_value=[0, 0], minlen=(MINIMUM_COST_CURVE_SEGMENTS + 1), maxlen=(MAXIMUM_COST_CURVE_SEGMENTS + 1))
    _values = tt.Array(default_value=[0, 0], minlen=(MINIMUM_COST_CURVE_SEGMENTS + 1), maxlen=(MAXIMUM_COST_CURVE_SEGMENTS + 1))
    inertia = T.CFloat(allow_none=True, default_value=None, min=0, help='Inertia of generator (NotImplemented)')
    droop = T.CFloat(allow_none=True, default_value=None, min=0, help='Droop of generator (NotImplemented)')

    @property
    def _npoints(self):
        return self.nsegments + 1

    @T.observe('noload_cost')
    def _callback_noload_cost_update_points_values(self, change):

        self._values = [change['new']] * self._npoints

        return change['new']

    @T.observe('minimum_generation')
    def _callback_minimum_generation_update_points_values(self, change):

        self._points = np.linspace(change['new'], self.capacity, self._npoints)

        return change['new']

    @T.observe('capacity')
    def _callback_capacity_update_points_values(self, change):

        self._points = np.linspace(self.minimum_generation, change['new'], self._npoints)

        return change['new']

    @T.observe('nsegments')
    def _callback_nsegments_update_points_values(self, change):

        self._points = np.linspace(self.minimum_generation, self.capacity, change['new'] + 1)
        self._values = [self.noload_cost] * (change['new'] + 1)

        return change['new']

    @T.validate('_points', '_values')
    def _validate_max_length(self, proposal):
        if len(proposal['value']) > self._npoints:
            raise T.TraitError(
                'len({class_name}().{trait_name}) must be equal to {class_name}().nsegments + 1.'.format(
                    class_name=proposal['owner'].__class__.__name__,
                    trait_name=proposal['trait'].name
                )
            )

        return proposal['value']

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
            # style={'description_width': 'initial'}
        )

        self._capacity = ipyw.BoundedFloatText(
            value=self.model.capacity,
            min=0,
            max=M,
            description='Capacity (MW):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._generation_type = ipyw.Dropdown(
            value=self.model.generation_type,
            options=Generator.generation_type.values,
            description='Generation Type:',
            # style={'description_width': 'initial'}
        )

        self._initial_status = ipyw.Checkbox(
            value=self.model.initial_status,
            description='Initial Status:',
            # style={'description_width': 'initial'}
        )

        self._initial_generation = ipyw.BoundedFloatText(
            value=self.model.initial_generation,
            min=0,
            max=0,
            description='Initial Generation (MW):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._minimum_up_time = ipyw.BoundedFloatText(
            value=self.model.minimum_up_time,
            min=0,
            max=24,
            description='Minimum Up Time (hr):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._minimum_down_time = ipyw.BoundedFloatText(
            value=self.model.minimum_down_time,
            min=0,
            max=24,
            description='Minimum Down Time (hr):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._minimum_generation = ipyw.BoundedFloatText(
            value=self.model.minimum_generation,
            min=0,
            max=0,
            description='Minimum Generation (MW):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._noload_cost = ipyw.BoundedFloatText(
            value=self.model.noload_cost,
            min=0,
            max=M,
            description='No-Load Cost ($/hr):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._startup_cost = ipyw.BoundedFloatText(
            value=self.model.startup_cost,
            min=0,
            max=M,
            description='Startup Cost ($/hr):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._ramp_up_rate = ipyw.BoundedFloatText(
            value=self.model.ramp_up_rate,
            min=0,
            max=0,
            description='Ramp Up Rate (MW/hr):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._ramp_down_rate = ipyw.BoundedFloatText(
            value=self.model.ramp_down_rate,
            min=0,
            max=0,
            description='Ramp Down Rate (MW/hr):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._startup_time = ipyw.BoundedFloatText(
            value=self.model.startup_time,
            min=0,
            max=24,
            description='Startup Time (hr):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._shutdown_time = ipyw.BoundedFloatText(
            value=self.model.shutdown_time,
            min=0,
            max=24,
            description='Shutdown Time (hr):',
            disabled=False,
            # style={'description_width': 'initial'}
        )

        self._nsegments = ipyw.IntSlider(
            value=self.model.nsegments,
            min=2,
            max=MAXIMUM_COST_CURVE_SEGMENTS,
            step=1,
            description='Number of Cost Curve Segments',
            disabled=False,
            # style={'description_width': 'initial'}
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
            self._nsegments,
            self._ramp_up_rate,
            self._ramp_down_rate,
            self._startup_time,
            self._shutdown_time,
            self._noload_cost,
            self._startup_cost,
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
        T.link((self.model, 'nsegments'), (self._nsegments, 'value'), )
        T.link((self.model, 'ramp_up_rate'), (self._ramp_up_rate, 'value'), )
        T.link((self.model, 'ramp_down_rate'), (self._ramp_down_rate, 'value'), )
        T.link((self.model, 'startup_time'), (self._startup_time, 'value'), )
        T.link((self.model, 'shutdown_time'), (self._shutdown_time, 'value'), )
        T.link((self.model, 'noload_cost'), (self._noload_cost, 'value'), )
        T.link((self.model, 'startup_cost'), (self._startup_cost, 'value'), )


class GeneratorRowView(GeneratorView):

    _model_name = T.Unicode('HBoxModel').tag(sync=True)
    _view_name = T.Unicode('HBoxView').tag(sync=True)


class GeneratorColumnView(GeneratorView):

    _model_name = T.Unicode('VBoxModel').tag(sync=True)
    _view_name = T.Unicode('VBoxView').tag(sync=True)


class GeneratorCostView(ipyw.VBox):

    model = T.Instance(Generator)

    def __init__(self, model=None, *args, **kwargs):

        super(GeneratorCostView, self).__init__(*args, **kwargs)

        if model is not None:
            self.model = model
        else:
            self.model = Generator()

        self._scale_x = bq.LinearScale(
            min=self.model.minimum_generation,
            max=self.model.capacity
        )

        self._scale_y = bq.LinearScale(
            min=0,
            max=(max(self.model._values) * 1.5 + 50)
        )

        self._scales = {
            'x': self._scale_x,
            'y': self._scale_y,
        }

        self._scatter = bq.Scatter(
            x=self.model._points,
            y=self.model._values,
            scales=self._scales
        )

        self._lines = bq.Lines(
            x=self.model._points,
            y=self.model._values,
            scales=self._scales
        )

        self._axes_x = bq.Axis(scale=self._scale_x)
        self._axes_y = bq.Axis(scale=self._scale_y, orientation='vertical', padding_x=0.025)

        f = bq.Figure(marks=[self._lines, self._scatter], axes=[self._axes_x, self._axes_y])

        children = [f]

        self.children = children

        T.link((self.model, 'capacity'), (self._scale_x, 'max'))
        T.link((self.model, '_points'), (self._scatter, 'x'))
        T.link((self.model, '_values'), (self._scatter, 'y'))
        T.link((self.model, '_points'), (self._lines, 'x'))
        T.link((self.model, '_values'), (self._lines, 'y'))

        # self._scatter.observe(self._callback_ydata, names=['y'])

        with self._scatter.hold_sync():
            self._scatter.enable_move = True
            self._scatter.update_on_move = True
            self._scatter.interactions = {'click': None}

    def _callback_ydata(self, change):
        self._scale_y.max = float(max(self._scatter.y)) + 50

