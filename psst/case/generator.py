import ipywidgets as ipyw
import traitlets as t
import numpy as np
import bqplot as bq
import traittypes as tt

M = 1e10
MAXIMUM_COST_CURVE_SEGMENTS = 50
MINIMUM_COST_CURVE_SEGMENTS = 1


class Generator(t.HasTraits):

    '''Generator Model'''

    name = t.CUnicode(default_value='GenCo0', help='Name of Generator (str)')
    generator_bus = t.CUnicode(default_value='Bus0', help='Bus of Generator (str)')
    generator_voltage = t.CFloat(default_value=1.0, help='Nominal voltage of the generator (p.u.)')
    base_power = t.CFloat(default_value=100.0, help='Base power of the generator (MVA)')
    generation_type = t.Enum(
        [
            'COAL',
            'NATURALGAS',
            'WIND'
        ],
        default_value='COAL'
    )
    minimum_up_time = t.CInt(default_value=0, min=0, help='Minimum up time (hrs)')
    minimum_down_time = t.CInt(default_value=0, min=0, help='Minimum down time (hrs)')
    ramp_up_rate = t.CFloat(default_value=0, min=0, help='Ramp up rate (MW/hr)')
    ramp_down_rate = t.CFloat(default_value=0, min=0, help='Ramp down rate (MW/hr)')
    maximum_real_power = t.CFloat(default_value=0, min=0, help='Capacity of Generator (MW)')
    minimum_real_power = t.CFloat(default_value=0, min=0, help='Minimum generation (MW)')
    maximum_imag_power = t.CFloat(default_value=0, help='Maximum reactive generation (MVAR)')
    minimum_imag_power = t.CFloat(default_value=0, help='Minimum reactive generation (MVAR)')
    initial_real_power = t.CFloat(default_value=0, min=0, help='Initial power generation (MW)')
    initial_imag_power = t.CFloat(default_value=0, min=0, help='Initial power generation (MVAR)')
    initial_status = t.CBool(default_value=True, min=0, help='Initial status (bool)')
    startup_time = t.CInt(default_value=0, min=0, help='Startup time (hrs)')
    shutdown_time = t.CInt(default_value=0, min=0, help='Shutdown time (hrs)')
    nsegments = t.CInt(
        default_value=2,
        min=MINIMUM_COST_CURVE_SEGMENTS,
        max=MAXIMUM_COST_CURVE_SEGMENTS,
        help='Number of data points for piecewise linear'
    )
    cost_curve_points = tt.Array(default_value=[0, 0], minlen=(MINIMUM_COST_CURVE_SEGMENTS + 1), maxlen=(MAXIMUM_COST_CURVE_SEGMENTS + 1))
    cost_curve_values = tt.Array(default_value=[0, 0], minlen=(MINIMUM_COST_CURVE_SEGMENTS + 1), maxlen=(MAXIMUM_COST_CURVE_SEGMENTS + 1))
    noload_cost = t.CFloat(default_value=0, min=0, help='No-Load Cost of a Generator ($/hr)')
    startup_cost = t.CFloat(default_value=0, min=0, help='Startup Cost of a Generator ($/hr)')
    inertia = t.CFloat(allow_none=True, default_value=None, min=0, help='Inertia of generator (NotImplemented)')
    droop = t.CFloat(allow_none=True, default_value=None, min=0, help='Droop of generator (NotImplemented)')

    @property
    def _npoints(self):
        return self.nsegments + 1

    @property
    def ramp_rate(self):
        raise AttributeError(
            "'{class_name}' object has no attribute 'ramp_rate'. Try 'ramp_up_rate' or 'ramp_down_rate'.".format(
                class_name=self.__class__.__name__
            )
        )

    @ramp_rate.setter
    def ramp_rate(self, v):
        self.ramp_up_rate = v
        self.ramp_down_rate = v

    @t.observe('noload_cost')
    def _callback_noload_cost_update_points_values(self, change):

        self.cost_curve_points = np.linspace(self.minimum_real_power, self.maximum_real_power, self._npoints)
        self.cost_curve_values = [change['new']] * self._npoints

        return change['new']

    @t.observe('minimum_real_power')
    def _callback_minimum_real_power_update_points_values(self, change):

        self.cost_curve_points = np.linspace(change['new'], self.maximum_real_power, self._npoints)
        self.cost_curve_values = [self.noload_cost] * self._npoints

        return change['new']

    @t.observe('maximum_real_power')
    def _callback_maximum_real_power_update_points_values(self, change):

        self.cost_curve_points = np.linspace(self.minimum_real_power, change['new'], self._npoints)
        self.cost_curve_values = [self.noload_cost] * self._npoints

        self.ramp_rate = self.maximum_real_power

        return change['new']

    @t.observe('nsegments')
    def _callback_nsegments_update_points_values(self, change):

        self.cost_curve_points = np.linspace(self.minimum_real_power, self.maximum_real_power, change['new'] + 1)
        self.cost_curve_values = [self.noload_cost] * (change['new'] + 1)

        return change['new']

    @t.validate('cost_curve_points', 'cost_curve_values')
    def _validate_max_length(self, proposal):
        if not len(proposal['value']) == self._npoints:
            raise t.TraitError(
                'len({class_name}().{trait_name}) must be equal to {class_name}().nsegments + 1.'.format(
                    class_name=proposal['owner'].__class__.__name__,
                    trait_name=proposal['trait'].name
                )
            )

        return proposal['value']

    @t.validate(
        'ramp_up_rate',
        'ramp_down_rate',
        'initial_real_power',
        'initial_reactive_power',
    )
    def _less_than_maximum_real_power_check(self, proposal):
        if not proposal['value'] <= self.maximum_real_power:
            raise t.TraitError(
                '{class_name}().{trait_name} must be a less than or equal to {class_name}().maximum_real_power.'.format(
                    class_name=proposal['owner'].__class__.__name__,
                    trait_name=proposal['trait'].name
                )
            )
        else:
            return proposal['value']


