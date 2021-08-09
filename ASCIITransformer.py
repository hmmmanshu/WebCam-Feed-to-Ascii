import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class ASCIITransformer:
    def __init__(self,  height=25, dark_style=False, font_size=20):
        self.new_height = height
        self.shading_style = "@%#*+=-:. "
        self.dark_style = dark_style
        if dark_style:
            self.shading_style = self.shading_style[::-1]
        self.font_size = font_size

    def __to_ascii(self, brightness):
        return self.shading_style[round((brightness / 255) * (len(self.shading_style) - 1))]

    def __stringify(self, img=None):
        if img is None:
            img = self.img

        img_height, img_width = img.shape
        new_width = (2 * self.new_height * img_width) // img_height

        scaled_img = cv2.resize(img, dsize=(
            new_width, self.new_height), interpolation=cv2.INTER_CUBIC)

        ascii_arr = np.empty((self.new_height, new_width), dtype=str)
        for i in range(self.new_height):
            for j in range(new_width):
                ascii_arr[i, j] = self.__to_ascii(scaled_img[i, j])

        self.ascii_arr_shape = ascii_arr.shape
        lines = '\n'.join([''.join([''.join(char) for char in row])
                          for row in ascii_arr])
        return lines

    def __imagify(self, img=None):
        lines = self.__stringify(img)

        bg_color, fg_color = ((0, 0), (255, 255)) if self.dark_style is True else (
            (255, 255), (0, 0))
        img_size = (int(self.ascii_arr_shape[1] * self.font_size * 0.65), int(
            self.ascii_arr_shape[0] * self.font_size * 1.2))
        img = Image.new('LA', img_size, bg_color)
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype("RobotoMono-Bold.ttf", self.font_size)
        d.text((10, 10), lines, fill=fg_color, font=font, spacing=0.5)
        return img

    def transform_to_txt(self, fname="ascii-img.txt"):
        ascii_lines = self.__stringify()
        file = open(fname, "w")
        file.writelines(ascii_lines)

    def transform_to_img(self, fname="ascii-img.png"):
        img = self.__imagify()
        img.save(fname)

    def transform_to_video(self):
        print("Options")
        print("q - quit")
        print("= - incerase height")
        print("- - decerase height")
        print("] - increase font size")
        print("[ - decrease font size")
        vid = cv2.VideoCapture(0)  # Cam feed
        while (True):
            ret, frame = vid.read()
            grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ascii_img = np.asarray(self.__imagify(grayscale))[:, :, :1]
            cv2.imshow('frame', ascii_img)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == ord('d'):
                self.__reverse_shading()
            elif key == ord('='):
                self.new_height += 1
            elif key == ord('-'):
                self.new_height -= 1
            elif key == ord(']'):
                self.font_size += 1
            elif key == ord('['):
                self.font_size -= 1

        vid.release()
        cv2.destroyAllWindows()

    def __reverse_shading(self):
        self.dark_style = not self.dark_style
        self.shading_style = self.shading_style[::-1]
