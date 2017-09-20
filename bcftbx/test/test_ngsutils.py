#######################################################################
# Tests for ngsutils.py module
#######################################################################
import unittest
import os
import tempfile
import shutil
import gzip
from bcftbx.ngsutils import *

class TestGetreadsFunction(unittest.TestCase):
    """Tests for the 'getreads' function
    """
    def setUp(self):
        self.wd = tempfile.mkdtemp()
        self.example_fastq_data = """@K00311:43:HL3LWBBXX:8:1101:21440:1121 1:N:0:CNATGT
GCCNGACAGCAGAAAT
+
AAF#FJJJJJJJJJJJ
@K00311:43:HL3LWBBXX:8:1101:21460:1121 1:N:0:CNATGT
GGGNGTCATTGATCAT
+
AAF#FJJJJJJJJJJJ
@K00311:43:HL3LWBBXX:8:1101:21805:1121 1:N:0:CNATGT
CCCNACCCTTGCCTAC
+
AAF#FJJJJJJJJJJJ
"""
        self.example_csfasta_data = """# Cwd: /home/pipeline
# Title: solid0127_20121204_FRAG_BC_Run_56_pool_LC_CK
>1_51_38_F3
T3..3.213.12211.01..000..111.0210202221221121011..0
>1_51_301_F3
T0..3.222.21233.00..022..110.0210022323223202211..2
>1_52_339_F3
T1.311202211102.331233332113.23332233002223222312.2
"""
        self.example_qual_data = """# Cwd: /home/pipeline
# Title: solid0127_20121204_FRAG_BC_Run_56_pool_LC_CK
>1_51_38_F3
16 -1 -1 5 -1 24 15 12 -1 21 12 16 22 19 -1 26 13 -1 -1 4 21 4 -1 -1 4 7 9 -1 4 5 4 4 4 4 4 13 4 4 4 5 4 4 10 4 4 4 4 -1 -1 4 
>1_51_301_F3
22 -1 -1 4 -1 24 30 7 -1 4 9 26 6 16 -1 25 25 -1 -1 17 18 13 -1 -1 4 14 24 -1 4 14 17 32 4 7 13 13 22 4 12 19 4 24 6 9 8 4 4 -1 -1 9 
>1_52_339_F3
27 -1 33 24 28 32 29 17 25 27 26 30 30 31 -1 28 33 19 19 13 4 20 21 13 5 4 12 -1 4 23 13 8 4 10 4 6 5 7 4 8 4 8 12 5 12 10 8 7 -1 4
"""
    def tearDown(self):
        shutil.rmtree(self.wd)
    def test_getreads_fastq(self):
        """getreads: read records from Fastq file
        """
        # Make an example file
        example_fastq = os.path.join(self.wd,"example.fastq")
        with open(example_fastq,'w') as fp:
            fp.write(self.example_fastq_data)
        # Read lines
        fastq_reads = getreads(example_fastq)
        reference_reads = [self.example_fastq_data.split('\n')[i:i+4]
                           for i
                           in xrange(0,
                                     len(self.example_fastq_data.split('\n')),
                                     4)]
        for r1,r2 in zip(reference_reads,fastq_reads):
            self.assertEqual(r1,r2)
    def test_getreads_gzipped_fastq(self):
        """getreads: read records from gzipped Fastq file
        """
        # Make an example file
        example_fastq = os.path.join(self.wd,"example.fastq.gz")
        with gzip.open(example_fastq,'w') as fp:
            fp.write(self.example_fastq_data)
        # Read lines
        fastq_reads = getreads(example_fastq)
        reference_reads = [self.example_fastq_data.split('\n')[i:i+4]
                           for i
                           in xrange(0,
                                     len(self.example_fastq_data.split('\n')),
                                     4)]
        for r1,r2 in zip(reference_reads,fastq_reads):
            self.assertEqual(r1,r2)
    def test_getreads_csfasta(self):
        """getreads: read records from csfasta file
        """
        # Make an example file
        example_csfasta = os.path.join(self.wd,"example.csfasta")
        with open(example_csfasta,'w') as fp:
            fp.write(self.example_csfasta_data)
        # Read lines
        csfasta_reads = getreads(example_csfasta)
        reference_reads = [self.example_csfasta_data.split('\n')[i:i+2]
                           for i
                           in xrange(2,
                                     len(self.example_fastq_data.split('\n')),
                                     2)]
        for r1,r2 in zip(reference_reads,csfasta_reads):
            self.assertEqual(r1,r2)
    def test_getreads_qual(self):
        """getreads: read records from qual file
        """
        # Make an example file
        example_qual = os.path.join(self.wd,"example.qual")
        with open(example_qual,'w') as fp:
            fp.write(self.example_qual_data)
        # Read lines
        qual_reads = getreads(example_qual)
        reference_reads = [self.example_qual_data.split('\n')[i:i+2]
                           for i
                           in xrange(2,
                                     len(self.example_qual_data.split('\n')),
                                     2)]
        for r1,r2 in zip(reference_reads,qual_reads):
            self.assertEqual(r1,r2)

