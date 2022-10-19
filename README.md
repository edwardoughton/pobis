Policy Options for Broadband Infrastructure Strategies (podis)
============================================================
[![Build Status](https://travis-ci.org/edwardoughton/podis.svg?branch=master)](https://travis-ci.org/edwardoughton/podis)
[![Coverage Status](https://coveralls.io/repos/github/edwardoughton/podis/badge.svg?branch=master)](https://coveralls.io/github/edwardoughton/podis?branch=master)

**podis** allows transparent and reproducible analysis of policy options for improving
broadband infrastructure connectivity, thus contributing to sustainable economic development.

The simulation model available in this repository can be applied to local, national or regional
telecommunication markets, to quantify the performance of different technologies or business
models. The evidence produced can be used to inform the design of
broadband infrastructure strategies.

Citation
---------

- Oughton, E., 2021. Policy options for digital infrastructure strategies: A simulation model
  for broadband universal service in Africa. arXiv:2102.03561 [cs, econ, q-fin].


Data analytics for broadband strategies
=======================================
Myriad high-level policy reports have attempted to quantify the costs of infrastructure
delivery for connecting unconnected communities. The majority use spreadsheet methods to
estimate the required investment, leaving substantial uncertainty embedded within the results
which is rarely portrayed to policy makers.

The method developed here takes a new approach by drawing on a range of analytical tools rarely
utilized in telecom policy research, including remote sensing and least-cost network designs
derived from infrastructure simulation. The figure below illustrates how these approaches are
combined to produce demand and supply estimates to quantify broadband universal service
strategies.

## Example analytical approach

<p align="center">
  <img src="/figures/approach.png" />
</p>

As `podis` functions in a spatially disaggregated way, it is possible to convert detailed
local modeling into continent-wide assessment of universal broadband. In the table below,
the necessary investment per decile is reported for the whole of Africa, based on the
private cost, net government cost, and the total financial cost.

## The financial cost of universal broadband for the African continent

<p align="center">
  <img src="/figures/validation_10_mbps.png" />
</p>

Investment costs by `podis` are able to be converted into disaggregated estimates, as
demonstrated below.

## Continental assessment of universal broadband costs by user location across Africa

<p align="center">
  <img src="/figures/z_cost_per_user_spatially_Financial_10_mbps.png" />
</p>

Using conda
==========

The recommended installation method is to use conda, which handles packages and virtual
environments, along with the conda-forge channel which has a host of pre-built libraries and packages.

Create a conda environment called podis:

    conda create --name podis python=3.7 gdal

Activate it (run this each time you switch projects):

    conda activate podis

First, install required packages:

    conda install geopandas rasterio rasterstats networkx seaborn descartes

Then install podis:

    python setup.py install

Alternatively, for development purposes, clone this repo and run:

    python setup.py develop


Download necessary data
=======================

You will need numerous input data sets.

First, download the Global Administrative Database (GADM), following the link below and making
sure you download the "six separate layers.":

- https://gadm.org/download_world.html

Place the data into the following path `data/raw/gadm36_levels_shp`.

Then download the WorldPop global settlement data from:

- https://www.worldpop.org/geodata/summary?id=24777.

Place the data in `data/raw/settlement_layer`.

Next, download the nightlight data here:

https://ngdc.noaa.gov/eog/data/web_data/v4composites/F182013.v4.tar

Place the unzipped data in `data/raw/nightlights/2013`.

Obtain the Mobile Coverage Explorer data from Collins Bartholomew:

https://www.collinsbartholomew.com/mobile-coverage-maps/mobile-coverage-explorer/

Place the data into `data/raw/Mobile Coverage Explorer`.

Once complete, run the following to preprocess all data:

    python scripts/preprocess.py


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

**podis** was developed at George Mason University, Fairfax, VA, USA.

Guidance and support has been very much appreciated from collaborators at the World Bank's
Digital Economy for Africa program.

Thank you to both the Benton Institute for Broadband & Society and the TPRC Board for
recognizing this paper at TPRC48 with a Charles Benton Early Career Scholar Award.
