===========================================================
Agent-Based Modeling of Electricity Systems (AMES) - Market
===========================================================

Copyright (c) 2020, Battelle Memorial Institute

Copyright 2007 - present: numerous others credited in `<AUTHORS.rst>`_

Summary
-------

The key features of AMES include:

* Simulation of **day-ahead** security-constrained unit commitment (SCUC) / security-constrained economic dispatch (SCED) and **real-time** SCED optimizations, running in tandem over successive days of operation, with continually updated initial state conditions.

* Agent-based computational platform designed for federation with other domain simulators, thus permitting the study of larger systems such as integrated transmission and distribution systems.

* Implementation in Python and open-source solver `CBC <https://github.com/coin-or/Cbc>`_, with an option to use a commercial solver on large problems.

Acknowledgement
---------------

AMES was originated in 2006 at Iowa State University (ISU) by Prof.  Leigh 
Tesfatsion and her students.  It evolved through several versions with 
funding from the National Science Foundation, the ISU Electric Power 
Research Center, the U.  S.  Department of Energy (DOE) Office of 
Electricity (OE), the DOE Advanced Research Projects Agency-Energy 
(ARPA-E), the Pacific Northwest National Laboratory (PNNL), and Sandia 
National Laboratories.  

Historical Notes
----------------

A brief summary of the version history follows:

* Version 1.x (June 2007 - October 2007) by Junjie Sun and Leigh Tesfatsion modeled daily day-ahead market (DAM) operations in U.S. RTO/ISO-managed wholesale power markets.  The DAM was cleared by a Security-Constrained Economic Dispatch (SCED) optimization implemented via a newly developed DC OPF solver (DCOPFJ), with congestion handled by locational marginal pricing.  Generators could be configured with reinforcement learning capabilities using a learning module (JReLM) developed by Charlie Giessler.

* Version 2.x (July 2008 - May 2013) by Hongyan Li, Leigh Tesfatsion, and Sean Mooney. This version substantially extended the capabilities of Version 1.x by permitting LSEs to submit price-sensitive demand bids into the DAM SCED optimization, by including a more sophisticated reinforcement learning implementation for generators, and by significant improvements to the graphical user interface.

* Version 3.x (December 2017) by Auswin George Thomas and Leigh Tesfatsion. This version introduced an hourly real-time market (RTM) solved as a SCED optimization.

* Version 4.x (November 2015 - April 2017) by Dheepak Krishnamurthy, Wanning Li, Leigh Tesfatsion, and Auswin George Thomas. This version supported an 8-bus test system that models wholesale power market operations for the Independent System Operator of New England (ISO-NE). It included a stochastic two-stage Security-Constrained Unit Commitment (SCUC).   Most of the code was ported from Java to a Python package called the Power System Simulation Toolkit (PSST).

* Version 5.x (May 2020) by Swathi Battula and Leigh Tesfatsion, with support from PNNL (Tom McDermott, Mitch Pelton, Qiuhua Huang, Sarmad Hanif). This version consolidates features from previous versions and continues the main development in PSST. It adds support for the submission of price-sensitive demand bids into daily DAM SCUC/SCED and RTM SCED optimizations formulated as MILP problems with a comprehensive set of system constraints.  It permits continual updating of initial state conditions to permit market operations to run over successive days.  The package includes an 8-bus test system based on data, operations, and market timing for the Electric Reliability Council of Texas (ERCOT).

More detail is provided in the `original release notes <http://www2.econ.iastate.edu/tesfatsi/AMESVersionReleaseHistory.htm>`_ 
and `list of publications <http://www2.econ.iastate.edu/tesfatsi/AMESMarketHome.htm>`_.  
The original contributors to AMES have now spread out 
through several organizations in the electric power industry.  In order to 
facilitate long-term viability and broader use of AMES, this repository 
has been created to consolidate the development efforts from different 
organizations.  

License
-------

:doc:`LICENSE`

