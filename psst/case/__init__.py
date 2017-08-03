import os
import logging

import pandas as pd

from .descriptors import (
    Name, Version, BaseMVA, BusName, Bus, Branch, BranchName,
    Gen, GenName, GenCost, Load, Period, _Attributes
)

from . import matpower

from .utils import convert_to_model_one

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
                if len(_list) == 1 and (attribute == 'version' or attribute == 'baseMVA'):
                    setattr(mpc, attribute, _list[0][0])
                else:
                    cols = max([len(l) for l in _list])
                    columns = matpower.COLUMNS.get(attribute, [i for i in range(0, cols)])
                    columns = columns[:cols]
                    if cols > len(columns):
                        if attribute != 'gencost':
                            logger.warning('Number of columns greater than expected number.')
                        # Based on MODEL 2
                        columns = columns[:-1] + ['{}_{}'.format(columns[-1], i) for i in range(cols - len(columns), -1, -1)]
                    df = pd.DataFrame(_list, columns=columns)

                    if attribute == 'bus':
                        df.set_index('BUS_I', inplace=True)

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

    @classmethod
    def _read_festiv(cls, mpc):
        if not isinstance(mpc, cls):
            filename = mpc
            mpc = cls(filename=os.path.abspath(os.path.join(current_directory, '../../cases/case.m')))

        config = dict()
        config['SYSTEM'] = pd.read_excel(filename, sheetname='SYSTEM', index_col=0, header=None, skiprows=1).to_dict()[1]

        gen = pd.read_excel(filename, sheetname='GEN')

        for name, row in gen.iterrows():
            mpc.gen.loc[name] = mpc.gen.loc['GenCo0']
            mpc.gencost.loc[name] = mpc.gencost.loc['GenCo0']

        mpc.gen = mpc.gen.drop('GenCo0', axis=0)
        mpc.gencost = mpc.gencost.drop('GenCo0', axis=0)

        mpc.gen['PMAX'] = gen['CAPACITY']

        gencost = pd.read_excel(filename, sheetname='COST')

        number_of_segments = int(len(gencost.columns) / 2 / 2)

        mpc.gencost = convert_to_model_one(mpc.gencost, number_of_columns=number_of_segments * 2)

        for i, col in enumerate(gencost.columns):
            if gencost[col].isnull().all():
                continue
            if 'COST' in col:
                mpc.gencost['COST_{}'.format(i + 1)] = gencost[col]
            if 'MW' in col:
                mpc.gencost['COST_{}'.format(i - 1)] = gencost[col]

        for i, r in mpc.gencost.iterrows():
            n = r['NCOST']
            for i in range(0, n):
                r['COST_{}'.format((i * 2) + 1)] = r['COST_{}'.format((i * 2) + 1)] * r['COST_{}'.format(i * 2)]

        genbus = pd.read_excel(filename, sheetname='GENBUS')

        genbus = pd.concat([genbus['GENBUS'].str.split('.').apply(lambda x: x[1]), genbus['GENBUS'].str.split('.').apply(lambda x: x[0])], axis=1)
        genbus.columns = ['GEN', 'BUS']
        genbus = genbus.set_index('GEN')

        mpc.gen.loc[genbus['BUS'].index, 'GEN_BUS'] = genbus['BUS']

        bus = pd.read_excel(filename, sheetname='BUS')
        for i, b in enumerate(bus['BUSES'].unique()):
            if i == 0:
                bus = 'Bus1'
            else:
                bus = 'Bus2'
            mpc.bus.loc[b] = mpc.bus.loc[bus]

        mpc.bus = mpc.bus.drop('Bus1')
        mpc.bus = mpc.bus.drop('Bus2')

        branch = pd.read_excel(filename, sheetname='BRANCHDATA')

        for i, row in branch.iterrows():
            mpc.branch.loc[i] = mpc.branch.loc[0]

        mpc.branch = mpc.branch.drop(0)

        mpc.branch['F_BUS'] = branch['BRANCHBUS'].str.split('.').apply(lambda x: x[1])
        mpc.branch['T_BUS'] = branch['BRANCHBUS'].str.split('.').apply(lambda x: x[2])

        mpc.branch['BR_R'] = branch['RESISTANCE']
        mpc.branch['BR_X'] = branch['REACTANCE']
        mpc.branch['BR_B'] = branch['SUSCEPTANCE']
        mpc.branch['RATE_A'] = branch['LINE_RATING']

        for c in mpc.bus_name:
            mpc.load[c] = 0
        t = mpc.load.drop('Bus1', axis=1)
        t = t.drop('Bus2', axis=1)
        mpc.load = t

        return mpc


read_matpower = PSSTCase._read_matpower
read_festiv = PSSTCase._read_festiv
