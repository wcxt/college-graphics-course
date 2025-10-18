import sys
from PySide6.QtCore import QDate, QFile, Qt, QTextStream
from PySide6 import QtGui, QtWidgets 

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100
    rd, gd, bd = r / 255.0, g / 255.0, b / 255.0
    k = 1 - max(rd, gd, bd)
    c = (1 - rd - k) / (1 - k)
    m = (1 - gd - k) / (1 - k)
    y = (1 - bd - k) / (1 - k)
    return round(c * 100), round(m * 100), round(y * 100), round(k * 100)

def cmyk_to_rgb(c, m, y, k):
    c, m, y, k = [v / 100.0 for v in (c, m, y, k)]
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return round(r), round(g), round(b)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Project 1")
        self.setMinimumSize(600, 600)

        central = QtWidgets.QTextEdit("Main content")
        self.setCentralWidget(central)

        # Create tools dock
        dock = QtWidgets.QDockWidget("Narzędzia", self)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setFixedWidth(220)
        toolbox = QtWidgets.QWidget()
        dock.setWidget(toolbox)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        layout = QtWidgets.QVBoxLayout(toolbox)
        layout.addSpacing(25)

        # Primitive button choice
        self.primitive_group = QtWidgets.QButtonGroup()
        line_rb = QtWidgets.QRadioButton('Linia')
        rect_rb = QtWidgets.QRadioButton('Prostokąt')
        circle_rb = QtWidgets.QRadioButton('Okrąg')
        rect_rb.setChecked(True)
        self.primitive_group.addButton(line_rb, 0)
        self.primitive_group.addButton(rect_rb, 1)
        self.primitive_group.addButton(circle_rb, 2)
        layout.addWidget(line_rb)
        layout.addWidget(rect_rb)
        layout.addWidget(circle_rb)

        layout.addSpacing(25)

        # TextBox for creating primitives
        layout.addWidget(QtWidgets.QLabel("Parametry:"))
        self.param_textbox = QtWidgets.QPlainTextEdit()
        self.param_textbox.setPlaceholderText("Dla linii: x1 y1 x2 y2\nDla prostokąta: x y w h\nDla okręgu: x y r")
        self.param_textbox.setFixedHeight(100)
        create_button = QtWidgets.QPushButton('Utwórz z parametrów')
        layout.addWidget(self.param_textbox)
        layout.addWidget(create_button)

        # Save/Load buttons
        hbox = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("Zapisz")
        load_button = QtWidgets.QPushButton("Otwórz")
        hbox.addWidget(save_button)
        hbox.addWidget(load_button)
        layout.addLayout(hbox)

        layout.addSpacing(25)

        # Color select
        layout.addWidget(QtWidgets.QLabel('Wybór koloru'))
        self.color_cbox = QtWidgets.QComboBox()
        self.color_cbox.addItems(["RGB", "CMYK"])
        self.color_cbox.currentTextChanged.connect(self.on_color_mode_changed)
        layout.addWidget(self.color_cbox)

        layout.addSpacing(10)
        
        # RGB controls
        self.rgb_controls = {}
        for name in ('R', 'G', 'B'):
            row = QtWidgets.QHBoxLayout()
            value_label = QtWidgets.QLabel(name)
            value_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
            value_spin =QtWidgets.QSpinBox() 
            value_spin.setRange(0, 255)
            value_slider.setRange(0, 255)

            value_slider.valueChanged.connect(lambda v, n=name: self.on_rgb_changed(n, v))
            value_spin.valueChanged.connect(lambda v, n=name: self.on_rgb_changed(n, v))
            
            row.addWidget(value_label)
            row.addWidget(value_slider)
            row.addWidget(value_spin)
            layout.addLayout(row)
            self.rgb_controls[name] = (value_slider, value_spin)

        # CMYK controls
        self.cmyk_controls = {}
        for name in ('C', 'M', 'Y', 'K'):
            row = QtWidgets.QHBoxLayout()
            value_label = QtWidgets.QLabel(name)
            value_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
            value_spin = QtWidgets.QSpinBox() 
            value_slider.setRange(0, 100)
            value_spin.setRange(0, 100)

            value_slider.valueChanged.connect(lambda v, n=name: self.on_cmyk_changed(n, v))
            value_spin.valueChanged.connect(lambda v, n=name: self.on_cmyk_changed(n, v))

            row.addWidget(value_label)
            row.addWidget(value_slider)
            row.addWidget(value_spin)
            layout.addLayout(row)
            self.cmyk_controls[name] = (value_slider, value_spin)


        # Color preview 
        self.color_preview = QtWidgets.QLabel()
        self.color_preview.setFixedHeight(40)
        self.color_preview.setFrameShape(QtWidgets.QFrame.Shape.Box)
        layout.addWidget(QtWidgets.QLabel('Podgląd koloru:'))
        layout.addWidget(self.color_preview)

        layout.addStretch()
        
        self.updating_color = False
        self.on_color_mode_changed("RGB")
        self.set_rgb(0, 0, 0)

    def on_color_mode_changed(self, mode):
        is_rgb = mode == "RGB"
        is_cmyk = mode == "CMYK"
        for _, (value_slider, value_text) in self.rgb_controls.items():
            value_slider.setDisabled(is_cmyk)
            value_text.setDisabled(is_cmyk)
        for _, (value_slider, value_text) in self.cmyk_controls.items():
            value_slider.setDisabled(is_rgb)
            value_text.setDisabled(is_rgb)

    def on_rgb_changed(self, name, value):
        if self.updating_color: return
        self.updating_color = True 
        value_slider, value_text = self.rgb_controls[name]
        value_slider.setValue(value)
        value_text.setValue(value)

        r = self.rgb_controls['R'][0].value()
        g = self.rgb_controls['G'][0].value()
        b = self.rgb_controls['B'][0].value()
        cmyk = rgb_to_cmyk(r, g, b)

        for name, val in zip(('C', 'M', 'Y', 'K'), cmyk):
            cmyk_value_slider, cmyk_value_spin = self.cmyk_controls[name]
            cmyk_value_slider.setValue(val)
            cmyk_value_spin.setValue(val)
        
        self.update_color_preview(r, g, b)
        self.updating_color = False
            
    def on_cmyk_changed(self, name, value):
        if self.updating_color: return
        self.updating_color = True 
        value_slider, value_text = self.cmyk_controls[name]
        value_slider.setValue(value)
        value_text.setValue(value)

        c = self.cmyk_controls['C'][0].value()
        m = self.cmyk_controls['M'][0].value()
        y = self.cmyk_controls['Y'][0].value()
        k = self.cmyk_controls['K'][0].value()
        r, g, b = cmyk_to_rgb(c, m, y, k) 

        for name, val in zip(('R', 'G', 'B'), (r, g, b)):
            rgb_value_slider, rgb_value_spin = self.rgb_controls[name]
            rgb_value_slider.setValue(val)
            rgb_value_spin.setValue(val)

        self.update_color_preview(r, g, b)
        self.updating_color = False

    def update_color_preview(self, r, g, b):
        col = QtGui.QColor(r, g, b)
        pix = QtGui.QPixmap(200, 40)
        pix.fill(col)
        self.color_preview.setPixmap(pix)

    def set_rgb(self, r, g, b):
        self.updating_color = True
        for name, val in zip(('R','G','B'), (r,g,b)):
            value_slider, value_spin = self.rgb_controls[name]
            value_slider.setValue(val)
            value_spin.setValue(val)

        cmyk = rgb_to_cmyk(r,g,b)
        for name, val in zip(('C', 'M', 'Y', 'K'), cmyk):
            value_slider, value_spin = self.cmyk_controls[name]
            value_slider.setValue(val)
            value_spin.setValue(val)

        self.update_color_preview(r,g,b)
        self.updating_color = False



    # def create_dock(self):
    #     group = QtWidgets.QGroupBox("Primitives")
    #     layout = QtWidgets.QVBoxLayout()
    #     layout.addWidget(QtWidgets.QPushButton("Triangle"))
    #     layout.addWidget(QtWidgets.QPushButton("Triangle"))
    #     layout.addWidget(QtWidgets.QPushButton("Triangle"))
    #     group.setLayout(layout)
    #
    #     flayout = QtWidgets.QVBoxLayout()
    #     flayout.addWidget(group, 0, alignment=Qt.AlignmentFlag.AlignTop)
    #     widget = QtWidgets.QWidget()
    #     widget.setLayout(flayout)
    #
    #     dockWidget.setWidget(widget)
    #     return dockWidget
    #
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    print("Starting")
    sys.exit(app.exec())