class TestGetreadsSubsetFunction(unittest.TestCase):
    """Tests for the 'getreads_subset' function
    """
    def setUp(self):
        self.wd = tempfile.mkdtemp()
        self.example_fastq_data = """@K00311:43:HL3LWBBXX:8:1101:21440:1121 1:N:0:CNATGT
GCCNGACAGCAGAAAT
+
AAF#FJJJJJJJJJJJ
@K00311:43:HL3LWBBXX:8:1101:21460:1121 1:N:0:CNATGT
GGGNGTCATTGATCAT
+
AAF#FJJJJJJJJJJJ
@K00311:43:HL3LWBBXX:8:1101:21805:1121 1:N:0:CNATGT
CCCNACCCTTGCCTAC
+
AAF#FJJJJJJJJJJJ
"""
    def tearDown(self):
        shutil.rmtree(self.wd)
    def test_getreads_subset_fastq(self):
        """getreads: get subset of reads from Fastq file
        """
        # Make an example file
        example_fastq = os.path.join(self.wd,"example.fastq")
        with open(example_fastq,'w') as fp:
            fp.write(self.example_fastq_data)
        # Get subset
        fastq_reads = getreads_subset(example_fastq,
                                      indices=(0,2))
        reference_reads = [self.example_fastq_data.split('\n')[i:i+4]
                           for i in (0,8)]
        for r1,r2 in zip(reference_reads,fastq_reads):
            self.assertEqual(r1,r2)

class TestGetreadsRegexpFunction(unittest.TestCase):
    """Tests for the 'getreads_regex' function
    """
    def setUp(self):
        self.wd = tempfile.mkdtemp()
        self.example_fastq_data = """@K00311:43:HL3LWBBXX:8:1101:21440:1121 1:N:0:CNATGT
GCCNGACAGCAGAAAT
+
AAF#FJJJJJJJJJJJ
@K00311:43:HL3LWBBXX:8:1101:21460:1121 1:N:0:CNATGT
GGGNGTCATTGATCAT
+
AAF#FJJJJJJJJJJJ
@K00311:43:HL3LWBBXX:8:1101:21805:1121 1:N:0:CNATGT
CCCNACCCTTGCCTAC
+
AAF#FJJJJJJJJJJJ
"""
    def tearDown(self):
        shutil.rmtree(self.wd)
    def test_getreads_regexp_fastq(self):
        """getreads: get reads from Fastq file matching pattern
        """
        # Make an example file
        example_fastq = os.path.join(self.wd,"example.fastq")
        with open(example_fastq,'w') as fp:
            fp.write(self.example_fastq_data)
        # Get subset
        fastq_reads = getreads_regex(example_fastq,
                                      ":1101:21440:1121")
        reference_reads = [self.example_fastq_data.split('\n')[i:i+4]
                           for i in (0,)]
        for r1,r2 in zip(reference_reads,fastq_reads):
            self.assertEqual(r1,r2)

class TestReadSizeFunction(unittest.TestCase):
    """Tests for the 'read_size' function
    """
    def test_read_size_fastq(self):
        """
        read_size: check '.fastq' extension
        """
        self.assertEqual(read_size("test.fastq"),4)
    def test_read_size_fastq_gz(self):
        """
        read_size: check '.fastq.gz' extension
        """
        self.assertEqual(read_size("test.fastq.gz"),4)
    def test_read_size_fq(self):
        """
        read_size: check '.fq' extension
        """
        self.assertEqual(read_size("test.fq"),4)
    def test_read_size_fq_gz(self):
        """
        read_size: check '.fq.gz' extension
        """
        self.assertEqual(read_size("test.fq.gz"),4)
    def test_read_size_csfasta(self):
        """
        read_size: check '.csfasta' extension
        """
        self.assertEqual(read_size("test.csfasta"),2)
    def test_read_size_csfasta_gz(self):
        """
        read_size: check '.csfasta.gz' extension
        """
        self.assertEqual(read_size("test.csfasta.gz"),2)
    def test_read_size_qual(self):
        """
        read_size: check '.qual' extension
        """
        self.assertEqual(read_size("test.qual"),2)
    def test_read_size_qual_gz(self):
        """
        read_size: check '.qual.gz' extension
        """
        self.assertEqual(read_size("test.qual.gz"),2)

