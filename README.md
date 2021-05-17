# Annotate

[![](https://anaconda.org/arthurvinx/annotate/badges/installer/conda.svg)](https://anaconda.org/arthurvinx/annotate)
![](https://anaconda.org/arthurvinx/annotate/badges/version.svg)
![](https://anaconda.org/arthurvinx/annotate/badges/platforms.svg)
![](https://anaconda.org/arthurvinx/annotate/badges/license.svg)

Annotate is a Python package that annotates each query from a BLAST/DIAMOND tabular output using the best alignment for which a mapping is known.

## Installation

The easiest way to install this software, including its dependencies, is via [conda](https://docs.conda.io/en/latest/) with:

```bash
conda install -c conda-forge -c arthurvinx annotate
```

The conda-forge channel is necessary to get the main dependency, the plyvel Python package.

Check if your installation succeeded by typing:

```bash
annotate --help
```

The installation was successful if the help message was displayed.

```bash
usage: annotate [-h] [-v] {createdb,idmapping,fixplyvel} ...

Annotate each query using the best alignment for which a mapping is known

positional arguments:
  {createdb,idmapping,fixplyvel}
                        Sub-command help

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

## Usage

Annotate uses a [levelDB](https://github.com/google/leveldb) database (key-value disk repository) to map queries to new identifiers.

A mapping file is required to create a levelDB database. The valid mapping file is composed by a header (opcional) and at least two columns, one containing the identifiers that will be used as keys, and the other containing the values mapped for each key:

Example 1

| key | value |
| --- | ----- |
| a   | 1     |
| b   | 2     |
| c   | 3     |
| a   | 4     |

In the case of duplicated keys, such as the key 'a' in the Example 1, the value for this key in the database will be replaced for each new entry found in the mapping file. Thus, the final value for the key 'a' is 4.

There are arguments used to create the database that inform in which column to find the keys/values, as well as an argument informing the presence/absence of a header.

To download a zip file containing the example data used in the next sections [click here](https://gist.github.com/jvfe/a1c913cd9f04c073f6d0e8a5ae85a10f/archive/eef5c90c96a4f590c6cb1cf123ca54cc4d7968c0.zip).

### Creating the database

```bash
usage: annotate createdb [-h] [--sep SEP] [--header HEADER] [-d DIRECTORY]
                         input output key value

Create/Update a mapping database

positional arguments:
  input                 A mapping file containing at least two columns
  output                LevelDB prefix
  key                   Column index (0-based) in which the keys can be found
  value                 Column index (0-based) in which the values can be
                        found

optional arguments:
  -h, --help            show this help message and exit
  --sep SEP             The separator between columns (default: \t)
  --header HEADER       Indicates the presence of a header in the input file
                        (default: True)
  -d DIRECTORY, --directory DIRECTORY
                        Directory of databases (default:
                        $HOME/.annotate/levelDB)
```

The first step to use annotate is the creation of a levelDB.
In this example we will use a mapping file containing GenBank/RefSeq identifiers as keys, and UniProtKB identifiers as values ([input.txt](https://github.com/arthurvinx/annotate/blob/master/test/input.txt)).

Four arguments are required to create a levelDB with the **createdb** sub-command:

```bash
annotate createdb input.txt example 0 1
```

- The file containing the key-value information (**input.txt**).

- The prefix of the output database (**example**). This prefix is used as the database name. A meaningful name, such as **genbank_refseq2uniprotkb**, is preferable. By default, this database is stored at the **.annotate** folder under your home directory.

- The last two arguments indicate where the key and value columns are located in the mapping file. As the index is zero-based, the key column number is **0**, and the value column number is **1**. These can will be different according to your input file.

You can also pass other arguments to the **createdb** sub-command, such as the column separator, whether the file has a header, and the directory used to store the database. To see a list of the existing arguments type:

```bash
annotate createdb -h
```

### Annotating queries

```bash
usage: annotate idmapping [-h] [-b BITSCORE] [-e EVALUE] [-l ALEN]
                          [-i IDENTITY] [-d DIRECTORY] [--queryCol QUERYCOL]
                          [--subjectCol SUBJECTCOL] [--evalueCol EVALUECOL]
                          [--bitscoreCol BITSCORECOL] [--alenCol ALENCOL]
                          [--pidentCol PIDENTCOL] [--all ALL]
                          [--unknown UNKNOWN] [--sep SEP]
                          input output ldb

Translate identifiers from the input using the mapping database

positional arguments:
  input                 A BLAST/DIAMOND result in tabular format
  output                Output filename
  ldb                   LevelDB prefix

optional arguments:
  -h, --help            show this help message and exit
  -b BITSCORE, --bitscore BITSCORE
                        Minimum bit score of a hit to be considered good
                        (default: 50.0)
  -e EVALUE, --evalue EVALUE
                        Maximum e-value of a hit to be considered good
                        (default: 0.00001)
  -l ALEN, --alen ALEN  Minimum alignment length of a hit to be considered
                        good (default: 50)
  -i IDENTITY, --identity IDENTITY
                        Minimum percent identity of a hit to be considered
                        good (default: 80)
  -d DIRECTORY, --directory DIRECTORY
                        Directory of databases (default:
                        $HOME/.annotate/levelDB)
  --queryCol QUERYCOL   Column index (0-based) in which the query ID can be
                        found (default: 0)
  --subjectCol SUBJECTCOL
                        Column index (0-based) in which the subject ID can be
                        found (default: 1)
  --evalueCol EVALUECOL
                        Column index (0-based) in which the e-value can be
                        found (default: 10)
  --bitscoreCol BITSCORECOL
                        Column index (0-based) in which the bit score can be
                        found (default: 11)
  --alenCol ALENCOL     Column index (0-based) in which the alignment length
                        can be found (default: 3)
  --pidentCol PIDENTCOL
                        Column index (0-based) in which the percent identity
                        can be found (default: 2)
  --all ALL             Try to annotate all hits (default: False)
  --unknown UNKNOWN     Whether to write 'Unknown' in the output for unknown
                        mappings (default: True)
  --sep SEP             The separator between columns (default: \t)
```

After creating your local key-value store, you can annotate the identifiers obtained in your alignment file:

```bash
annotate idmapping diamond.m8 output.txt example
```

The arguments you see above are:

- The input alignment file (`diamond.m8`).

- The name of the output file containing the annotation (`output.txt`).

- The prefix of the levelDB you want to use, in this case, `example`.

- Annotate also tries to accommodate different file formats,
  so you can specify where the expected columns are located,
  type `annotate idmapping -h` to see a list of possible arguments.

An important thing to note from the output you obtained above is that not all of the queries were annotated in the output file, some having their value as `Unknown`.

This could be either because annotate couldn't find a mapping for the query ID in the levelDB or because the hit couldn't reach one of annotate's thresholds -
By default, annotate has a series of filters to ensure only the best mapping is used, but you're free to change the value of these thresholds, with parameters such as `-b` to define the minimum bit score, for instance. Type `annotate idmapping -h` to see a list of arguments and defaults you can change in your command.
