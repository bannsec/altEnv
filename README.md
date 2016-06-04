# altEnv
altEnv is an Alternate Environment manager

This repo project is inspired by there being some strange environments that come up in CTF challenges. The idea here is to simplify the process of setting up these environemnts. Normally, one would just use VMWare or something, but when faced with an ARM/MIPS or other strange binary, it becomes a little more complicated. The goal of this script is simply to take that complexity away from the challenges, and allow you to work on the challenge.

# View Types
altEnv allows you to select how you wish to interact with the virtual environment. Note that sometimes one works and another doesn't. If one doesn't work, simply try the next. This will be different depending on what OS you're installing, install options, etc.

## Console
In Console mode, altEnv will attempt to connect you to the system as if it was directly executing in the current window. This is done in the backend by specifying "-nographic" to force only textual output.

## Curses
In Curses mode, you are able to get some limitied graphicish things. Since it's still curses, it is text based. However, it can in general look nicer than the console version.

## VNC
The VNC View Type is actually the QEMU default. In this case, QEMU will start up a virtual monitor and host it as a VNC service. You need to connect to it via normal VNC channels. In my testing, I've noticed some viewers not working terribly well. However, I've had good success with the Remmina viewer.

# Current Support

## MIPS

- Debian (option for Stable, Testing, Unstable)

## MIPSEL

- Debian (option for Stable, Testing, Unstable)

## x86_64

- Arch Linux

## i386

- Arch Linux
