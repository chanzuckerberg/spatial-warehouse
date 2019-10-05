.. _contributing:

Contributing
============

This package is only as useful as the data that exist in the format it specifies. We eagerly encourage contribution
of datasets, and would be happy to work to evolve the schema.

To contribute to the schema or library, or to add formatted data, please begin by `opening an issue`_ to discuss the
proposed contribution. For data additions, the contribution process is simple: add a conversion example to
:code:`/conversion_examples` that reads the data from a publicly accessible repository. We will run the script, upload
the data to the :py:mod:`starspace` amazon s3 bucket, and add the contributed data to :py:mod:`starspace.data`
Optionally, you can add a notebook to :code:`/analysis_examples` demonstrating how the data can be navigated and showing
off the cool features of your spatial dataset!

.. _opening an issue: https://github.com/chanzuckerberg/spatial-warehouse/issues/new
