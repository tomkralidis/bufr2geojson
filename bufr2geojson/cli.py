###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import json
import logging
import os.path
from pathlib import Path
import sys
from csv import QUOTE_NONNUMERIC
import click

from bufr2geojson import __version__, BUFRParser, transform as as_geojson

LOGGER = logging.getLogger(__name__)
THISDIR = os.path.dirname(os.path.realpath(__file__))

def cli_option_verbosity(f):
    logging_options = ["ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]

    def callback(ctx, param, value):
        if value is not None:
            logging.basicConfig(stream=sys.stdout,
                                level=getattr(logging, value))
        return True

    return click.option("--verbosity", "-v",
                        type=click.Choice(logging_options),
                        help="Verbosity",
                        callback=callback)(f)


def cli_callbacks(f):
    f = cli_option_verbosity(f)
    return f


@click.group()
@click.version_option(version=__version__)
def cli():
    """bufr2geojson"""
    pass

@click.command()
@click.pass_context
@click.argument("bufr_file", type=click.File(errors="ignore"))
@click.option("--output-dir", "output_dir", required=True,
              help="Name of output file")
@click.option("--csv", "write_csv", required=False, default=False, help=
              "write CSV output as well")
@cli_option_verbosity
def transform(ctx, bufr_file, output_dir, write_csv, verbosity):
    result = None
    LOGGER.info(f"Transforming {bufr_file.name} to geojson")
    geojson = as_geojson(bufr_file)
    outfile = Path(bufr_file.name).stem
    for key in geojson:
        outfile_key = f"{output_dir}{os.sep}{outfile}-{key}.json"
        with open(outfile_key,"w") as fh:
            fh.write(json.dumps(geojson[key]["geojson"], indent=4))
        if write_csv:
            outfile_key = f"{output_dir}{os.sep}{outfile}-{key}_metadata.csv"
            geojson[key]["metadata.csv"].to_csv(outfile_key, index=False, quoting=QUOTE_NONNUMERIC, na_rep="NA")  # noqa
            outfile_key = f"{output_dir}{os.sep}{outfile}-{key}_records.csv"
            geojson[key]["records.csv"].to_csv(outfile_key, index=False, quoting=QUOTE_NONNUMERIC, na_rep="NA")  # noqa

    LOGGER.info("Done")
    
cli.add_command(transform)