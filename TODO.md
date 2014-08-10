# Crotale - ToDo list

## Get actual status from FFmpeg processes

Will have to use subprocess.read instead of communicate

Or maybe use pexpect

## Add watch folder functionality

Should use watchdog for file system events. Will have to use a wait/check filesize loop to make sure we aren't processing files before the transfer is complete.

Ideally, we will be able to mount network file systems, keeping a database of those mount points, so they can be reconnected on boot.
