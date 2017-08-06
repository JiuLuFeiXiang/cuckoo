import Tkinter as tkinter
import subprocess
import logging

log = logging.getLogger(__name__)

class ScreenRecord:
    def __init__(self, output_path, filename):
        self.vcodecs = {}
        self.vcodecs["h264_lossless"] = ["-c:v", "libx264", "-g", "15", "-crf", "0", "-pix_fmt", "yuv444p"]
        self.vcodecs["h264"] = ["-c:v", "libx264", "-vprofile", "baseline", "-g", "15", "-crf", "1", "-pix_fmt", "yuv420p"]
        self.vcodecs["mpeg4"] = ["-c:v", "mpeg4", "-g", "15", "-qmax", "1", "-qmin", "1"]
        #self.vcodecs["xvid"] = ["-c:v", "libxvid", "-g", "15", "-b:v", "40000k"]
        self.vcodecs["huffyuv"] = ["-c:v", "huffyuv"]
        self.vcodecs["ffv1"] = ["-c:v", "ffv1", "-coder", "1", "-context", "1"]
        self.vcodecs["vp8"] = ["-c:v", "libvpx", "-g", "15", "-qmax", "1", "-qmin", "1"]
        self.vcodecs["theora"] = ["-c:v", "libtheora", "-g", "15", "-b:v", "40000k"]
        #self.vcodecs["dirac"] = ["-c:v", "libschroedinger", "-g", "15", "-b:v", "40000k"]

        self.filename = filename
        self.output_path = output_path
        self.output = self.output_path + "\\" + self.filename

        self.proc = None

    def get_desktop_resolution(self):
        root = tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return (width, height)

    def stop(self):
        try:
            self.proc.kill()
        except OSError as e:
            log.debug("Error stop recording screen: %s", e)
        except Exception as e:
            log.exception("Unable to stop recording screen with pid %d: %s",
                              self.proc.pid, e)
    
    def record(self):
        resl = self.get_desktop_resolution()
        width = resl[0]
        height = resl[1]

        args =  [
            'ffmpeg',
            '-f', 'gdigrab',
            '-framerate', str(15),
            '-offset_x', str(0),
            '-offset_y', str(0),
            '-video_size', "%dx%d" %(width, height),
            '-i', 'desktop',
       
        ]

        args += self.vcodecs["h264"]
        args += [self.output]

        self.proc = subprocess.Popen(args, shell=False)