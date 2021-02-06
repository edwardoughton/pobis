Policy Options for Digital Infrastructure Strategies (podis)
============================================================
[![Build Status](https://travis-ci.org/edwardoughton/podis.svg?branch=master)](https://travis-ci.org/edwardoughton/podis)
[![Coverage Status](https://coveralls.io/repos/github/edwardoughton/podis/badge.svg?branch=master)](https://coveralls.io/github/edwardoughton/podis?branch=master)

**podis** allows transparent and reproducible analysis of policy options for improving
digital infrastructure connectivity, thus contributing to sustainable economic development.

The simulation model available in this repository can be applied to local, national or regional
telecommunication markets, to quantify the performance of different technology, business model
or regional integration options. The evidence produced can be used to inform the design of
digital infrastructure strategies.

Citation
---------

- Oughton, E.J. (2021) Policy options for digital infrastructure strategies: A simulation
  model for broadband universal service in Africa. arXiv:3592803  [cs, econ, q-fin].


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

## Quantifying broadband strategies with data analytics

<p align="center">
  <img src="/figures/approach.png" />
</p>

The composition of the private cost is visualized below for each technology tested,
demonstrating the structure of the investment required to achieve comprehensive universal
broadband across the six example countries assessed here (Côte D’Ivoire, Mali, Senegal, Kenya,
Tanzania and Uganda).

## Composition of the private cost structure by country

<p align="center">
  <img src="/figures/private_cost.png" />
</p>

In those circumstances where the revenue able to support infrastructure deployment falls short
of the required investment, areas are therefore unviable based on current market conditions.
Consequently, government is required to provide a state subsidy to help deploy the required
infrastructure in these situations. The figure below demonstrates how `podis` is able to
estimate the required state subsidy needed to achieve universal broadband.

## Quantifying state subsidies for universal broadband

<p align="center">
  <img src="/figures/government_cost.png" />
</p>


Using conda
==========

The recommended installation method is to use conda, which handles packages and virtual
environments, along with the conda-forge channel which has a host of pre-built libraries and
packages.

Create a conda environment called podis:

    conda create --name podis python=3.7 gdal

Activate it (run this each time you switch projects):

    conda activate podis

First, install optional packages:

    conda install geopandas rasterio rasterstats

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

First run the following initial preprocessing script to extract the necessary files:

    python scripts/preprocess.py

Then

    python scripts/core.py


Acknowledgements
================

**podis** was developed at George Mason University, Fairfax, VA, USA.

Support from collaborators at the World Bank's Digital Economy for Africa program has been very
much appreciated.

Thank you to the Benton Institute for Broadband & Society and TPRC Board for recognizing this
paper at TPRC48 with a Charles Benton Early Career Scholar Award.
