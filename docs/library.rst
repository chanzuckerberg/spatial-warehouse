.. _data:

Working with Data
=================

The starspace library defines a very simple set of objects to read and manipulate the :py:class:`Spots`,
:py:class:`Matrix`, and :py:class:`Regions` objects. Each object subclasses an :py:class:`xarray.Dataset` or
:py:class:`xarray.DataArray` object, meaning that they can be used the same way one would use an :py:mod:`xarray`
object. For those more familiar with :py:mod:`numpy` or :py:mod:`pandas`, there are simple ways to drop out of
:py:mod:`xarray`, and for those that are more familiar with R and wish to use that language, we show how to serialize
each object into a format that can be loaded into R.

For ease of use, starspace packages some pre-formatted data, which is stored in :py:mod:`starspace.data`. These data
are used in the below examples.

Matrix
======

Serialization options
---------------------

starspace defines two special serialization routines for the :py:class:`Matrix` object to improve usability with
downstream genomics packages.

.. code-block:: python

    import starspace
    matrix = starspace.data.osmFISH.matrix()

    # save to loom for reading in R
    matrix.to_loom("osmFISH.loom")

    # convert to anndata for use with scanpy
    adata = matrix.to_anndata()
    # optionally, save to disk
    adata.save("osmFISH.h5ad")

Because starspace subclasses :py:mod:`xarray.DataArray`, it can also take advantage of any of the
`xarray serialization routines`_, for example:

.. _xarray serialization routines: http://xarray.pydata.org/en/stable/io.html

.. code-block:: python

    matrix.to_netcdf("osmFISH.nc")

Extracting column or row metadata
---------------------------------
Turn row or column metadata into a tidy :py:mod:`pandas.Dataframe`:

.. code-block:: python

    import starspace
    matrix = starspace.data.osmFISH.matrix()

    # pandas dataframe
    col_metadata = matrix.column_metadata()
    # pandas dataframe
    row_metadata = matrix.row_metadata()

To extract cell x gene expression data into a :py:mod:`numpy.array`:

.. code-block:: python

    import starspace
    matrix = starspace.data.osmFISH.matrix()

    # numpy array
    data = matrix.values

For more information on how to work with :py:mod:`xarray` objects, see `their documentation`_

.. _their documentation: http://xarray.pydata.org/en/stable/index.html

Spots
=====

Spots is a simple tidy columnar data file that records the positions and identity of each spot. Because of this
structure, it is simple to turn it into a :py:mod:`pandas.DataFrame`:

.. code-block:: python

    import starspace
    spots = starspace.data.osmFISH.spots()

    # pandas dataframe
    df = spots.to_dataframe()

From pandas, one an serialize the :py:mod:`pandas.Dataframe` a number of ways, including to :code:`.csv`:

.. code-block:: python

    df.to_csv('osmFISH_spots.csv')

see the `Pandas documentation`_ for more information.

.. _Pandas documentation: https://pandas.pydata.org/pandas-docs/stable/reference/frame.html#serialization-io-conversion

Regions
=======

Regions is a `Dask`_-serialized label image. We use dask to enable large images, often bigger than would fit in memory,
to be easily manipulated. For images that fit in memory, they can be easily converted into numpy arrays for downstream
processing:

.. _Dask: https://docs.dask.org/en/latest/

.. code-block:: python

    import starspace
    regions = starspace.data.osmFISH.regions()

    # numpy array
    data = regions.values
