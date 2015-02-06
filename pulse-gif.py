#!/usr/bin/env python
from __future__ import division
import sys, os
import argparse
from PIL import Image, ImageDraw, ImageFont

DEFAULT_MARGINS = {"top": 10, "bottom": 10, "left": 10, "right": 10}

PULSE_RATE = 20
TICKS_PER_SECOND = 10
# Won't work accurately for any integer because of rounding errors

FONT_DIR = "/Users/diegolascasas/Library/Fonts"
TMP_DIR = "/var/tmp/freq-gif"

class PulseGif:
    def __init__(
            self,
            text = "[No text provided]",
            font_name = "Montserrat-Regular",
            font_size = 40,
            margins = DEFAULT_MARGINS,
            bg_color = (255,255,255),
            frequency_per_second = 0.166666667,
    ):
        self.set_text(text, font_name, font_size)
        self.set_margins(margins)
        self.bg_color = bg_color
        self.frequency_per_second = frequency_per_second

        
    def set_margins(self, margins):
        sniffer = ImageDraw.Draw(Image.new("RGB",(10,10)))
        size = sniffer.textsize(self._text,self._font)
        self._img_dimensions = (size[0] + margins["left"] + margins["right"],
                               size[1] + margins["top"] + margins["bottom"])
        self._text_loc = (margins["top"], margins["left"])
        self.frames_uptodate = False

        
    def set_text(self, text = None, font_name = None, font_size = None):
        if text:
            self._text = text
        if font_name:
            self._font_name = font_name
        if font_size:
            self._font_size = font_size
        font_path = "{}/{}.ttf".format(FONT_DIR,self._font_name)
        self._font = ImageFont.truetype(font_path, self._font_size)
        self.frames_uptodate = False
    
    def _make_text_frame(self, alpha):
        frame  = Image.new("RGB", self._img_dimensions, self.bg_color)
        drawer = ImageDraw.Draw(frame)
        drawer.text(self._text_loc, self._text, font=self._font,
                    fill=(alpha, alpha, alpha))
        frame.info["alpha"] = alpha
        return(frame)


    def update_frames(self):
        self.frames = [self._make_text_frame(alpha)
                       for alpha in xrange(25,155,PULSE_RATE)]
        self.frames_uptodate = True

        
    def write_gif(self, fname, clean=True):        
        if not self.frames_uptodate:
            self.update_frames()

        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)
        else:
            filelist = [f for f in os.listdir(TMP_DIR) if f.endswith(".gif")]
            for f in filelist:
                os.remove("%s/%s" % (TMP_DIR,f))
                
        ## PULSE FRAMES FIRST
        for im in self.frames:
            im.save("%s/__pulse%03d.gif" % (TMP_DIR, im.info["alpha"]))

        ## THEN IDLE FRAMES
        seconds_per_loop = 1 / self.frequency_per_second
        n_frames = seconds_per_loop * TICKS_PER_SECOND
        n_idle_frames = int(n_frames - len(self.frames))
        for i in xrange(n_idle_frames):
            self.frames[-1].save("%s/_idle%d.gif" % (TMP_DIR,i))

        ## Note: must make sure pulse frames are listed before idle frames            
        tick_size = 100 // TICKS_PER_SECOND    
        cmd = "convert -delay {}x100 {}/*.gif -loop 0 {}"
        os.system(cmd.format(tick_size, TMP_DIR, fname))

# os.system("convert -layers Optimize anim.gif anim_optimized.gif")
def usage():
    print ""

def main():
    parser = argparse.ArgumentParser(
        description='Creates a gif pulsating in a given frequency.')
    parser.add_argument("text", metavar="Text", default=["No","Text"],nargs="+",
                        help='The text you want printed in the gif image.')
    parser.add_argument(
        '--frequency', '-f', type=float, default=0.25,
        metavar="F", help='Frequency (per second) of the pulse. Default: 0.25.'
    )
    parser.add_argument(
        '--output', '-o', default="pulse.gif",metavar="FILENAME",
        help='Filename of the resulting gif. If the .gif sufix is not present it is added automaticaly. Default: pulse.gif)'
    )

    args=parser.parse_args()
    if args.output[-4:] != ".gif":
        args.output+=".gif"
    
    im = PulseGif(text=" ".join(args.text),
                  frequency_per_second = args.frequency)
    im.write_gif(args.output)
    

if __name__ == "__main__": 
    main()
