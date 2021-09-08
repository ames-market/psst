import psst
from psst.case import read_matpower

'''
 Unit test to confirm that PSST can read the bus name strings
 along with setting the bus names as Bus1, Bus 2, ...
 A new df, bus_string, contains the bus names Bus1, Bus 2, ...
 as indices and the bus string
        {
	'a';
	'b';
	'c';
};
 as the string name of the bus.  This unit test confirms that
 the indices of the attribute bus_name are identical to that of bus
'''


def test_bus_name_string(bus_name_string):
    print(bus_name_string)
    assert bus_name_string.columns == 'BUS_NAME_STRING'

def test_bus_indices(busindex,bus_nameindex):
    print(busindex)
    assert (busindex == bus_nameindex).all()


if __name__ == '__main__':
    dir = '../notebooks/cases'
    #matpower_file = dir+'/case3.m'
    matpower_file = dir+'/case3_withbusname.m'
    case = read_matpower( matpower_file)
    if 'bus_string' in case._attributes:
        test_bus_name_string(case.bus_string)
        test_bus_indices(case.bus.index,case.bus_string.index)
    else:
        print('this case does not have pre-defined bus names')
        test_bus_indices(case.bus.index,case.bus_name)
