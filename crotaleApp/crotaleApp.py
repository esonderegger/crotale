from flask import Flask, abort, render_template, redirect, request, url_for
from flask import copy_current_request_context, jsonify
from werkzeug import secure_filename
from sqlalchemy import create_engine, Column, Integer, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
import subprocess
import thread

app = Flask(__name__)


alchemyEngine = create_engine('postgresql://crotale:crotale@localhost/crotale')
alchemyBase = declarative_base()
alchemySession = sessionmaker(bind=alchemyEngine)
session = alchemySession()


class AudioFile(alchemyBase):
    """ SQLAlchemy class describing a file to be processed """
    id = Column(Integer, primary_key=True)
    originalname = Column(Text)
    inpath = Column(Text)
    outpath = Column(Text)
    ilufs = Column(Float)
    ithresh = Column(Float)
    lra = Column(Float)
    lrathresh = Column(Float)
    lralow = Column(Float)
    lrahigh = Column(Float)
    starttime = Column(DateTime)
    endtime = Column(DateTime)
    status = Column(Text)
    __tablename__ = 'AudioFile'

    def __init__(self, filename):
        self.originalname = filename
        self.starttime = datetime.datetime.now()
        self.status = 'uploading'


def r128Stats(filePath):
    """ takes a path to an audio file, returns a dict with the loudness
    stats computed by the ffmpeg ebur128 filter """
    ffargs = ['/usr/local/bin/ffmpeg',
              '-nostats',
              '-i',
              filePath,
              '-filter_complex',
              'ebur128',
              '-f',
              'null',
              '-']
    proc = subprocess.Popen(ffargs, stderr=subprocess.PIPE)
    stats = proc.communicate()[1]
    summaryIndex = stats.rfind('Summary:')
    summaryList = stats[summaryIndex:].split()
    ILufs = float(summaryList[summaryList.index('I:') + 1])
    IThresh = float(summaryList[summaryList.index('I:') + 4])
    LRA = float(summaryList[summaryList.index('LRA:') + 1])
    LRAThresh = float(summaryList[summaryList.index('LRA:') + 4])
    LRALow = float(summaryList[summaryList.index('low:') + 1])
    LRAHigh = float(summaryList[summaryList.index('high:') + 1])
    statsDict = {'I': ILufs, 'I Threshold': IThresh, 'LRA': LRA,
                 'LRA Threshold': LRAThresh, 'LRA Low': LRALow,
                 'LRA High': LRAHigh}
    return statsDict


def linearGain(iLUFS, goalLUFS=-23):
    """ takes a floating point value for iLUFS, returns the necessary
    multiplier for audio gain to get to the goalLUFS value """
    gainLog = -(iLUFS - goalLUFS)
    return 10 ** (gainLog / 20)


def ffApplyGain(inPath, outPath, linearAmount):
    """ creates a file from inpath at outpath, applying a filter
    for audio volume, multiplying by linearAmount """
    ffargs = ['/usr/local/bin/ffmpeg', '-y', '-i', inPath,
              '-af', 'volume=' + str(linearAmount)]
    if outPath[-4:].lower() == '.mp3':
        ffargs += ['-acodec', 'libmp3lame', '-aq', '0']
    ffargs += [outPath]
    return subprocess.call(ffargs)


def createDBTable():
    """ Used on install to create the necessary database table """
    alchemyBase.metadata.create_all(alchemyEngine)


@app.route("/")
def index():
    return render_template("base.html")


@app.route("/filestatus/<id>")
def filestatus(id):
    audioRow = session.query(AudioFile).get(id)
    if audioRow:
        item = audioRow.__dict__
    else:
        item = {'id': id}
    return render_template("filestatus.html", item=item)


@app.route("/jsonstatus/<id>")
def jsonstatus(id):
    audioRow = session.query(AudioFile).get(id)
    if audioRow:
        jsonDict = {'id': audioRow.id}
        jsonDict['originalname'] = audioRow.originalname
        jsonDict['outpath'] = audioRow.outpath
        jsonDict['ilufs'] = audioRow.ilufs
        jsonDict['ithresh'] = audioRow.ithresh
        jsonDict['lra'] = audioRow.lra
        jsonDict['lrathresh'] = audioRow.lrathresh
        jsonDict['lrahigh'] = audioRow.lrahigh
        jsonDict['lralow'] = audioRow.lralow
        jsonDict['status'] = audioRow.status
        if audioRow.ilufs:
            jsonDict['gainapplied'] = "{0:.1f}".format(-(audioRow.ilufs + 23))
        else:
            jsonDict['gainapplied'] = False
        return jsonify(jsonDict)
    else:
        return jsonify({'id': id, 'status': 'not found'})


@app.route('/uploadaudio', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        audiofile = request.files['audiofile']
        if audiofile:
            audioRow = AudioFile(audiofile.filename)
            session.add(audioRow)
            session.commit()
            rowid = audioRow.id
            idstr = str(rowid)
            uploadFolder = os.path.join('/srv/www/crotale/uploads', idstr)
            os.makedirs(uploadFolder)
            filename = secure_filename(audiofile.filename)
            uploadPath = os.path.join(uploadFolder, filename)
            audiofile.save(uploadPath)
            audioRow.inpath = uploadPath
            audioRow.status = 'uploaded'
            session.commit()

            @copy_current_request_context
            def processAudio():
                audioRow.status = 'calculating average loudness'
                session.commit()
                stats = r128Stats(audioRow.inpath)
                audioRow.ilufs = stats['I']
                audioRow.ithresh = stats['I Threshold']
                audioRow.lra = stats['LRA']
                audioRow.lrathresh = stats['LRA Threshold']
                audioRow.lralow = stats['LRA Low']
                audioRow.lrahigh = stats['LRA High']
                audioRow.status = 'applying gain'
                session.commit()
                correctDir = os.path.join('/srv/www/crotale/corrected', idstr)
                os.makedirs(correctDir)
                filename = os.path.basename(audioRow.inpath)
                correctedPath = os.path.join(correctDir, filename)
                gain = linearGain(stats['I'])
                ffApplyGain(audioRow.inpath, correctedPath, gain)
                audioRow.outpath = correctedPath[16:]
                audioRow.endtime = datetime.datetime.now()
                audioRow.status = 'Loudness processing complete.'
                session.commit()
            thread.start_new_thread(processAudio, ())
            return redirect(url_for("filestatus", id=rowid))
    abort(403)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
