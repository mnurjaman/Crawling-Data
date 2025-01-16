# from urllib.parse import urljoin, urlparse


# def is_valid_url(url):
#     """
#     Memeriksa apakah sebuah URL valid
#     """
#     try:
#         result = urlparse(url)
#         return all([result.scheme, result.netloc])
#     except:
#         return False


# def get_domain(url):
#     """
#     Mengambil domain dari sebuah URL
#     """
#     parsed_uri = urlparse(url)
#     return "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)


# # Re-export urljoin untuk konsistensi
# urljoin = urljoin
