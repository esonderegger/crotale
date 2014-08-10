crotale
=======

Crotale is an EBU R128 loudness correction web application, inspired by [Xylo](https://github.com/kylophone/xylo)

Background
----------

In 2010, the European Broadcasting Union published its [Loudness Recommendation EBU R128](https://tech.ebu.ch/webdav/site/tech/shared/r/r128-2014.pdf). Previously, audio engineers had peak and RMS metering, which has shortcomings because humans do not perceive all frequencies as equally loud. R128 corrects for these [Fletcher-Munson curves](http://en.wikipedia.org/wiki/Fletcher%E2%80%93Munson_curves) so that different types of audio normalized to the same level in LUFS should sound equally loud.

The EBU recommends that all program material be normalized to -23 LUFS.

What Crotale does
-----------------

Crotale is a web application, designed to be run on the same local network as where audio engineers are creating their files. It provides an interface where someone can upload an audio file to the crotale server and then download a corrected file, normalized to -23 LUFS.

Soon, it will hopefully also provide an interface to create watch folders, where engineers can place uncorrected files in one location and then retrieve normalized files in a different location.

Installation
------------

The easiest way to install Crotale is to use the [virtual appliance file](https://s3-us-west-2.amazonaws.com/crotale/crotale-latest.ova). To use it, download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) on a machine on your network, then inside virtualbox, go to "file -> import appliance" and select the crotale-latest.ova file you just downloaded. After the appliance is set up, click "start" to start the crotale server.

The second easiest way to install crotale is to create a virtual machine in VirtualBox and install [Ubuntu Server 14.04](http://www.ubuntu.com/download/server) on it. Have the default user be "crotale". Then, download the [crotale source code](https://s3-us-west-2.amazonaws.com/crotale/crotale-latest.tar.gz) into the home directory, uncompress it, and install it by typing:

    wget https://s3-us-west-2.amazonaws.com/crotale/crotale-latest.tar.gz
    tar -zxvf crotale-latest.tar.gz
    ./instalScript.sh

You will be prompted for the password you created for the crotale user.

The most difficult way to install Crotale would be if you want to use crotale on an existing server. If you have a preferred method for running uWSGI applications, you can just use the code in the crotaleApp folder. You will also need FFmpeg to be installed at /usr/local/bin/ffmpeg or change the location of the ffmpeg binary in crotaleApp.py.

Usage
-----

In order to access Crotale from a web browser, you may be able to simply enter its hostname in the url bar. By default, this is [http://crotale/](http://crotale/). If this doesn't work, you may need to find the ip address assigned to your crotale server. To do this, log into the virtual appliance (defaults: username=crotale, password=crotate) and type "ifconfig". Then, enter that ip address into the url bar of your browser, for example: [http://192.168.1.111](http://192.168.1.111).

Then, simply upload an audio file via the form. It should display status information, and then information about the the loudness values calculated on the uploaded file with a button to download the normalized file.

Contribute
----------

- Issue Tracker: [github.com/esonderegger/crotale/issues](https://github.com/esonderegger/crotale/issues)
- Source Code: [github.com/esonderegger/crotale](https://github.com/esonderegger/crotale)

Support
-------

If you are having issues, please let me know by sending me an email at evan.sonderegger@gmail.com

License
-------

The project is licensed under the MIT license.
