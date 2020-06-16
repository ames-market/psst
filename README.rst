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

See documentation_ and publications_ for more information.

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

More detail is provided in the `original release notes <http://www2.econ.iastate.edu/tesfatsi/AMESVersionReleaseHistory.htm>`_.  
The original contributors to AMES have now spread out 
through several organizations in the electric power industry.  In order to 
facilitate long-term viability and broader use of AMES, this repository 
has been created to consolidate the development efforts from different 
organizations.  

License and Disclaimer
----------------------

`<LICENSE.rst>`_

`<DISCLAIMER.rst>`_

.. _documentation:

Documentation
-------------

- Leigh Tesfatsion and Swathi Battula (2020), "Analytical SCUC/SCED Optimization Formulation for AMES V5.0," Economics Working Paper #20014, Iowa State University, Ames, IA. Available online: https://lib.dr.iastate.edu/econ_workingpapers/109/

.. _publications:

Publications
------------

- Swathi Battula, Leigh Tesfatsion, and Thomas E. McDermott (2020), "An ERCOT Test System for Market Design Studies" (`WP Preprint, pdf, 3.5MB <https://lib.dr.iastate.edu/econ_workingpapers/79>`_), Applied Energy, to appear.
- Charles Gieseler (2005), "A Java Reinforcement Learning Module for the Repast Toolkit: Facilitating Study and Implementation with Reinforcement Learning in Social Science Multi-Agent Simulations" (`pdf, 1.1MB <http://www2.econ.iastate.edu/tesfatsi/CharlesGieseler_thesis.pdf>`_), (`ppt, 1.1MB <http://www2.econ.iastate.edu/tesfatsi/CharlieGieseler_thesisPresentation.pdf>`_), Department of Computer Science, Iowa State University, M.S. Thesis.
- Deddy Koesrindartoto and Leigh Tesfatsion (2004), "Testing the Reliability of FERC's Wholesale Power Market Platform: An Agent-Based Computational Economics Approach" (`pdf, 45KB <http://www2.econ.iastate.edu/tesfatsi/usaeetalk.pdf>`_), Energy, Environment, and Economics in a New Era, Proceedings of the 24th USAEE/IAEE North American Conference, Washington, D.C., July 8-10.
- Deddy Koesrindartoto, Junie Sun, and Leigh Tesfatsion (2005), "An Agent-Based Computational Laboratory for Testing the Economic Reliability of Wholesale Power Market Designs" (`pdf, 112KB <http://www2.econ.iastate.edu/tesfatsi/ieeepow.pdf>`_), Proceedings of the IEEE Power and Energy Society General Meeting, San Francisco, California, June 12-16, pp. 931-936.
- Dheepak Krishnamurthy, Wanning Li, and Leigh Tesfatsion (2016), "An 8-Zone Test System based on ISO New England Data: Development and Application" (`pdf, 636KB <http://www2.econ.iastate.edu/tesfatsi/8ZoneISONETestSystem.RevisedAppendix.pdf>`_), IEEE Transactions on Power Systems, Vol. 31, Issue 1, 2016, 234-246.
- John Lally (2002), "Financial Transmission Rights: Auction Example," in Financial Transmission Rights Draft 01-10-02, m-06 ed., ISO New England, Inc., January.
- Hongyan Li and Leigh Tesfatsion (2011), "ISO Net Surplus Collection and Allocation in Wholesale Power Markets Under Locational Marginal Pricing" (`Working Paper Version, pdf, 819KB <http://www2.econ.iastate.edu/tesfatsi/ISONetSurplus.WP09015.pdf>`_), IEEE Transactions on Power Systems, Vol. 26, No. 2, 627-641. (`DOI Location <http://dx.doi.org/10.1109/TPWRS.2010.2059052>`_)
- Hongyan Li and Leigh Tesfatsion (2012), "Co-Learning Patterns as Emergent Market Phenomena: An Electricity Market Illustration" (`WP pdf, 1.5M <http://www2.econ.iastate.edu/tesfatsi/CoLearningEmergence.LiTesWP10042.TP.June2011.pdf>`_), Journal of Economic Behavior and Organization, Volume 82, Issue 2-3, 395-419.
- Hongyan Li, Junjie Sun, and Leigh Tesfatsion (2011), "Testing Institutional Arrangements via Agent-Based Modeling: A U.S. Electricity Market Application" (`WP pdf, 2.2MB <http://www2.econ.iastate.edu/tesfatsi/LMPCorrelationStudy.LST.pdf>`_), pp. 135-158 in H. Dawid and W. Semmler (Eds.), Computational Methods in Economic Dynamics, Dynamic Modeling and Econometrics in Economics and Finance 13, Springer.
- Hongyan Li and Leigh Tesfatsion (2009), "Development of Open Source Software for Power Market Research: The AMES Test Bed" (`pdf preprint, 628KB <http://www2.econ.iastate.edu/tesfatsi/OSS_AMES.2009.pdf>`_), Journal of Energy Markets, Vol. 2, No. 2, 111-128.
- Hongyan Li and Leigh Tesfatsion (2009), "Capacity Withholding in Restructured Wholesale Power Markets: An Agent-Based Test Bed Study" (`pdf, 2.3MB <http://www2.econ.iastate.edu/tesfatsi/CapacityWithholding.PSCE2009.LiTesfatsion.pdf>`_), Proceedings of the IEEE Power Systems Conference & Exposition (PSCE), Seattle, WA, March 15-18, 2009.
- Hongyan Li, Junjie Sun, and Leigh Tesfatsion (2009),Hongyan Li, Junjie Sun, and Leigh Tesfatsion, "Separation and Volatility of Locational Marginal Prices in Restructured Wholesale Power Markets" (`pdf, 2.3MB <http://www2.econ.iastate.edu/tesfatsi/LMPSeparationVolatility.LST.pdf>`_), ISU Economics Working Paper #09009, Latest Revision March 2010.
- Hongyan Li, Junjie Sun, and Leigh Tesfatsion (2008), "Dynamic LMP Response Under Alternative Price-Cap and Price-Sensitive Demand Scenarios" (`pdf, 465KB <http://www2.econ.iastate.edu/tesfatsi/DynamicLMPResponse.IEEEPES2008.LST.pdf>`_), Proceedings of the IEEE Power and Energy Society General Meeting, Carnegie-Mellon University, Pittsburgh, July 20-24.
- Wanning Li and Leigh Tesfatsion (2017), "An 8-Zone ISO-NE Test System with Physically-Based Wind Power," (`pdf, 870KB <http://www2.econ.iastate.edu/tesfatsi/EightZoneISONETestSystemWithWind.LiTesfatsion.pdf>`_), Economics Working Paper No. 17017, Department of Economics, Iowa State University, January.
- Mohammed Shahidehpour, Hatim Yamin, and Zuyi Li (2002), Market Operations in Electric Power Systems, IEEE, Wiley-Interscience (`DOI <https://onlinelibrary.wiley.com/doi/book/10.1002/047122412X>`_).
- Abhishek Somani and Leigh Tesfatsion (2008), "An Agent-Based Test Bed Study of Wholesale Power Market Performance Measures" (`pdf, 2.8MB <http://www2.econ.iastate.edu/tesfatsi/AMESPerformanceMeasures.ASLT.IEEECIM2008.pdf>`_), IEEE Computational Intelligence Magazine, Volume 3, Number 4, November, pages 56-72.
- Junjie Sun and Leigh Tesfatsion (2007a), "Dynamic Testing of Wholesale Power Market Designs: An Open-Source Agent-Based Framework", Computational Economics, Volume 30, Number 3, pp. 291-327. (Note: This article is an abridged version of ISU Economics Working Paper No. 06025 (`pdf, 2.2MB <http://www2.econ.iastate.edu/tesfatsi/DynTestAMES.JSLT.pdf>`_), July 2007. The working paper provides a detailed description of the AMES Wholesale Power Market Test Bed V1.0 together with illustrative experimental findings.)
- Junjie Sun and Leigh Tesfatsion (2007b), "An Agent-Based Computational Laboratory for Wholesale Power Market Design" (`pdf, 724KB <http://www2.econ.iastate.edu/tesfatsi/DynTest.IEEEPES2007.JSLT.pdf>`_), Proceedings of the IEEE Power and Energy Society General Meeting, Tampa, Florida, June 2007.
- Junjie Sun and Leigh Tesfatsion (2007c), "DC Optimal Power Flow Formulation and Testing Using QuadProgJ" (`pdf, 543KB <http://www2.econ.iastate.edu/tesfatsi/DC-OPF.JSLT.pdf>`_), ISU Economics Working Paper No. 06014, Department of Economics, Iowa State University, 2007.
- Junjie Sun and Leigh Tesfatsion (2007d), "Open-Source Software for Power Industry Research, Teaching, and Training: A DC-OPF Illustration" (`pdf, 115KB <http://www2.econ.iastate.edu/tesfatsi/DC-OPF.IEEEPES2007.JSLT.pdf>`_), Proceedings of the IEEE Power and Energy Society General Meeting, Tampa, Florida, June 2007.
- Auswin G. Thomas and Leigh Tesfatsion (2018), "Braided Cobwebs: Cautionary Tales for Dynamic Pricing in Retail Electric Power Markets" (`Preprint, pdf, 546KB <http://www2.econ.iastate.edu/tesfatsi/BraidedCobwebs.ThomasTesfatsion.PreprintIEEETPWRS.pdf>`_), IEEE Transactions on Power Systems, Volume 33, Issue 6, 6870-6882.
- Steven Widergren, Junjie Sun, and Leigh Tesfatsion (2006), "Market Design Test Environments" (`pdf,136KB <http://www2.econ.iastate.edu/tesfatsi/MDTestEnvironment.2006IEEEPES.pdf>`_), Proceedings of the IEEE Power and Energy Society General Meeting, Montreal, June.

