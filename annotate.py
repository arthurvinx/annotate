#!/usr/bin/python

import plyvel
import os
import time
from os.path import expanduser
import argparse
import sys

#functions

def write(out, query, result):
    out.write("%s\t%s\n" % (query,result))

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected!')

def getAll(blast, alen, evalue, bitscore, identity, queryCol, subjectCol, evalueCol, bitscoreCol, alenCol, pidentCol, db, out, unknown):
    check = True
    query = None
    with open(blast, "r") as f:
        write(out, "Query", "Annotation")
        for line in f:
            ls = line.split("\t")
            if check:
                lastIndexOfInterest = max(queryCol, subjectCol, evalueCol, bitscoreCol, alenCol, pidentCol)
                if len(ls) < 6:
                    print("Invalid number of columns!\n"+blast+" has "+str(len(ls))+" columns and at least 6 columns are required!")
                    break
                elif len(ls) <= lastIndexOfInterest:
                    print("Invalid number of columns!\n"+blast+" has "+str(len(ls))+" columns and the last index of interest is "+str(lastIndexOfInterest)+"!")
                    break
                else:
                    check = False
            query = ls[queryCol]
            if not checkHit(ls, alen, evalue, bitscore, identity, alenCol, evalueCol, bitscoreCol, pidentCol):
                if unknown:
                    write(out, query, "Unknown")
                continue
            result = db.get(ls[subjectCol])
            if result == None:
                if unknown:
                    write(out, query, "Unknown")
                continue
            write(out, query, result)

def getBestHits(blast, alen, evalue, bitscore, identity, queryCol, subjectCol, evalueCol, bitscoreCol, alenCol, pidentCol, db, out, unknown):
    firstQuery = True
    match = False
    check = True
    query = None
    with open(blast, "r") as f:
        write(out, "Query", "Annotation")
        for line in f:
            ls = line.split("\t")
            if check:
                lastIndexOfInterest = max(queryCol, subjectCol, evalueCol, bitscoreCol, alenCol, pidentCol)
                if len(ls) < 6:
                    print("Invalid number of columns!\n"+blast+" has "+str(len(ls))+" columns and at least 6 columns are required!")
                    break
                elif len(ls) <= lastIndexOfInterest:
                    print("Invalid number of columns!\n"+blast+" has "+str(len(ls))+" columns and the last index of interest is "+str(lastIndexOfInterest)+"!")
                    break
                else:
                    check = False
            if firstQuery:
                query = ls[queryCol]
                firstQuery = False
            if match:
                if query == ls[queryCol]:
                    continue
                else:
                    match = False
                    query = ls[queryCol]
            else:
                if query != ls[queryCol]:
                    if unknown:
                        write(out, query, "Unknown")
                    query = ls[queryCol]
            if not checkHit(ls, alen, evalue, bitscore, identity, alenCol, evalueCol, bitscoreCol, pidentCol):
                continue
            result = db.get(ls[subjectCol])
            if result == None:
                continue
            write(out, query, result)
            match = True
    if not match:
        if unknown:
            write(out, query, "Unknown")

def checkHit(ls, alen, evalue, bitscore, identity, alenCol, evalueCol, bitscoreCol, pidentCol):
    if float(ls[pidentCol]) < identity:
        return False
    elif int(ls[alenCol]) < alen:
        return False
    elif float(ls[evalueCol]) > evalue:
        return False
    elif float(ls[bitscoreCol]) < bitscore:
        return False
    return True

#help

parser = argparse.ArgumentParser(description="Annotate each query using the best alignment for which a mapping is known")
parser.add_argument("blast", help="BLAST/DIAMOND result file (tabular format)")
parser.add_argument("output", help="output file name")
parser.add_argument("type", help="levelDB prefix")
parser.add_argument("-b", "--bitscore", help="minimum bit score of a hit to be considered good (default: 50.0)",type=float, default=50.0)
parser.add_argument("-e", "--evalue", help="maximum e-value of a hit to be considered good (default: 0.00001)",type=float, default=0.00001)
parser.add_argument("-l", "--alen", help="minimum alignment length of a hit to be considered good (default: 100)", type=int, default=100)
parser.add_argument("-i", "--identity", help="minimum percent identity of a hit to be considered good (default: 80)", type=float, default=80)
parser.add_argument("-d", "--directory", help="directory containing a levelDB (default: $HOME/.basta/taxonomy)", default="home")
parser.add_argument("--queryCol", help="column index (0-based) in which the query ID can be found (default: 0)", type=int, default=0)
parser.add_argument("--subjectCol", help="column index (0-based) in which the subject ID can be found (default: 1)", type=int, default=1)
parser.add_argument("--evalueCol", help="column index (0-based) in which the e-value can be found (default: 10)", type=int, default=10)
parser.add_argument("--bitscoreCol", help="column index (0-based) in which the bit score can be found (default: 11)", type=int, default=11)
parser.add_argument("--alenCol", help="column index (0-based) in which the alignment length can be found (default: 3)", type=int, default=3)
parser.add_argument("--pidentCol", help="column index (0-based) in which the percent identity can be found (default: 2)", type=int, default=2)
parser.add_argument("--all", help="try to annotate all hits (default: False)", type=str2bool, default=False)
parser.add_argument("--unknown", help="whether to write 'Unknown' in the output for unknown mappings (default: True)", type=str2bool, default=True)
args = parser.parse_args()

#check args

if not os.path.isfile(args.blast):
    print(args.blast+" is not a file or does not exist!")
    sys.exit()
if args.directory=="home":
    bastahome = os.path.join(expanduser("~"),".basta/taxonomy")
    if not os.path.isdir(bastahome):
        print("BASTA home not found!\n"+bastahome+" is not a directory or does not exist!")
        sys.exit()
    dbdir = os.path.join(bastahome,str(args.type+"_mapping.db"))
    if not os.path.isdir(dbdir):
        print("No database found!\n"+dbdir+" is not a directory or does not exist!")
        sys.exit()
else:
    if not os.path.isdir(args.directory):
        print("Directory not found!\n"+args.directory+" is not a directory or does not exist!")
        sys.exit()
    dbdir = os.path.join(args.directory,str(args.type+"_mapping.db"))
    if not os.path.isdir(dbdir):
        print("No database found!\n"+dbdir+" is not a directory or does not exist!")
        sys.exit()

#assign annotation

db = plyvel.DB(dbdir, create_if_missing=False)
out = open(args.output, "w")
start_time = time.time()
print("Annotating queries, this may take some time...")
if args.all:
    getAll(args.blast, args.alen, args.evalue, args.bitscore, args.identity, args.queryCol, args.subjectCol, args.evalueCol, args.bitscoreCol, args.alenCol, args.pidentCol, db, out, args.unknown)
else:
    getBestHits(args.blast, args.alen, args.evalue, args.bitscore, args.identity, args.queryCol, args.subjectCol, args.evalueCol, args.bitscoreCol, args.alenCol, args.pidentCol, db, out, args.unknown)
out.close()
db.close()
print("Done!")
elapsed_time = time.time() - start_time
print("Time: "+str(elapsed_time)+" seconds.")
