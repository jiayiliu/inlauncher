#!/usr/bin/env python

import Tkinter as tk
import subprocess
from threading import Thread
from Queue import Queue
from time import sleep
import re


class NonBlockingStreamReader:
    def __init__(self, stream, maxline=1000):
        """non-blocking stream reader to read the stdout from ipython notebook.

        detail about this class is described [here](http://eyalarubas.com/python-subproc-nonblock.html)
        :param stream: the stream to read from.
                Usually a process' stdout or stderr.
        :param maxline: the maximum line stored in queue
        :return: NonBlockingStreamReader object
        """
        self._s = stream
        self._q = Queue(maxsize=maxline)

        def _populateQueue(stream, queue):
            """Collect lines from 'stream' and put them in 'queue'.

            :param stream: incoming stream
            :param queue: queue to store data
            """
            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    break

        self._t = Thread(target = _populateQueue,
                args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def get_record(self):
        return [i for i in self._q.queue]


class Application(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        self.master.title("inlauncher")
        self.current_ip = u"IP of ipython notebook"
        self.grid()
        self.create_layout()

    def create_layout(self):
        self.start_button = tk.Button(self, text="Start ipython notebook", command=self.start)
        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.ip_label = tk.Text(self, height=1, width=25)
        self.start_button.grid(column=0, columnspan=4, row=0)
        self.ip_label.insert(1.0, self.current_ip)
        self.ip_label.grid(column=0, columnspan=4, row=1)
        self.quit_button.grid(column=0, columnspan=4, row=2)

    def start(self):
        self.ip_label.delete(1.0, self.count_length())
        self.start_notebook()
        self.ip_label.insert(1.0, self.current_ip+':'+self.current_port)

    def quit(self):
        self.process.terminate()
        self.master.quit()

    def start_notebook(self):
        """Start ipython notebook
        """
        self.process = subprocess.Popen(["ipython","notebook"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.record_reader = NonBlockingStreamReader(self.process.stdout)
        sleep(1)
        self.report_ip()
        # TODO add port forwarding
        # TODO add ip report
        # TODO add stdout recording
        return u"192.168.1.10:8080"

    def count_length(self):
        """
        Count the length of the current IP address and format according to tk requirement
        "line.column" - line starts from 1 and column starts from 0.
        [reference](http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/text-index.html)

        :return: a string indicates the length of the current ip
        """
        return "1."+str(len(self.current_ip))

    def report_ip(self):
        for i in self.record_reader.get_record():
            if re.search("The IPython Notebook is running at:", i):
                info = i.split("The IPython Notebook is running at:")
                info = info[1].split(':')
                self.current_ip = 'http:'+info[1]
                self.current_port = info[2].split('/')[0]


if __name__ == "__main__":
    Application().mainloop()