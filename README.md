# pyipatcher
Incomplete iOS bootchain patchers in Python
## Notes
* ~~It will be pushed to pip as a package later~~
* You can now install it locally (see Installation)
* patchfinder64 is ported from [xerub's patchfinder](https://github.com/xerub/patchfinder64)
* kernelpatcher is ported from [palera1n team's fork of Kernel64Patcher](https://github.com/palera1n/Kernel64Patcher)
## Installation
```
git clone https://github.com/Mini-Exploit/pyipatcher
cd pyipatcher
./install.sh
```
## Usage
```
$ python3 -m pyipatcher
<<<<<<< HEAD
pyipatcher version: 1.0.1
=======
pyipatcher version: 1.0.0
>>>>>>> 4badf384ca941815dc41014795bc3900146dd967
Usage: python -m pyipatcher [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
<<<<<<< HEAD
  asrpatcher
=======
>>>>>>> 4badf384ca941815dc41014795bc3900146dd967
  kernelpatcher
```
## Future plan
* Complete kernel patcher
* Add iBoot patcher, ASR patcher, restored_external patcher
## Credits
Thanks to [plx](https://github.com/justtryingthingsout) for helping me with many fixes
