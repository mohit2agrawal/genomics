#!/usr/bin/env python
#
#     demultiplex_undetermined_fastq.py: demultiplex undetermined Illumina reads
#     Copyright (C) University of Manchester 2013 Peter Briggs
#
########################################################################
#
# demultiplex_undetermined_fastq.py
#
#########################################################################

"""demultiplex_undetermined_fastq.py

Attempts to demultiplex the reads in the "Undetermined_indices" directory
produced by a CASAVA run, by barcode (i.e. index sequences) matching in
the read headers.

This program was originally written to deal with HiSEQ data where
dual-indexed and single indexed barcoding protocols were mixed in the same
sequencing run.

"""

#######################################################################
# Import modules that this module depends on
#######################################################################

__version__ = "0.0.1"

import os
import sys
import optparse

# Put .. onto Python search path for modules
SHARE_DIR = os.path.abspath(
    os.path.normpath(
        os.path.join(os.path.dirname(sys.argv[0]),'..')))
sys.path.append(SHARE_DIR)
import bcftbx.IlluminaData as IlluminaData
import bcftbx.FASTQFile as FASTQFile

#######################################################################
# Class definitions
#######################################################################

class BarcodeMatcher:
    """BarcodeMatcher

    Class for testing whether a sequence matches a barcode.

    Example usage:
    >>> b = BarcodeMatcher("ACCTAG")
    >>> b.match("ACCTAC") # returns False, exact match required
    >>> b.match("ACCTAC",max_mismatches=1) # returns True, one mismatch

    """

    def __init__(self,barcode):
        """Create a new BarcodeMatcher

        Arguments:
          barcode: barcode (i.e. index) sequence to test against

        """
        self.__barcode = barcode

    @property
    def barcode(self):
        """Return the stored barcode/index sequence.

        """
        return self.__barcode

    def match(self,test_barcode,max_mismatches=0):
        """Test a barcode/index sequence against the stored sequence

        Arguments:
          test_barcode: barcode/index sequence being tested
          max_mismatches: maximum number of mismatches allowed while
            still considering the two sequences to match (default is
            zero i.e. no mismatches)

        Returns:
          True if test barcode matches the reference, False otherwise.

        """
        if test_barcode.startswith(self.__barcode):
            return True
        nmismatches = 0
        try:
            for i in range(len(self.__barcode)):
                if test_barcode[i] != self.__barcode[i]:
                    nmismatches += 1
                    if nmismatches > max_mismatches:
                        return False
        except IndexError:
            return False
        return True

#######################################################################
# Module Functions
#######################################################################

def demultiplex_fastq(fastq_file,barcodes,nmismatches):
    """Perform demultiplexing of a FASTQ file

    Demultiplex reads in a FASTQ file given information about a set of 
    barcode/index sequences.

    Produces a file for each barcode, plus another for 'unbinned'
    reads.

    Arguments:
      fastq_file: FASTQ file to be demultiplexed (can be gzipped)
      barcodes: list of barcode sequences to use for demultiplexing
      nmismatches: maxiumum number of mismatched bases allowed when
        testing whether barcode sequences match

    Returns:
      No return value
    """
    # Start
    print "Processing %s" % fastq_file
    info = IlluminaData.IlluminaFastq(fastq_file)
    # Set up output files
    output_files = {}
    # Weed out barcodes that aren't associated with this lane
    local_barcodes = []
    for barcode in barcodes:
        if barcode['lane'] != info.lane_number:
            continue
        local_barcodes.append(barcode)
        output_file_name = "%s_%s_L%03d_R%d_%03d.fastq" % (barcode['name'],
                                                           barcode['index'],
                                                           info.lane_number,
                                                           info.read_number,
                                                           info.set_number)
        print "\t%s\t%s" % (barcode['index'],output_file_name)
        if os.path.exists(output_file_name):
            print "\t%s: already exists,exiting" % output_file_name
            sys.exit(1)
        output_files[barcode['index']] = open(output_file_name,'w')
    # Check if there's anything to do
    if len(local_barcodes) == 0:
        return
    # Also make a file for unbinned reads
    unbinned_file_name = "unbinned_L%03d_R%d_%03d.fastq" % (info.lane_number,
                                                            info.read_number,
                                                            info.set_number)
    if os.path.exists(unbinned_file_name):
        print "\t%s: already exists,exiting" % unbinned_file_name
        sys.exit(1)
    output_files['unbinned'] = open(unbinned_file_name,'w')
    # Process reads
    nreads = 0
    for read in FASTQFile.FastqIterator(fastq_file):
        nreads += 1
        matched_read = False
        this_barcode = read.seqid.index_sequence
        for barcode in local_barcodes:
            if barcode['matcher'].match(this_barcode,nmismatches):
                ##print "Matched %s against %s" % (this_barcode,barcodes[barcode]['name'])
                output_files[barcode['index']].write(str(read)+'\n')
                matched_read = True
                break
        # Put in unbinned if no match
        if not matched_read:
            output_files['unbinned'].write(str(read)+'\n')
        ##if nreads > 100: break
    # Close files
    for barcode in local_barcodes:
        output_files[barcode['index']].close()
    print "\tMatched %d reads for %s" % (nreads,os.path.basename(fastq_file))

