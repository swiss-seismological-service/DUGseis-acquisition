# Installation Instructions

The `conda` Python distribution is recommended, but you can use any Python
distribution you see fit.

## Installing `conda`

1. Install `miniconda` for your operating system: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html). In a fresh installation, a [WSL](https://de.wikipedia.org/wiki/Windows-Subsystem_f%C3%BCr_Linux) or a docker container miniconda can be installed with:

```bash
apt update
apt upgrade -y
apt install wget
apt install git
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```
2. Reopen console.

## Create a new environment

```bash
conda config --add channels conda-forge
conda update conda
conda create -n dug_seis_acquisition python=3.9 obspy
conda activate dug_seis_acquisition
```

The "conda-forge" channels only need to be added once.
Installing obspy at this stage worked better than with the setup.py.

**Make sure the `dug_seis_acquisition` environment is active when using `DUGSeis-acquisition` and for
all the following steps on this page!**


## Install DUGSeis-acquisition

Clone DUGSeis-acquisition

```bash
cd ~
mkdir code
cd code
git clone https://github.com/swiss-seismological-service/DUGseis-acquisition.git
```
Creating the `code` folder is optional.

```bash
cd DUGseis-acquisition
conda activate dug_seis_acquisition
pip install -e /home/code/DUGseis-acquisition/
```
`pip install -e .` stopped working for me (March 2022).
On a Windows machine use `pip install -e C:\code\DUGseis-acquisition\`.

## Update DUGSeis-acquisition

To update `DUGSeis-acquisition` please change to the `DUGSeis-acquisition` directory and run:

```bash
git pull
```

If that does not work for some reason (e.g. the `DUGSeis-acquisition` repository has been
force pushed to, local changes, ...) please do the following (**All your local
changes will be deleted!**):

```bash
git fetch origin main
git reset --hard origin/main
```

If the `DUGSeis-acquisition` dependencies changed, just run

```bash
conda activate dug_seis_acquisition
pip install -e /home/code/DUGseis-acquisition/
```


conda create -n docu python=3.9 obspy
pip install -e C:\polybox\asdfAqSys\code\docu\
conda activate docu
cd docs
make.bat html


docu\dug_seis\acquisition\hardware_driver\pyspcm.py
build succeeded, 2 warnings.
