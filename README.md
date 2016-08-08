# 3dspin

3D spinning objects on the EMFcamp badge (TiLDA Mkπ)

<iframe src="https://vine.co/v/5bzMrK7YU7d/embed/simple" width="600" height="600" frameborder="0"></iframe><script src="https://platform.vine.co/static/scripts/embed.js"></script>

## Installing

Currently it's not in the badge app library, as I can't get it to work from the menu. If you want to run it on your own thing, you'll need to create an app directory, copy across all the code and models, then launch it with `pyboard` like so:

```
python3 test/pyboard.py main.py --device=/dev/tty.usbmodem1422
```

## Usage

Hit A and B to cycle between objects.

## Adding more models

The app loads OBJ files from the `models` directory, so they are easy to add, but it can't handle very big ones. Don't expect to be able to drop in a teapot without memory exceptions ruining your day; even a crappy sphere was too much for it in my testing.