#######################################################################
# Main program
#######################################################################

if __name__ == "__main__":

    # Create command line parser
    p = optparse.OptionParser(usage="%prog OPTIONS DIR",
                              version="%prog "+__version__,
                              description="Reassign reads with undetermined index sequences. "
                              "(i.e. barcodes). DIR is the name (including any leading path) "
                              "of the 'Undetermined_indices' directory produced by CASAVA, "
                              "which contains the FASTQ files with the undetermined reads from "
                              "each lane.")
    p.add_option("--barcode",action="append",dest="barcode_info",default=[],
                 help="specify barcode sequence and corresponding sample name as BARCODE_INFO. "
                 "The syntax is '<name>:<barcode>:<lane>' e.g. --barcode=PB1:ATTAGA:3")
    p.add_option("--samplesheet",action="store",dest="sample_sheet",default=None,
                 help="specify SampleSheet.csv file to read barcodes, sample names and lane "
                 "assignments from (as an alternative to --barcode).")

    # Parse command line
    options,args = p.parse_args()

    # Get data directory name
    if len(args) != 1:
        p.error("expected one argument (location of undetermined index reads)")
    undetermined_dir = os.path.abspath(args[0])

    # Set up barcode data
    barcodes = []
    for barcode_info in options.barcode_info:
        name,barcode,lane = barcode_info.split(':')
        print "Assigning barcode '%s' in lane %s to %s" % (barcode,lane,name)
        barcodes.append({ 'name': name,
                          'index': barcode,
                          'matcher': BarcodeMatcher(barcode),
                          'lane': int(lane)})

    # Read from sample sheet (if supplied)
    if options.sample_sheet is not None:
        print "Reading data from sample sheet %s" % options.sample_sheet
        sample_sheet = IlluminaData.CasavaSampleSheet(options.sample_sheet)
        for line in sample_sheet:
            name = line['SampleID']
            barcode = line['Index'].rstrip('N').rstrip('-').rstrip('N')
            lane = line['Lane']
            print "Assigning barcode '%s' in lane %s to %s" % (barcode,lane,name)
            barcodes.append({ 'name': name,
                              'index': barcode,
                              'matcher': BarcodeMatcher(barcode),
                              'lane': int(lane) })
    if len(barcodes) < 1:
        p.error("need at least one --barcode and/or --samplesheet assignment")

    # Collect input files
    p = IlluminaData.IlluminaProject(undetermined_dir)

    # Loop over "samples" and match barcodes
    for s in p.samples:
        for fq in s.fastq:
            fastq = os.path.join(s.dirn,fq)
            demultiplex_fastq(fastq,barcodes,1)
    print "Finished"

