# -*- coding: utf-8 -*-
import psst.cli as p

try:
    p.scuc(
        "/home/osboxes/grid/repository/ERCOTTestSystem/AMES-V5.0/DATA/PSST_TestCases/PSL_3bus_margin.dat",
        "/home/osboxes/grid/repository/ERCOTTestSystem/AMES-V5.0/psst/tests/GenCoSchedule.dat",
        "cplex",
    )
except:
    pass
