import FreeCAD as App
import Part, Sketcher
from ..qrcode_lib import main as qrcode_lib 

def create(obj_name="QRCode"):
    """
    Object creation method
    """


    obj = App.ActiveDocument.addObject('Sketcher::SketchObjectPython', obj_name)
    obj.ViewObject.Proxy = 0
    qrcode(obj)
    ViewProviderQrCode(obj.ViewObject)

    App.ActiveDocument.recompute()

    return obj

class qrcode():
    
    def __init__(self, obj):
        """
        Default constructor
        """

        self.Type = 'QRCode'

        obj.Proxy = self

        obj.addProperty('App::PropertyString', 'Data', 'QR Data', 'QR data').Data = "Text"
        obj.addProperty('App::PropertyLength', 'Width', 'Dimensions', 'QR width').Width = '10 mm'
        obj.addProperty('App::PropertyLength', 'Height', 'Dimensions', 'QR height').Height = '10 mm'

    # Function to create a square
    def process_square(self, obj, x, y, width, height, close_left, close_right, close_top, close_bottom):
        # Define the points of the square
        start_x = x * width
        start_y = y * height
        p1 = App.Vector(start_x, start_y, 0)
        p2 = App.Vector(start_x + width, start_y, 0)
        p3 = App.Vector(start_x + width, start_y - height, 0)
        p4 = App.Vector(start_x, start_y - height, 0)
        
        # Create lines
        if close_bottom:
            obj.addGeometry(Part.LineSegment(p1, p2))
        
        if close_right:
            obj.addGeometry(Part.LineSegment(p2, p3))
            
        if close_top:
            obj.addGeometry(Part.LineSegment(p3, p4))
            
        if close_left:
            obj.addGeometry(Part.LineSegment(p4, p1))

    def generate_qr(self, text):
        qr = qrcode_lib.QRCode()
        qr.add_data(text)
        qr.make()

        return qr.modules
        
    def create_qr_code_sketch(self, obj, text, width, height):
        # Generate QR code
        lines = self.generate_qr(text)

        num_lines = len(lines)
        num_cells_per_line = len(lines[0])

        cell_size = min(width, height) / max(num_lines, num_cells_per_line)
            
        # Add squares to the sketch for each "1" in the QR code
        for y, line in enumerate(lines):
            last_line_index = len(lines) - 1
                    
            for x, cell in enumerate(line):
                last_cell_index = len(line) - 1
                
                up_cell = False if y == 0 else lines[y-1][x]
                down_cell = False if y == last_line_index else lines[y+1][x]
                left_cell = False if x == 0 else lines[y][x-1]
                right_cell = False if x == last_cell_index else lines[y][x+1]
                
                close_left = (cell and not left_cell)
                close_right = (cell and not right_cell)
                close_top = (cell and not up_cell)
                close_bottom = (cell and not down_cell)
                
                self.process_square(obj, x, y, cell_size, cell_size, 
                    close_left=close_left, 
                    close_top=close_top, 
                    close_right=close_right, 
                    close_bottom=close_bottom,
                )
                
        # Recompute the document to apply changes
        obj.recompute()

    def execute(self, obj):
        """
        Called on document recompute
        """

        print('Recomputing {0:s} ({1:s})'.format(obj.Name, self.Type))
        obj.deleteAllGeometry()
        self.create_qr_code_sketch(obj, obj.Data, obj.Width.Value, obj.Height.Value)


class ViewProviderQrCode:
    def __init__(self, obj):
      ''' Set this object to the proxy object of the actual view provider '''
      obj.Proxy = self

    def getDefaultDisplayMode(self):
      ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
      return "Flat Lines"

    def getIcon(self):
        '''Return the icon in XPM format which will appear in the tree view. This method is\
                optional and if not defined a default icon is shown.'''
        return """
            /* XPM */
            static const char * ViewProviderBox_xpm[] = {
            /* columns rows colors chars-per-pixel */
            "16 16 2 1 ",
            "  c None",
            ". c white",
            /* pixels */
            "                ",
            " ......  ...... ",
            " .    .  .    . ",
            " . .. .  . .. . ",
            " . .. .  . .. . ",
            " .    .  .    . ",
            " ......  ...... ",
            "                ",
            "        . .. .. ",
            " ...... . .. .  ",
            " .    . .       ",
            " . .. .   ... . ",
            " . .. . .   . . ",
            " .    .  .      ",
            " ...... .. .. . ",
            "                "
            """