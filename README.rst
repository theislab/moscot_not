|Codecov|

moscot - multi-omic single-cell optimal transport tools
=======================================================

This repository extends **moscot** with neural OT (``NOT``) solvers including the implementation of the single-cell trajecotry experiments from 
**"Unbalancedness in Neural Monge Maps Improves Unpaired Domain Translation" [ICLR 2024]** (https://arxiv.org/abs/2311.15100).

For the main repository of our paper, please refer to https://github.com/ExplainableML/uot-fm.

**Moscot** is a scalable framework for Optimal Transport (OT) applications in single-cell genomics. It can be used for

- trajectory inference (incorporating spatial and lineage information)
- mapping cells to their spatial organisation
- aligning spatial transcriptomics slides
- translating modalities
- prototyping of new OT models in single-cell genomics

It is powered by `OTT <https://ott-jax.readthedocs.io>`_ which is a JAX-based Optimal Transport toolkit that supports just-in-time compilation, GPU acceleration, automatic differentiation and linear memory complexity for OT problems. For more information, please have a look at our `documentation <https://moscot.readthedocs.io>`_. 

Installation
------------
We recommend first install `jax<=0.4.23` for GPU support as described in https://jax.readthedocs.io/en/latest/installation.html.

Next, in order to install **moscot_not** from source, run::

    git clone https://github.com/theislab/moscot_not
    cd moscot
    pip install -e .

Additionaly, to run the downstream analysis of the single-cell trajectory inference experiments, please also install **cellrank** as described in https://cellrank.readthedocs.io/en/stable/installation.html.

Single-cell Trajectory Inference with OT-ICNN
------------

To reproduce the single-cell trajecotry inference results using ``OT-ICNN`` and ``UOT-ICNN`` from the Unbalancedness paper, please first download the preprocessed dataset `here <https://figshare.com/articles/dataset/pancreas_1415_h5ad/25151984>`_.
Afterwards, you can find the corresponding notebooks in ``/notebooks``.


.. |Codecov| image:: https://codecov.io/gh/theislab/moscot/branch/master/graph/badge.svg?token=Rgtm5Tsblo
    :target: https://codecov.io/gh/theislab/moscot
    :alt: Coverage