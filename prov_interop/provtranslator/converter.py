"""Manages invocation of ProvTranslator service.
"""
# Copyright (c) 2015 University of Southampton
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions: 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.  

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path
import requests

from prov_interop import http
from prov_interop import standards
from prov_interop.component import ConfigError
from prov_interop.component import RestComponent
from prov_interop.converter import ConversionError
from prov_interop.converter import Converter
from prov_interop.provtranslator import service

class ProvTranslatorConverter(Converter, RestComponent):
  """Manages invocation of ProvTranslator service."""

  def __init__(self):
    """Create converter.
    """
    super(ProvTranslatorConverter, self).__init__()

  def configure(self, config):
   """Configure converter. ``config`` must hold entries::

        url: ...endpoint URL...
        input-formats: [...list of formats from prov_interop.standards...]
        output-formats: [...list of formats from prov_interop.standards...]

    For example::

        url: https://provenance.ecs.soton.ac.uk/validator/provapi/documents/
        input-formats: [provn, ttl, trig, provx, json]
        output-formats: [provn, ttl, trig, provx, json]

    :param config: Configuration
    :type config: dict
    :raises ConfigError: if ``config`` does not hold the above entries
    """
   super(ProvTranslatorConverter, self).configure(config)

  def convert(self, in_file, out_file):
    """Convert input file into output file. Each file must have an
    extension matching a format in ``prov_interop.standards``.

    :param in_file: Input file name
    :type in_file: str or unicode
    :param out_file: Output file name
    :type out_file: str or unicode
    :raises ConversionError: if the input file is not found, or the
    HTTP response is not 200
    :raises requests.exceptions.ConnectionError: if there are problems
    executing the request e.g. the URL cannot be found
    """
    super(ProvTranslatorConverter, self).convert(in_file, out_file)
    in_format = os.path.splitext(in_file)[1][1:]
    out_format = os.path.splitext(out_file)[1][1:]
    super(ProvTranslatorConverter, self).check_formats(in_format, out_format)
    with open(in_file, "r") as f:
      doc_str = f.read()
    (response_code, response_text) = service.translate(self._url, 
                                                       in_format, 
                                                       out_format, 
                                                       doc_str)
    if (response_code != requests.codes.ok): # 200 OK
      raise ConversionError(self._url + " POST returned " + 
                            str(response_code))
    with open(out_file, "w") as f:
      f.write(response_text)