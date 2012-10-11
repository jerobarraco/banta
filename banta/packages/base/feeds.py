# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
logger = logging.getLogger(__name__)

import feedparser
import urllib2
import os

import PySide.QtCore as _qc
import PySide.QtGui as _qg
import banta
import banta.db
import banta.packages

class Reader( _qc.QThread ):
	newsFetched = _qc.Signal(list)
	def __init__(self):
		_qc.QThread.__init__(self)
		#self.setAutoDelete(True)
		self.feeds = []
		self.messages = []
		self.last = -1
		self.feed_url = u"http://www.moongate.com.ar/feeds/posts/default"
		self.html=u'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body>%s</body></html>'''

	def __downloadAndConvertImage(self, url):
		"""Downloads an image and encodes it at base64 to use when creating the message string
		notice all this info is handled on memory
		this method is private to this class (notice the __)
		idea from syrius @ irc.freenode.net
		"""
		#i love python batteries
		try:
			u = urllib2.urlopen(url)
			im = u.read()
			#and simplicity, and i love qt for handling size of the image and data so well
			return im.encode('base64')
		except:
			return ""

	def getVersion(self):
		#TODO read from www.shinystat, and on status 302 read the correct location
		#and cache that location if possible.

		p = os.name
		if p == 'nt':
			osn = 'Windows NT 5.1'
		elif p=='posix':
			osn = 'Linux'
		elif p=='mac':
			osn = 'Mac OS X'
		else:
			osn = p

		s = _qc.QLocale.system()
		country = s.countryToString(s.country())
		lang = s.name()
		ua = 'Banta/%s (%s; %s; %s)' % (banta.__version__, osn, country, lang)
		ref = 'http://www.moongate.com.ar/?q=%s'%(banta.__version__)
		opener = urllib2.build_opener()
		opener.addheaders = [
			('User-agent', 'Mozilla/5.0'),
			("Accept", "*/*"),
		 	('Accept-Language', lang),
			('Referer', ref),
			('User-Agent', ua)
		]
		url = "http://s2.shinystat.com/cgi-bin/shinystat.cgi?USER=moongate&ver="+banta.__version__
		opener.open(url).read()


	def run(self, *args, **kwargs):
		self.feeds = feedparser.parse( self.feed_url  )
		basestr = self.html % u'Novedades:<a href="%s"><img src="data:image/jpeg;base64,%s" width=25 height=25 />  <span style=" font-size:8pt; text-decoration: underline; color:#aaaaff;">%s</span></a> (%s) "%s..."'
		for i in self.feeds.entries:
			dp = i.date_parsed
			d = _qc.QDateTime(dp.tm_year, dp.tm_mon, dp.tm_mday, dp.tm_hour, dp.tm_min, dp.tm_sec)
			#doesnt work as expected
			#notice we used setWordWrap(True) in the designer for the label, so it doesnt break the ui zen
			text = i.summary#[:60]
			im = ''
			if ("media_thumbnail" in i) and (len(i.media_thumbnail)>0):
				im = self.__downloadAndConvertImage(i.media_thumbnail[0]['url'])
			msg = basestr%( i.link, im, i.title, d.toString(), text)
			self.messages.append(msg)
		self.newsFetched.emit(self.messages)
		if not banta.db.CONF.DEBUG:
			self.getVersion()

class Feeds(banta.packages.GenericModule):
	REQUIRES = []
	NAME = "Feeds"
	last_message = 0
	def __init__(self, app):
		super(Feeds, self).__init__(app)

	def load(self):
		#graphic effect to control the opacity of the label
		self.goe = _qg.QGraphicsOpacityEffect()
		#assign the effect to the label
		self.app.window.l_news.setGraphicsEffect(self.goe)
		animation = _qc.QPropertyAnimation(self.goe, "opacity")
		animation.setDuration(2000)
		animation.setStartValue(0)
		animation.setEndValue(1)
		self.a = animation

		#We could use QTConcurrent.run but i dont find it as convenient.. because of instance sharing and signals
		#this timer will show the messages in the status label
		self.timer = _qc.QTimer(self.app)
		self.timer.timeout.connect(self.showMessage)
		#The timer is started ONLY when the reader has fetched some news
		#the reader will fetch the news from internet, or fail-to if there's no internet
		self.app.reader = Reader()
		self.app.reader.newsFetched.connect(self.addNews, _qc.Qt.QueuedConnection)
		self.app.reader.finished.connect(self.term)
		self.app.reader.start()

	@_qc.Slot()
	def showMessage(self):
		"""This signal shows a message stored on self.news on the status bar,
		runs on the main thread.
		This is triggered by the self.timer"""
		if not self.news : return
		#this is safe only if we dont remove any news, if we do that, we must put last_message to 0
		msg = self.news [self.last_message]
		self.last_message +=1
		self.last_message %= len(self.news)
		self.app.window.l_news.setText(msg)
		#to keep things easy, we'll only animate the fade-in
		#re-start the animation
		self.a.start()

	@_qc.Slot(str)
	def addNews(self, news):
		"""This slot is called from the runner thread, when the runner has finished.
		news is a list with all the messages (can be html)"""
		self.news = news
		self.last_message = 0
		#para que no espere 2 minutos en mosrta el primer mensaje
		self.showMessage()
		##only starts the timer after we've got the news
		self.timer.start(60000)

	@_qc.Slot()
	def term(self):
		pass #The thread is finished..

	def wait(self):
		self.app.reader.wait(5000)

a = """NOTE ABOUT QTHREADS!!
DONT add slots to a QThread subclass:
they’ll be invoked from the “wrong” thread, that is, not the one the QThread object is managing, but the one that object is living in,
 forcing you to specify a direct connection and/or to use moveToThread(this).

 QThread objects are not threads; they’re control objects around a thread, therefore meant to be used from another thread
  (usually, the one they’re living in).
A good way to achieve the same result is splitting the “working” part from the “controller” part, that is, writing a
 QObject subclass and using QObject::moveToThread() to change its affinity:

class Worker : public QObject
{
    Q_OBJECT
public slots:
    void doWork() {
        /* ... */
    }
};
/* ... */

QThread *thread = new QThread;
Worker *worker = new Worker;
connect(obj, SIGNAL(workReady()), worker, SLOT(doWork()));
worker->moveToThread(thread);
thread->start();
"""