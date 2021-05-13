# Annotate

[![](https://anaconda.org/arthurvinx/annotate/badges/installer/conda.svg)](https://anaconda.org/arthurvinx/annotate)
![](https://anaconda.org/arthurvinx/annotate/badges/version.svg)
![](https://anaconda.org/arthurvinx/annotate/badges/platforms.svg)
![](https://anaconda.org/arthurvinx/annotate/badges/license.svg)

Annotate is a Python package that annotates each query from a BLAST/DIAMOND tabular output using the best alignment for which a mapping is known.

## Installation

The main dependency of this package is the plyvel Python package.
To install the software including its dependencies we recommend using [conda](https://docs.conda.io/en/latest/):

```bash
conda install -c conda-forge -c arthurvinx annotate
```

Check if your installation succeeded by typing:

```bash
annotate --help
```

You should see the help message.

## Example usage

- Annotate works via a key-value database, a [LevelDB](https://en.wikipedia.org/wiki/LevelDB).
  So, in order to create your local key-value store,
  you'll need a file in the following format:

| key | value |
| --- | ----- |
| a   | 1     |
| b   | 2     |
| c   | 3     |
| a   | 4     |

(Note that repeated keys, such as 'a', will have their value reassigned in the database to the latest value found)

- Thankfully, we can provide some test data to get you right to testing annotate.
  [Click here](https://gist.github.com/jvfe/a1c913cd9f04c073f6d0e8a5ae85a10f/archive/eef5c90c96a4f590c6cb1cf123ca54cc4d7968c0.zip) to download a zip file containing the example data we'll be using in this showcase.

### Creating the database

- The first step to start using annotate is creating a local levelDB.
  For this purpose we'll use a file containing key-value information (input.txt).

```bash
annotate createdb input.txt example 0 1
```

Let's unpack the arguments you see above:

- First, we specify the file containing the key-value information (`input.txt`).

- Then, we specify the prefix of the output levelDB (`example`),
  this prefix will be used in the next command to indicate what levelDB you're using,
  so choose something meaningful to your analysis.
  By default this levelDB will be created in a `.annotate` folder under your home directory.

- And finally, we say where in the text file the key and value columns are located. This index is zero-based, so in our case we can say the key column is `0` and the value column is `1`, these can be different according to your input file.

- You can also pass other arguments to the `createdb` command, such as the column separator, if the file has a header and in which directory you want to create the levelDB. Type `annotate createdb -h` to see a list of all possible arguments.

### Annotating queries

- After creating your local key-value store, you can annotate the identifiers obtained in your alignment file:

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
