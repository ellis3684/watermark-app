from tkinter import filedialog
from PIL import Image, UnidentifiedImageError, ImageDraw, ImageFont, ImageOps


class Watermarker:
    """All watermark functionality of the watermark app is contained within this class."""
    def __init__(self):
        # All attributes are empty to begin with.
        self.base_image = None
        self.watermark_image = None
        self.watermark_text = None
        self.mark_location = None
        self.mark_is_text = False
        self.mark_is_image = False
        self.text_color = None

    def upload_photo(self):
        """Uses Tkinter to ask the user to choose a file for their base image.
        If the file is not an image, an exception is raised."""
        filename = filedialog.askopenfilename()
        try:
            image = Image.open(filename).convert("RGBA")
            self.base_image = ImageOps.exif_transpose(image)
        except UnidentifiedImageError:
            raise Exception("Sorry, that's not an image file. Only image files may be uploaded.")

    def upload_watermark_photo(self):
        """Uses Tkinter to ask the user to choose a file for their watermark image.
        If the file is not an image, an exception is raised."""
        filename = filedialog.askopenfilename()
        try:
            watermark_image = Image.open(filename).convert("RGBA")
            self.watermark_image = ImageOps.exif_transpose(watermark_image)
        except UnidentifiedImageError:
            raise Exception("Sorry, that's not an image file. Only image files may be uploaded.")
        else:
            self.mark_is_image = True

    def get_text(self, text):
        """Takes a string as an argument, and sets the class instance's watermark text attribute to the string."""
        self.watermark_text = text
        self.mark_is_text = True

    def get_location(self, location):
        """Takes a string as an argument, and sets the class instance's watermark location attribute to the string."""
        self.mark_location = location

    def set_mark_location(self, image_width, image_height, mark_width, mark_height):
        """Takes the base image's width and height, and the watermark image's/text's width and height as arguments,
        then uses the watermark location attribute to return the x and y of where the watermark should be placed
        on the base image."""
        margin = 20
        if self.mark_location == "Center":
            x = (image_width / 2) - (mark_width / 2)
            y = (image_height / 2) - (mark_height / 2)
        elif self.mark_location == "Top-Left":
            x = margin
            y = margin
        elif self.mark_location == "Top-Right":
            x = image_width - mark_width - margin
            y = margin
        elif self.mark_location == "Bottom-Left":
            x = margin
            y = image_height - mark_height - margin
        elif self.mark_location == "Bottom-Right":
            x = image_width - mark_width - margin
            y = image_height - mark_height - margin
        else:
            raise Exception("Something went wrong - please re-run the application, and try again, "
                            "or note the details of the bug and notify me.")
        return int(x), int(y)

    def set_text_color(self, color):
        """Takes a string describing color as an argument, and sets the class instance's text color RGBA values
        to the desired color. The alpha is set to 64 to show 25% opacity."""
        if color == "Black text":
            self.text_color = (0, 0, 0, 64)
        elif color == "White text":
            self.text_color = (255, 255, 255, 64)

    def mark_image(self):
        """This uses Python's Pillow library to either draw text on the base image (if the watermark is text), or
        pastes the watermark with 12% opacity over the base image (if the watermark is an image)."""
        image_width, image_height = self.base_image.size
        if self.mark_is_text:
            overlay_image = Image.new("RGBA", (image_width, image_height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay_image)
            text = self.watermark_text
            font_size = int(((image_width + image_height) / 2) // 12)
            font = ImageFont.truetype("segoeui.ttf", font_size)
            mark_width, mark_height = draw.textsize(text, font)
            x, y = self.set_mark_location(image_width, image_height, mark_width, mark_height)
            draw.text((x, y), text, font=font, fill=self.text_color)
            watermarked_image = Image.alpha_composite(self.base_image, overlay_image)
        elif self.mark_is_image:
            mark_image = self.watermark_image
            # If the watermark image's width or height exceeds 1/4 of the base image's width or height, the
            # watermark image is resized while maintaining aspect ratio until it is no more than 1/4 of the
            # base image's size.
            mark_max_size = (image_width // 4, image_height // 4)
            mark_image.putalpha(32)
            mark_image.thumbnail(mark_max_size)
            mark_width, mark_height = mark_image.size
            x, y = self.set_mark_location(image_width, image_height, mark_width, mark_height)
            self.base_image.paste(mark_image, (x, y), mark_image)
            watermarked_image = self.base_image
        else:
            raise Exception("Something went wrong - please re-run the application, and try again, "
                            "or note the details of the bug and notify me.")
        # The watermarked image is shown to the user, and is saved as "watermarked_image.png" in the current directory.
        watermarked_image.show()
        watermarked_image.save("watermarked_image.png")
