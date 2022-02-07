# Installation and usage

Continuous time series acquisition from Spectrum digitizer cards to ASDF format, for DUGseis

## Status

This software has alpha/beta status. It cannot be expected to fulfill any specific requirements or to flawlessly fulfill any specific specific task. All liability derogated - use it at your own risk, or don't use it!

## Usage

Data acquisition:
```bash
$ cd DUGseis-acquisition
$ conda activate dug_seis_acquisition
$ dug-seis -v acquisition
```

## Installation

1. Install miniconda: https://docs.conda.io/en/latest/miniconda.html
2. Create new environment:

```bash
conda create -n dug_seis_acquisition python=3.9
conda activate dug_seis_acquisition
```

3. Clone DUGSeis

```
git clone https://github.com/swiss-seismological-service/DUGseis-acquisition.git
```

4. Install DugSeis and dependencies

```
cd DUGseis-acquisition
conda activate dug_seis_acquisition
pip install -e .
```

## License & Copyright

DUG Seis is licensed under the GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html).

The copyright is held by ETH Zurich, Switzerland.
Main Contributors for the first version developed until August 2019 are
- Joseph Doetsch
- Thomas Haag
- Sem Demir
- Linus Villiger