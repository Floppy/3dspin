# 3dspin

3D spinning objects on the EMFcamp badge (TiLDA Mkπ)

Demo video: https://vine.co/v/5bzMrK7YU7d

## Installing

Install from the TiLDA app library; look for `3DSpin` in `uncategorized`.

## Development

If you want to develop and test the code on your own thing via the USB port, you'll need to create an app directory on there called `floppy~3dspin`, copy across all the code and models, then launch it with `pyboard` like so:

```
python3 test/pyboard.py main.py --device=/dev/tty.usbmodem1422
```

## Usage

Hit A and B to cycle between objects. Rotate the badge to rotate the object (static is with the badge hanging vertically).

## Adding more models

The app loads any OBJ files in the app directory, so they are easy to add, but it can't handle very big ones. Don't expect to be able to drop in a teapot without memory exceptions ruining your day; even a crappy sphere was too much for it in my testing.

## License & Credits

The code I've written in `main.py` is open source under the MIT license, as are the `OBJ` files.

The code in `matrix.py` is shamelessly stolen from https://sites.google.com/site/3dprogramminginpython/ and then badly converted to Python 3 by me. Thanks to the author.

`test/pyboard.py` is taken from micropython and included here just for convenience.
