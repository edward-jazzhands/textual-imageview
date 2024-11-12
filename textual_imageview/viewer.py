import math

from PIL import Image
from textual import events
from textual.app import RenderResult
from textual.widget import Widget

from textual_imageview.img import ImageView


class ImageViewer(Widget):
    DEFAULT_CSS = """
    ImageViewer{
        min-width: 8;
        min-height: 8;
    }
    """

    def __init__(
            self,
            image: Image.Image,
            min_zoom: int = 10,
            max_zoom: int = 1,
            nested: bool = False,
        ):
        """A widget that displays an image and allows zooming and panning.
        
        Args:
            image (Image.Image): The image to display.
            min_zoom (int, optional): The minimum zoom level. Defaults to 10.
            max_zoom (int, optional): The maximum zoom level. Defaults to 0.
            nested (bool, optional): Whether the ImageViewer will be a child inside another Widget. Defaults to False.

        Setting `nested` to True will make the ImageViewer only respond to mouse events when it has focus. """
        
        super().__init__()
        if not isinstance(image, Image.Image):
            raise TypeError(
                f"Expected PIL Image, but received '{type(image).__name__}' instead."
            )

        self.image = ImageView(image)
        self.mouse_down = False
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.nested = nested

    def on_show(self):
        w, h = self.size.width, self.size.height
        img_w, img_h = self.image.size

        # Compute zoom such that image fits in container
        zoom_w = math.log(max(w, 1) / img_w, self.image.ZOOM_RATE)
        zoom_h = math.log((max(h, 1) * 2) / img_h, self.image.ZOOM_RATE)
        zoom = max(0, math.ceil(max(zoom_w, zoom_h)))
        self.image.set_zoom(zoom)

        # Position image in center of container
        img_w, img_h = self.image.zoomed_size
        self.image.origin_position = (-round((w - img_w) / 2), -round(h - img_h / 2))
        self.image.set_container_size(w, h, maintain_center=False)

        self.refresh()

    def on_mouse_scroll_down(self, event: events.MouseScrollDown):
        """scroll down to zoom out"""

        func_pass = False
        if self.parent.has_focus or not self.nested:
            func_pass = True

        if func_pass:

            offset = self.region.offset
            zoom_position = self.image.rowcol_to_xy(event.y, event.x, (offset.y, offset.x)) 
            zoom_level = self.image._zoom

            if zoom_level < self.min_zoom:
                self.image.zoom(1, zoom_position)

            self.refresh()
            event.stop()

    def on_mouse_scroll_up(self, event: events.MouseScrollDown):
        """scroll up to zoom in"""

        func_pass = False
        if self.parent.has_focus or not self.nested:
            func_pass = True

        if func_pass:

            offset = self.region.offset
            zoom_position = self.image.rowcol_to_xy(event.y, event.x, (offset.y, offset.x))
            zoom_level = self.image._zoom

            if zoom_level > self.max_zoom:
                self.image.zoom(-1, zoom_position)

            self.refresh()
            event.stop()

    def on_mouse_down(self, _: events.MouseDown):
        self.mouse_down = True
        self.capture_mouse(capture=True)

    def on_mouse_up(self, _: events.MouseDown):
        self.mouse_down = False
        self.capture_mouse(capture=False)

    def on_mouse_move(self, event: events.MouseMove):
        if self.mouse_down and (event.delta_x != 0 or event.delta_y != 0):
            self.image.move(event.delta_x, event.delta_y * 2)
            self.refresh()

    def on_resize(self, event: events.Resize):
        self.image.set_container_size(event.size.width, event.size.height)
        self.refresh()

    def render(self) -> RenderResult:
        return self.image
