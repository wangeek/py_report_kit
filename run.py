# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012-2013 2Vive. All Rights Reserved.
#    Author: Wang Zhenzhen <nifabric@gmail.com>
#
##############################################################################
import StringIO
import os
import subprocess
from jinja2 import Environment, PackageLoader 

class ReportKit():
    """ Use Jinja2 template to render datasource into html, and webkit engine to generate pdf, store in output.
    """

    def __init__(self,datasource, template, output, res_format):
        self.datasource = datasource
        self.template = template
        self.output = output 
        self.res_format = res_format 

    def csv_reader(self):
        """ read data from a csv into a dict
        f csv file to read
        """
        import csv
        ds = open(self.datasource,'r')
        res = [x for x in csv.DictReader(ds)]
        ds.close()
        return res

    def render2html(self, data):
        """ render a jinja2 template into steam of html using data
        """
        env = Environment(loader=PackageLoader(os.path.basename(__file__).split(".")[0],'.'))
        template = env.get_template(self.template)
        return template.stream(data)

    def run(self):
        datas = self.csv_reader()
        steam = self.render2html({'datas':datas})
        steam.dump(self.output+".html")
        if self.res_format == "pdf":
            #TODO use config file to store params
            app = os.path.dirname(os.path.abspath(__file__))+"/wkhtmltopdf"
            #command = app+" --page-size Letter --disable-smart-shrinking --dpi 300 -B 0 -L 0 -R 0 -T 0 %s %s" %(self.output+".html", self.output+".pdf")
            command = app+" --page-size Letter --disable-smart-shrinking --dpi 300 --zoom 0.772 -B 0 -L 0 -R 0 -T 0 %s %s" %(self.output+".html", self.output+".pdf")
            print command
            try:
                status = subprocess.call(command, stderr=subprocess.PIPE,shell=True)
                if status:
                    print status
            except :
                print "\n Error, do you have wkhtmltopdf installed ?"
                return False
        return True


if __name__ == "__main__":

    # handle option stuff
    from optparse import OptionParser
    import sys
    usage = "usage: %prog [options] datasource"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", dest="template", default="default.tpl.html", help="Template file to use, 'default.tpl.html' as default.")
    parser.add_option("-o", dest="output", default="output", help="file store results, 'output' as default.")
    parser.add_option("-f", dest="format", default="pdf", help="Format of result. pdf(default) or html")
    (options, args) = parser.parse_args() 
    if len(args) == 1:
        datasource = args[0]
    else:
        parser.error('need a data source file.')

    out = sys.stdout
    print >> out, "Reading data source(be patient).....",
    out.flush()
    report = ReportKit(
        datasource,
        options.template,
        options.output,
        options.format,
        )
    if report.run():
        print >> out, "done!"
    else:
        print >> out, "failed!"
