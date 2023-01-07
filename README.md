Policy Options for Broadband Infrastructure Strategies (podis)
============================================================
[![Build Status](https://travis-ci.org/edwardoughton/podis.svg?branch=master)](https://travis-ci.org/edwardoughton/podis)
[![Coverage Status](https://coveralls.io/repos/github/edwardoughton/podis/badge.svg?branch=master)](https://coveralls.io/github/edwardoughton/podis?branch=master)

**pobis** allows transparent and reproducible analysis of policy options for improving mobile
broadband infrastructure connectivity.

The simulation model available in this repository can be applied to local, national or regional
telecommunication markets, to quantify the performance of different technologies or business
models. The evidence produced can be used to inform the design of
broadband infrastructure strategies.

Citation
---------

- Oughton, E.J. (2023) ‘Policy Options for Broadband Infrastructure Strategies: A Simulation Model for Affordable Universal Broadband in Africa’. Telematics and Informatics 76 (January): 101908. https://doi.org/10.1016/j.tele.2022.101908.


## Example analytical approach

<p align="center">
  <img src="/figures/approach.png" />
</p>

As `pobis` functions in a spatially disaggregated way, it is possible to convert detailed
local modeling into continent-wide assessment of universal broadband. In the table below,
the necessary investment per decile is reported for the whole of Africa, based on the
private cost, net government cost, and the total financial cost.

## Assessment of universal mobile broadband across Africa

<p align="center">
  <img src="/figures/a.png" />
</p>

Using conda
==========

The recommended installation method is to use conda, which handles packages and virtual
environments, along with the conda-forge channel which has a host of pre-built libraries and packages.

Create a conda environment called pobis:

    conda create --name pobis python=3.7 gdal

Activate it (run this each time you switch projects):

    conda activate pobis

First, install required packages:

    conda install geopandas rasterio rasterstats networkx seaborn descartes

Then install pobis:

    python setup.py install

Alternatively, for development purposes, clone this repo and run:

    python setup.py develop


Download necessary data
=======================

You will need numerous input data sets. See the published paper for a full summary.


Using the model
===============

First, if you have site data, run the following initial preprocessing script:

    python scripts/prep1.py

Then run the second preprocessing script, as follows:

    python scripts/prep2.py

You can then run the model for the countries selected for detailed modeling:

    python scripts/run.py

Next, we then need to prep data for all African countries before scaling the results:

    python scripts/prep_uba.py

And now we can estimate the costs of all African countries:

    python scripts/user_costs.py

If you want to know the percentage savings between strategies, run:

    python scripts/percentages.py


Plotting results
===============

The `vis` folder contains visualization scripts to generate plots in R (`plots.r`).
To plot the maps for the African continent the following script can be executed:

    python vis/vis.py


Acknowledgements
================

**pobis** was developed at George Mason University, Fairfax, VA, USA.

Guidance and support has been very much appreciated from collaborators at the World Bank's
Digital Economy for Africa program.

Thank you to both the Benton Institute for Broadband & Society and the TPRC Board for
recognizing this paper at TPRC48 with a Charles Benton Early Career Scholar Award.
