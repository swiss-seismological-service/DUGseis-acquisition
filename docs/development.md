# Development

It is an evolution of the code found here:
[https://github.com/swiss-seismological-service/DUGseis-acquisition](https://github.com/swiss-seismological-service/DUGseis-acquisition)

The data processing companion code can be found here:
[https://gitlab.seismo.ethz.ch/doetschj/DUG-Seis](https://gitlab.seismo.ethz.ch/doetschj/DUG-Seis)

## Software Structure
From higher level access to lower levels closer to the hardware.

```{image} static/current_python_calling_tree.png
:alt: DUGSeis Logo
:width: 100%
:align: center
```

## Directory Structure

As of March 2022 the directory structure is approximately as follows:

```
.
├── README.md
├── docs
│   └── ...
├── dug_seis
│   ├── cmd_line.py
│   └── acqisition
│      ├── hardware_driver
│      ├── scripts
│      │  └── testing
│      ├── acquisition.py
│      ├── card_manager.py
│      ├── ...
│
├── ...
└── setup.py
```

* `README.md`: Root level readme file.
* `docs`: Sphinx based documentation.
* `dug_seis`: Source code for the actual `DUGSeis-acquisition` package.
* `dug_seis/cmd_line.py`: Code for the command line interface.
* `dug_seis/acquisition/hardware_driver`: Interface to the driver of the Spectrum cards.
* `dug_seis/acquisition/scripts`: Tools to plot data and read ASDF files.
* `dug_seis/acquisition/scripts/testing`: Test of new features and ideas.
* `dug_seis/acquisition/acquisition.py`: Acquisition entry point.
* `dug_seis/acquisition/card_manager.py`: Main acquisition loop, run’s until ctrl + c.
* `setup.py`: Setup script teaching Python how to install `DUGSeis`.

## Documentation Building

The documentation resides in the `docs` directory. It depends on the following packages:

* `sphinx`
* `sphinx-book-theme`
* `myst-parser`

### Installation of sphinx

This is for the installation in a separate Environment. The `dug_seis_acquisition` environment could also be used. 
```bash
conda create -n docu python=3.9 obspy
conda activate docu
pip install -e /home/code/docu/
pip install sphinx, sphinx-book-theme, myst-parser
```

Once these are installed, just change to the docs directory and execute:

### Usage of sphinx

```bash
cd code/DUGSeis-acquisition/docs
make html
```

or (on Windows)

```bash
cd code/DUGSeis-acquisition/docs
./make.bat html
```

and the HTML documentation will be saved to `docs/_build/html`.

Currently, the build process generates 2 warnings if the hardware driver of the Spectrum cards is not present `spcm_win64.dll`.