import os
import logging

from builtins import super
import pandas as pd

from .descriptors import (Name, Version, BaseMVA, BusName, Bus, Branch, BranchName,
                        Gen, GenName, GenCost, Load, Period, _Attributes)

from . import matpower

logger = logging.getLogger(__name__)
pd.options.display.max_rows = 999
pd.options.display.max_columns = 999

current_directory = os.path.realpath(os.path.dirname(__file__))


class PSSTCase(object):

    name = Name()
    version = Version()
    baseMVA = BaseMVA()
    bus = Bus()
    bus_name = BusName()
    branch = Branch()
    branch_name = BranchName()
    gen = Gen()
    gencost = GenCost()
    gen_name = GenName()
    load = Load()
    period = Period()
    _attributes = _Attributes()

    def __init__(self, filename=None, mode='r'):
        self._attributes = list()
        if filename is not None:
            self._filename = filename
        else:
            self._filename = os.path.join(current_directory, '..', 'cases', 'case.m')
        if mode == 'r' or mode == 'read':
            self._read_matpower(self)

    def __repr__(self):
        name = getattr(self, 'name', None)
        gen_name = getattr(self, 'gen_name', None)
        bus_name = getattr(self, 'bus_name', None)
        branch_name = getattr(self, 'branch_name', None)
        name_string = 'name={}'.format(name) if name is not None else ''
        gen_string = 'Generators={}'.format(len(gen_name)) if gen_name is not None else ''
        bus_string = 'Buses={}'.format(len(bus_name)) if bus_name is not None else ''
        branch_string = 'Branches={}'.format(len(branch_name)) if branch_name is not None else ''
        l = [s for s in [name_string, gen_string, bus_string, branch_string] if s != '']
        if len(l) > 1:
            repr_string = ', '.join(l)
        elif len(l) == 1:
            repr_string = l[0]
        else:
            repr_string = ''

        return '<{}.{}({})>'.format(
                    self.__class__.__module__,
                    self.__class__.__name__,
                    repr_string,
                )

    @classmethod
    def _read_matpower(cls, mpc, auto_assign_names=True, fill_loads=True, remove_empty=True, reset_generator_status=True):

        if not isinstance(mpc, cls):
            filename = mpc
            mpc = cls(filename, mode=None)

        with open(os.path.abspath(mpc._filename)) as f:
            string = f.read()

        for attribute in matpower.find_attributes(string):
            _list = matpower.parse_file(attribute, string)
            if _list is not None:
                if len(_list) == 1 and (attribute=='version' or attribute=='baseMVA'):
                    setattr(mpc, attribute, _list[0][0])
                else:
                    cols = max([len(l) for l in _list])
                    columns = matpower.COLUMNS.get(attribute, [i for i in range(0, cols)])
                    columns = columns[:cols]
                    if cols > len(columns):
                        if attribute != 'gencost':
                            logger.warning('Number of columns greater than expected number.')
                        columns = columns[:-1] + ['{}_{}'.format(columns[-1], i) for i in range(cols - len(columns), -1, -1)]
                    df = pd.DataFrame(_list, columns=columns)

                    if attribute == 'bus':
                        df.set_index('BUS_I',inplace=True)

                    setattr(mpc, attribute, df)
                mpc._attributes.append(attribute)

        mpc.name = matpower.find_name(string)

        if auto_assign_names is True:
            mpc.bus_name = mpc.bus_name
            mpc.gen_name = mpc.gen_name
            mpc.branch_name = mpc.branch_name

        if fill_loads is True:
            for i, row in mpc.bus.iterrows():
                mpc.load.loc[:, i] = row['PD']

        if mpc.bus_name.intersection(mpc.gen_name).values.size != 0:
            logger.warning('Bus and Generator names may be identical. This could cause issues when plotting.')

        mpc.gen.loc[mpc.gen['RAMP_10'] == 0, 'RAMP_10'] = mpc.gen['PMAX']
        mpc.gen['STARTUP_RAMP'] = mpc.gen['PMAX']
        mpc.gen['SHUTDOWN_RAMP'] = mpc.gen['PMAX']
        mpc.gen['MINIMUM_UP_TIME'] = 0
        mpc.gen['MINIMUM_DOWN_TIME'] = 0
        try:
            mpc.gencost.loc[mpc.gencost['COST_2'] == 0, 'NCOST'] = 2
        except KeyError as e:
            logger.warning(e)

        mpc.gen_status = pd.DataFrame([mpc.gen['GEN_STATUS'] for i in mpc.load.index])
        mpc.gen_status.index = mpc.load.index
        if reset_generator_status:
            mpc.gen_status.loc[:, :] = pd.np.nan

        return mpc


read_matpower = PSSTCase._read_matpower
