# Usage

Continuous time series acquisition from Spectrum digitizer cards to ASDF format, for DUGseis.

Data acquisition:
```bash
cd code/DUGseis-acquisition
conda activate dug_seis_acquisition
dug-seis acquisition
```

If another instance was used, a reactivation might e needed:
```bash
conda activate dug_seis_acquisition
pip install -e /home/code/DUGseis-acquisition/
```

If running on a Windows machine for debugging purposes disable the streaming ability.
To achieve this change the name of `streaming_servers:` e.g. to `DISABLEstreaming_servers:` in `dug-seis.yaml`.

## Status

This software has alpha/beta status. It cannot be expected to fulfill any specific requirements or to flawlessly fulfill any specific specific task. All liability derogated - use it at your own risk, or don't use it!

## License & Copyright

DUG Seis is licensed under the GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html).

The copyright is held by ETH Zurich, Switzerland.
Main Contributors for the first version developed until August 2019 are
- Joseph Doetsch
- Thomas Haag
- Sem Demir
- Linus Villiger