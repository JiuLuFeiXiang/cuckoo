import Tkinter as tkinter
import subprocess
import logging
import os

log = logging.getLogger(__name__)

# ffmpeg is currently our solid choice to record screen, ..
# others not suitable for us, like working only on Linux http://www.blendernation.com/ or too advanced for just recording screen - Opencv http://docs.opencv.org/master/d6/d00/tutorial_py_root.html,   
class ScreenRecord:
    def __init__(self, path, fname):
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

        self.fname = fname
        self.path = path
        self.file = self.path + "\\" + self.fname

        self.proc = None

    def get_desktop_resolution(self):
        root = tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return (width, height)

    def is_exe(self, fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def is_binary_exist(self, program):
        fpath, fname = os.path.split(program)
        if fpath:
            if self.is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if self.is_exe(exe_file):
                    return exe_file
        
        return None

    def stop(self):
        binary_to_check = 'ffmpeg.exe'
        binary_existence = str(self.is_binary_exist(binary_to_check))
        
        try:       
            if not binary_existence:
                log.debug('%s does not exist', binary_to_check)
            elif not self.proc:
                log.debug('%s could not be started', binary_to_check)
            else:
                log.debug("%s exists at ... %s", binary_to_check, binary_existence)
                stdout_data = self.proc.communicate("q\n")[0]
        except OSError as e:
            log.debug("Error stop recording screen: %s", e)
        except Exception as e:
            log.debug("Unable to stop recording screen with pid %d: exception=%s and stdout=%s",
                              self.proc.pid, e, stdout_data)
    
    def record(self):
        rsl = self.get_desktop_resolution()
        width = rsl[0]
        height = rsl[1]

        args =  [
            'ffmpeg.exe', '-y',
            '-f', 'gdigrab',
            '-framerate', str(15),
            # '-offset_x', str(0),
            # '-offset_y', str(0),
            # '-video_size', "%dx%d" %(width, height),
            '-i', 'desktop',
        ]

        #args += self.vcodecs["h264"]
        args += [self.file]

        self.proc = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=4096)
