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
pip3 install -U plyvel --no-cache-dir --no-deps --force-reinstall
```

The conda-forge channel is necessary to get the main dependency, the plyvel Python package. The pip command will avoid an import error described at the [Fixing plyvel](https://github.com/arthurvinx/annotate#fixing-plyvel) section.

Check whether your installation succeeded by typing:

```bash
annotate --help
```

If the installation was successful, you will see this help message:

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

As an alternative, you may install the plyvel package (version >= 1.3.0) via pip, download this repository contents, and use the annotate Python script.

## Usage

Annotate uses a [levelDB](https://github.com/google/leveldb) database (key-value disk repository) to map queries to new identifiers.

A mapping file is required to create a levelDB repository. A valid mapping file is composed by a header (opcional) and at least two columns, one containing the identifiers that will be used as keys, and the other containing the values mapped for each key:

**Input 1**

| key | value |
| --- | ----- |
| a   | 1     |
| b   | 2     |
| c   | 3     |
| a   | 4     |

In the case of duplicated keys, such as the key `a` from **Input 1**, the value for this key in the database will be replaced for each new entry found in the mapping file. Thus, the final value for the key `a` is `4`.

There are arguments used to create the database that inform in which column to find the keys/values, as well as an argument informing the presence/absence of a header.

To download a zip file containing the example data used in the next sections, [click here](https://gist.github.com/jvfe/a1c913cd9f04c073f6d0e8a5ae85a10f/archive/eef5c90c96a4f590c6cb1cf123ca54cc4d7968c0.zip). These files are also present in the [test](https://github.com/arthurvinx/annotate/tree/master/test) folder.

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

The first step to use annotate is the creation of a levelDB database.
In this example we will use a mapping file containing GenBank/RefSeq identifiers as keys, and UniProtKB identifiers as values ([input.txt](https://github.com/arthurvinx/annotate/blob/master/test/input.txt)).

**Input 2**

| GenBank_RefSeqProtein 	| UniProtKB         	|
|-----------------------	|-------------------	|
| WP_005581541.1        	| A0A1I3NYE9;L0ADC4 	|
| WP_005575885.1        	| A0A1I3N6N3;L0ALD9 	|
| WP_005576929.1        	| A0A1I3RLL1;L0AN04 	|
| WP_015233403.1        	| A0A1I3KT52;L0AFE0 	|
| WP_005578121.1        	| A0A1I3NAK9;L0ALK2 	|
| WP_005576999.1        	| A0A1I3R2S7;L0AMX4 	|
| AFZ74922.1            	| L0ANW7            	|

Four arguments are required to create a levelDB with the `createdb` sub-command. To create a levelDB from the `input.txt` mapping file, type:

```bash
annotate createdb input.txt example 0 1
```

- Input: The mapping file containing the key-value information (`input.txt`).

- Output: The prefix of the output database (`example`). This prefix is used as the database name. A meaningful name, such as **genbank_refseq2uniprotkb**, is preferable. By default, this database is stored at the **.annotate** folder under your home directory, using **.ldb** as suffix (file extension).

- Key/Value: The last two arguments indicate where the key and value columns are located in the mapping file. As the index is zero-based, the key column number is `0`, and the value column number is `1`. Inform these values according to your input file. Note that some entries in the UniProtKB column, from **Input 2**, contains identifiers separated by a semicolon. This was defined during the criation of this particular mapping file to allow multiple identifiers for a key.

You can also pass other arguments to the `createdb` sub-command, such as the column separator, whether the file has a header, and the directory used to store the database. To see a list of the existing arguments, type:

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

After the creation of a levelDB database, the `imapping` sub-command can be used to map the queries from a BLAST/DIAMOND tabular output to new identifiers. In this example we will use a DIAMOND tabular output containing GenBank/RefSeq identifiers in the hits/subject column ([diamond.m8](https://github.com/arthurvinx/annotate/blob/master/test/diamond.m8)).

**DIAMOND tabular output**

| Query	| Subject/Hit		| Identity	|Length |	|	|	|	|	|	| E-value	| Bit score	|
|-------	|----------------	|-------	|-----	|---	|---	|-----	|-----	|-----	|-----	|---------	|-------	|
| read1 	| WP_005581541.1 	| 98.2  	| 40  	| 1 	| 0 	| 129 	| 299 	| 1   	| 57  	| 7.7e-22 	| 113.6 	|
| read2 	| WP_005575885.1 	| 100.0 	| 60  	| 0 	| 0 	| 181 	| 2   	| 1   	| 60  	| 2.2e-24 	| 122.1 	|
| read3 	| WP_005580014.1 	| 100.0 	| 50  	| 0 	| 0 	| 2   	| 151 	| 385 	| 434 	| 3.6e-19 	| 104.8 	|
| read4 	| WP_005576929.1 	| 100.0 	| 98  	| 0 	| 0 	| 296 	| 3   	| 308 	| 405 	| 6.7e-42 	| 180.3 	|
| read5 	| ELY74166.1     	| 98.0  	| 100 	| 2 	| 0 	| 300 	| 1   	| 80  	| 179 	| 7.9e-43 	| 183.3 	|
| read5 	| WP_015233403.1 	| 98.0  	| 100 	| 2 	| 0 	| 300 	| 1   	| 98  	| 197 	| 7.9e-43 	| 183.3 	|
| read6 	| WP_005578121.1 	| 100.0 	| 52  	| 0 	| 0 	| 1   	| 156 	| 124 	| 175 	| 1.6e-22 	| 115.9 	|
| read7 	| WP_005576999.1 	| 92.0  	| 100 	| 8 	| 0 	| 1   	| 300 	| 14  	| 113 	| 1.1e-47 	| 199.5 	|
| read8 	| WP_005579760.1 	| 98.0  	| 100 	| 2 	| 0 	| 2   	| 301 	| 214 	| 313 	| 1.8e-42 	| 182.2 	|
| read8 	| AFZ74922.1     	| 98.0  	| 100 	| 2 	| 0 	| 2   	| 301 	| 188 	| 287 	| 1.8e-42 	| 182.2 	|

Three arguments are required to annotate queries: an input, an output, and the database to be used for the mappings. To annotate the queries using the `example` database, type:

```bash
annotate idmapping diamond.m8 output.txt example
```

- Input: A BLAST/DIAMOND tabular output (`diamond.m8`).

- Output: The desired output filename. The result is a tab-separated text file. (`output.txt`).

- LDB: The prefix of the levelDB to be used for the mappings (`example`).

The expected [output.txt](https://github.com/arthurvinx/annotate/blob/master/test/output.txt) for this example is:

**Example output**

| Query 	| Annotation        	|
|-------	|-------------------	|
| read1 	| Unknown           	|
| read2 	| A0A1I3N6N3;L0ALD9 	|
| read3 	| Unknown           	|
| read4 	| A0A1I3RLL1;L0AN04 	|
| read5 	| A0A1I3KT52;L0AFE0 	|
| read6 	| A0A1I3NAK9;L0ALK2 	|
| read7 	| A0A1I3R2S7;L0AMX4 	|
| read8 	| L0ANW7            	|

The default options generate an output containing one line for each query from the input. Note that some queries in this example were annotated as `Unknown`. This happens when annotate do not find any mapping for the hits from that query in the database, or when there are no hits meeting the thresholds. This software uses filters for some columns present in BLAST/DIAMOND tabular outputs, such as the bit score value, the alignment length, and the percent identity.

In the **Example output**:

- The read 1 has a mapping known, but do not meet the default minimum alignment length threshold, being mapped to `Unknown`.
- The read 3 has only one hit, with no known mapping, being mapped to `Unknown`.
- The read 5 and the read 8 were mapped for the second hit, because the first hit had no known mapping.

This software also tries to accommodate different file formats with at least 6 columns: query, subject, percent identity, alignment length, e-value, and bit score.
You can specify where the expected columns are located if your input is not in the BLAST/DIAMOND tabular format. To see a list of the existing arguments, type:

```bash
annotate idmapping -h
```

### Fixing plyvel

During the first use after the installation, the plyvel package installed via conda may present an import error and report an undefined symbol, preventing its import and use.

This error message ends like this:

```bash
ImportError: /home/vinx/miniconda3/envs/teste/lib/python3.9/site-packages/plyvel/_plyvel.cpython-39-x86_64-linux-gnu.so: undefined symbol: _ZTIN7leveldb10ComparatorE
```

In this case, the following command will reinstall the plyvel package and fix this problem:

```bash
pip3 install -U plyvel --no-cache-dir --no-deps --force-reinstall
```

The `fixplyvel` sub-command also reinstall the plyvel package via pip: 

```bash
annotate fixplyvel
```
