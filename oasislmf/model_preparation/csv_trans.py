# -*- coding: utf-8 -*-

__all__ = [
    'Translator'
]

import json
import logging
#import multiprocessing
import os

import pandas as pd

from lxml import etree

#from oasislmf.utils.concurrency import (
#    multiprocess,
#    multithread,
#    Task,
#)
from oasislmf.utils.exceptions import OasisException


class Translator(object):
    def __init__(self, input_path, output_path, xslt_path, xsd_path=None, append_row_nums=False, chunk_size=100000, logger=None):
        """
        Transforms exposures/locations in CSV format
        by converting a source file to XML and applying an XSLT transform
        to apply rules for selecting, merging or updating columns

        An optional step is to passing an XSD file for output validation

        :param input_path: Source exposures file path, which should be in CSV comma delimited format
        :type input_path: str

        :param output_path: File to write transform results
        :type output_path: str

        :param xslt_path: Source exposures Transformation rules file
        :type xslt_path: str

        :param xsd_path: Source exposures output validation file
        :type xsd_path: str

        :param append_row_nums: Append line numbers to first column of output called `ROW_ID` [1 .. n] when n is the number of rows processed.
        :type append_row_nums: boolean

        :param chunk_size: Number of rows to process per multiprocess Task
        :type chunk_size: int
        """

        self.logger = logger or logging.getLogger()
        self.xsd = (etree.parse(xsd_path) if xsd_path else None)
        self.xslt = etree.parse(xslt_path)
        self.fpath_input = input_path
        self.fpath_output = output_path
        self.chunk_size = chunk_size

        self.row_nums = append_row_nums
        self.row_limit = chunk_size
        self.row_header_in = None
        self.row_header_out = None

    def __call__(self):

        c=0

        for df_in in pd.read_csv(self.fpath_input,chunksize=self.chunk_size,encoding='utf-8'):
            headers = df_in.columns
            df_in = df_in.fillna("").values.astype("unicode").tolist()

            root = etree.Element('root')

            for row in df_in:
                rec = etree.SubElement(root, 'rec')
                for i in range(0, len(row)):
                    if(row[i] not in [None, "", 'NaN']):
                        rec.set(headers[i], row[i])

            #xslt_o = etree.parse(self.xslt)

            lxml_transform = etree.XSLT(self.xslt)

            dest = lxml_transform(root)
            root_dest = dest.getroot()

            row_header_out = root_dest[0].keys()

            rows = []

            for rec in root_dest:
                rows.append(dict(rec.attrib))

            df_out = pd.DataFrame(rows, columns=row_header_out)

            if self.row_nums:
                df_out['ROW_ID']=df_out.index+1+(c*self.chunk_size)
                new_row_header_out = ['ROW_ID']
                for header_item in row_header_out:
                    new_row_header_out.append(header_item)
                row_header_out = new_row_header_out
                df_out=df_out[row_header_out]
                #self.logger.info(row_header_out)

            if not os.path.isfile(self.fpath_output):
                df_out.to_csv(self.fpath_output, header=row_header_out,index=False)
            else:
                df_out.to_csv(self.fpath_output, mode='a', header=False,index=False)

            c=c+1
            self.logger.info("done chunk {}, {} rows".format(c,c*self.chunk_size))