class GeneratorView(ipyw.Box):

    model = t.Instance(Generator)

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

        self._maximum_real_power = ipyw.BoundedFloatText(
            value=self.model.maximum_real_power,
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

        self._initial_real_power = ipyw.BoundedFloatText(
            value=self.model.initial_real_power,
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

        self._minimum_real_power = ipyw.BoundedFloatText(
            value=self.model.minimum_real_power,
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
            self._maximum_real_power,
            self._minimum_real_power,
            self._initial_real_power,
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

        t.link((self._maximum_real_power, 'value'), (self._initial_real_power, 'max'), )
        t.link((self._maximum_real_power, 'value'), (self._minimum_real_power, 'max'), )
        t.link((self._maximum_real_power, 'value'), (self._ramp_up_rate, 'max'), )
        t.link((self._maximum_real_power, 'value'), (self._ramp_down_rate, 'max'), )
        t.link((self.model, 'maximum_real_power'), (self._maximum_real_power, 'value'), )
        t.link((self.model, 'name'), (self._name, 'value'), )
        t.link((self.model, 'generation_type'), (self._generation_type, 'value'), )
        t.link((self.model, 'initial_status'), (self._initial_status, 'value'), )
        t.link((self.model, 'minimum_real_power'), (self._minimum_real_power, 'value'), )
        t.link((self.model, 'initial_real_power'), (self._initial_real_power, 'value'), )
        t.link((self.model, 'minimum_up_time'), (self._minimum_up_time, 'value'), )
        t.link((self.model, 'minimum_down_time'), (self._minimum_down_time, 'value'), )
        t.link((self.model, 'nsegments'), (self._nsegments, 'value'), )
        t.link((self.model, 'ramp_up_rate'), (self._ramp_up_rate, 'value'), )
        t.link((self.model, 'ramp_down_rate'), (self._ramp_down_rate, 'value'), )
        t.link((self.model, 'startup_time'), (self._startup_time, 'value'), )
        t.link((self.model, 'shutdown_time'), (self._shutdown_time, 'value'), )
        t.link((self.model, 'noload_cost'), (self._noload_cost, 'value'), )
        t.link((self.model, 'startup_cost'), (self._startup_cost, 'value'), )


class GeneratorRowView(GeneratorView):

    _model_name = t.Unicode('HBoxModel').tag(sync=True)
    _view_name = t.Unicode('HBoxView').tag(sync=True)


class GeneratorColumnView(GeneratorView):

    _model_name = t.Unicode('VBoxModel').tag(sync=True)
    _view_name = t.Unicode('VBoxView').tag(sync=True)


class GeneratorCostView(ipyw.VBox):

    model = t.Instance(Generator)

    def __init__(self, model=None, *args, **kwargs):

        super(GeneratorCostView, self).__init__(*args, **kwargs)

        if model is not None:
            self.model = model
        else:
            self.model = Generator()

        self._scale_x = bq.LinearScale(
            min=self.model.minimum_real_power,
            max=self.model.maximum_real_power
        )

        self._scale_y = bq.LinearScale(
            min=0,
            max=(max(self.model.cost_curve_values) * 1.5 + 50)
        )

        self._scales = {
            'x': self._scale_x,
            'y': self._scale_y,
        }

        self._scatter = bq.Scatter(
            x=self.model.cost_curve_points,
            y=self.model.cost_curve_values,
            scales=self._scales
        )

        self._lines = bq.Lines(
            x=self.model.cost_curve_points,
            y=self.model.cost_curve_values,
            scales=self._scales
        )

        self._axes_x = bq.Axis(scale=self._scale_x)
        self._axes_y = bq.Axis(scale=self._scale_y, orientation='vertical', padding_x=0.025)

        f = bq.Figure(marks=[self._lines, self._scatter], axes=[self._axes_x, self._axes_y])

        children = [f]

        self.children = children

        t.link((self.model, 'maximum_real_power'), (self._scale_x, 'max'))
        t.link((self.model, 'cost_curve_points'), (self._scatter, 'x'))
        t.link((self.model, 'cost_curve_values'), (self._scatter, 'y'))

        ipyw.jslink((self._lines, 'x'), (self._scatter, 'x'))
        ipyw.jslink((self._lines, 'y'), (self._scatter, 'y'))

        # self._scatter.observe(self._callback_ydata, names=['y'])

        with self._scatter.hold_sync():
            self._scatter.enable_move = True
            self._scatter.update_on_move = True
            self._scatter.interactions = {'click': None}

    def _callback_ydata(self, change):
        self._scale_y.max = float(max(self._scatter.y)) + 50

