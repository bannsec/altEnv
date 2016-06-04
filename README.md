# altEnv
altEnv is an Alternate Environment manager

This repo project is inspired by there being some strange environments that come up in CTF challenges. The idea here is to simplify the process of setting up these environemnts. Normally, one would just use VMWare or something, but when faced with an ARM/MIPS or other strange binary, it becomes a little more complicated. The goal of this script is simply to take that complexity away from the challenges, and allow you to work on the challenge.

# Quick Start
To quick start, I've created a setup script. For the time being, I've only tested this for Debian based systems. However, I will extend that to others later.

```bash
$ ./setup.sh
$ workon altEnv
$ ./altEnv
3
```

Note that I added in option 3 to install QEMU. Even if you have a version on your system, it's not a bad idea to "install" the latest version. In this case, install simply means to download, compile, and be ready to use. It does not place that QEMU in your path anywhere so that this application can be fully removed without worry. If you wish to put it in your path, that's your option. It doesn't NEED to be in your path as it will save the install location.

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

# Common Problems

## Screen doesn't show anything
Not all the view types always work for each OS. If the option you tried didn't show anything, attempt a different View Type. In my experience so far, I haven't found an OS that will not display between the three options.

## Bootloader Warnings
Debian will give you a warning about not being able to install a boot loader. This is fine, but you need to be aware of what's going on. Basically, there's no Grub bootloader compiled that supports Debian MIPS/ARM and possibly others. When this is the case, QEMU can still boot but it requires appending an option to specify where the boot partition is. I default this option to /dev/sda1 where needed. This might not be the correct default depending on your partitioning options while you set up. If your boot partition ends up being something different, all you need to do is open the "config.ini" file in your environemnt and change "append" option to be root=/correct/partition/here

## I want to add my own option to QEMU
Easy! If you want to add an option manually, simply go into the "config.ini" file inside your environment (i.e.: <base path>/environments/blerg/config.ini) and add it under the "options" section. This section is basically parsed directly into the QEMU line as "-option option_value".

