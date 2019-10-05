from .classes import Matrix, Spots, Regions


# TODO add more data to s3, add to this module.
class osmFISH:

    @staticmethod
    def matrix():
        url = ("s3://starspace.data/formatted/osmfish_codeluppi_2018_nat-methods_somatosensory-cortex/" 
               "osmfish-codeluppi-2018-nat-methods-somatosensory-cortex.matrix.zarr/")
        return Matrix.load_zarr(url)

    @staticmethod
    def spots():
        url = ("s3://starspace.data/formatted/osmfish_codeluppi_2018_nat-methods_somatosensory-cortex/"
               "osmfish-codeluppi-2018-nat-methods-somatosensory-cortex.spots.zarr/")
        return Spots.load_zarr(url)

    @staticmethod
    def regions():
        url = ("s3://starspace.data/formatted/osmfish_codeluppi_2018_nat-methods_somatosensory-cortex/"
               "osmfish-codeluppi-2018-nat-methods-somatosensory-cortex.regions.zarr/")
        return Regions.load_zarr(url)
