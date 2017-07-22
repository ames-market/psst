import ipywidgets as ipyw
import traitlets as T

from .generator import Generator

M = 1e10


class GeneratorView(ipyw.VBox):

    def __init__(self, *args, **kwargs):
        super(GeneratorView, self).__init__(*args, **kwargs)

        # Create an instance of our model.
        self.model = Generator()

        self._title = ipyw.HTML('Generator:')

        self._name = ipyw.Text(
            value='GenCo0',
            description='Name'
        )

        self._capacity = ipyw.LowerBoundedFloatText(
            value=0,
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
            value=0,
            min=0,
            max=0,
            description='Initial Generation (MW):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._minimum_up_time = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=24,
            description='Minimum Up Time (hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._minimum_down_time = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=24,
            description='Minimum Down Time (hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._minimum_generation = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=0,
            description='Minimum Generation (MW):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._noload_cost = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=M,
            description='No-Load Cost ($/hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._startup_cost = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=M,
            description='Startup Cost ($/hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._ramp_up_rate = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=0,
            description='Ramp Up Rate (MW/hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._ramp_down_rate = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=0,
            description='Ramp Down Rate (MW/hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._startup_time = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=24,
            description='Startup Time (hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self._shutdown_time = ipyw.BoundedFloatText(
            value=0,
            min=0,
            max=24,
            description='Shutdown Time (hr):',
            disabled=False,
            style={'description_width': 'initial'}
        )
        # ['noload_cost', 'ramp_down_rate', 'ramp_up_rate', 'shutdown_time', 'startup_cost', 'startup_time']

        children = [
            self._title,
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
            self._startup_cost
        ]

        self.children = children

        T.link((self._capacity, 'value'), (self._initial_generation, 'max'), )
        T.link((self._capacity, 'value'), (self._minimum_generation, 'max'), )
        T.link((self._capacity, 'value'), (self._ramp_up_rate, 'max'), )
        T.link((self._capacity, 'value'), (self._ramp_down_rate, 'max'), )

        T.link((self.model, 'generation_type'), (self._generation_type, 'value'), )
        T.link((self.model, 'initial_status'), (self._initial_status, 'value'), )
        T.link((self.model, 'capacity'), (self._capacity, 'value'), )
        T.link((self.model, 'minimum_generation'), (self._initial_generation, 'value'), )
        T.link((self.model, 'initial_generation'), (self._initial_generation, 'value'), )
        T.link((self.model, 'minimum_up_time'), (self._minimum_up_time, 'value'), )
        T.link((self.model, 'minimum_down_time'), (self._minimum_down_time, 'value'), )

