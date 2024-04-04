from PySide2.QtWidgets import QWidget, QSizePolicy, QFileDialog, QLabel, QTableView, QGroupBox, QHBoxLayout, QVBoxLayout, QPushButton, QGridLayout,\
    QDialog, QListView, QTreeWidget, QTreeWidgetItem, QAbstractItemView, QCheckBox, QHeaderView
from PySide2.QtGui import QGuiApplication, QPainter
from PySide2.QtCore import Signal, Slot, QAbstractTableModel, Qt, QStringListModel
from PySide2.QtCharts import QtCharts
from DLPPrinter.dlpColorCalibrator import DLPColorCalibrator
from DLPPrinter.dlpSuperJobFile import DLPSuperJobFile


class DLPSettingsGUI(QWidget):

    def __init__(self, dlp_controller=None, dlp_slicer=None, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.dlp_controller = dlp_controller
        self.dlp_slicer = dlp_slicer
        self.dlp_color_calibrator = DLPColorCalibrator()
        self.dlp_color_calibrator.analysis_completed_signal.connect(self.update_charts)
        self.__current_super_job_group_idx = -1
        self.__current_super_job_subgroup_idx = -1
        self.data_fit_chart_view = None
        self.data_fit_chart = None
        self.main_layout = QHBoxLayout()
        self.__init_table_widget__()
        self.__init_color_calibration_widget()
        self.__default_parameters_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.main_layout.addWidget(self.__default_parameters_widget, stretch=1)
        self.main_layout.addWidget(self.__color_calibration_widget, stretch=2)
        self.setLayout(self.main_layout)
        self.main_layout.update()

    def __init_color_calibration_widget(self, parent=None):
        self.__color_calibration_widget = QGroupBox("Color Correction Options", parent)
        self.__color_calibration_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        color_calibration_layout = QVBoxLayout(self.__color_calibration_widget)

        chart_widget = QWidget(self.__color_calibration_widget)
        chart_layout = QGridLayout(chart_widget)
        self.data_fit_chart = QtCharts.QChart()
        self.data_fit_chart_view = QtCharts.QChartView(self.data_fit_chart)
        self.axis_x = QtCharts.QValueAxis()
        self.axis_x.setTitleText("Pixel Intensity")
        self.axis_x.setRange(0, 1)
        self.data_fit_chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.axis_y = QtCharts.QValueAxis()
        self.axis_y.setTitleText("Voxel Height (\u03BCm)")
        self.axis_y.setRange(0, 10)
        self.data_fit_chart.addAxis(self.axis_y, Qt.AlignLeft)
        chart_layout.addWidget(self.data_fit_chart_view, 0, 0, 1, 4)
        chart_widget.setLayout(chart_layout)

        buttons_widget = QWidget(self.__color_calibration_widget)
        buttons_layout = QHBoxLayout(buttons_widget)
        analyze_data_button = QPushButton("Analyze Data")
        analyze_data_button.clicked.connect(self.analyze_images)
        self.parameters_estimation_label = QLabel(f'Estimated parameters: \u03B1 = {self.dlp_color_calibrator.optimized_parameters[0]:.3f}, \u03B2 = {self.dlp_color_calibrator.optimized_parameters[1]:.3f}, \u03B3 =  {self.dlp_color_calibrator.optimized_parameters[2]:.3f}',
                                buttons_widget)
        buttons_layout.addWidget(analyze_data_button)
        buttons_layout.addWidget(self.parameters_estimation_label)
        buttons_widget.setLayout(buttons_layout)
        color_calibration_layout.addWidget(chart_widget)
        color_calibration_layout.addWidget(buttons_widget)
        self.__color_calibration_widget.setLayout(color_calibration_layout)

    @Slot()
    def analyze_images(self):
        file_names = QFileDialog.getOpenFileNames(caption='Select data', dir='../measured_data/grayscale_measured_data',
                                                  filter="Image Files (*.asc)")
        self.dlp_color_calibrator.analyze_data_files(file_names[0])

    @Slot()
    def update_charts(self):
        self.data_fit_chart = QtCharts.QChart()
        self.data_fit_chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        self.add_series(self.data_fit_chart, "Measured Data", self.dlp_color_calibrator.input_values, self.dlp_color_calibrator.average_data)
        self.add_series(self.data_fit_chart, "Fitted Curve", self.dlp_color_calibrator.input_values,
                        self.dlp_color_calibrator.fitted_curve)
        self.add_series(self.data_fit_chart, "Predicted Result", self.dlp_color_calibrator.input_values,
                        self.dlp_color_calibrator.corrected_output_values)
        series = self.data_fit_chart.series()
        self.data_fit_chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.axis_y.setRange(0, self.dlp_color_calibrator.measured_thickness)
        self.data_fit_chart.addAxis(self.axis_y, Qt.AlignLeft)
        for s in series:
            s.attachAxis(self.axis_x)
            s.attachAxis(self.axis_y)

        self.data_fit_chart_view.setRenderHint(QPainter.Antialiasing)
        self.data_fit_chart_view.setChart(self.data_fit_chart)

        self.parameters_estimation_label.setText(f'Estimated parameters: \u03B1 = {self.dlp_color_calibrator.optimized_parameters[0]:.3f}, \u03B2 = {self.dlp_color_calibrator.optimized_parameters[1]:.3f}, \u03B3 =  {self.dlp_color_calibrator.optimized_parameters[2]:.3f}')

    def add_series(self, chart, title, x, y):
        series = QtCharts.QLineSeries()
        series.setName(title)
        for idx, elem in enumerate(x):
            series.append(x[idx], y[idx])
        chart.addSeries(series)

    def __init_table_widget__(self, parent=None):
        self.__default_parameters_widget = QGroupBox("Default Parameters", parent)
        self.printer_parameters_list = self.dlp_controller.get_default_parameters()
        self.table_view = QTableView()
        self.table_model = self.MyTableModel(parent=self.__default_parameters_widget, data_list=self.printer_parameters_list)
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setVisible(False)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setStretchLastSection(False)
        self.table_view.resizeColumnsToContents()
        self.table_view.update()
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_view.setMinimumWidth(self.table_view.columnWidth(0) +
                                              self.table_view.columnWidth(1) + self.table_view.verticalScrollBar().width())
        apply_button = QPushButton("Apply Changes", self.__default_parameters_widget)
        apply_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        apply_button.clicked.connect(self.dlp_controller.save_default_parameters)
        create_super_job_button = QPushButton("Create Super Job File", self.__default_parameters_widget)
        create_super_job_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        create_super_job_button.clicked.connect(self.__open_super_job_creation_window)
        default_parameters_layout = QGridLayout(self.__default_parameters_widget)
        default_parameters_layout.addWidget(self.table_view, 0, 0, 1, 2)
        default_parameters_layout.addWidget(apply_button, 1, 0)
        default_parameters_layout.addWidget(create_super_job_button, 1, 1)
        self.__default_parameters_widget.setLayout(default_parameters_layout)
        self.__default_parameters_widget.updateGeometry()

    @Slot()
    def __open_super_job_creation_window(self):
        self.super_job_creation_window = QDialog(self)
        self.super_job_creation_window.setWindowTitle("Super Job Creation")
        self.super_job_creation_window.setMinimumHeight( 400)
        self.super_job_creation_window.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.super_job = DLPSuperJobFile()
        left_widget = self.__create_super_job_left_widget(self.super_job_creation_window)
        central_widget = self.__create_super_job_central_widget(self.super_job_creation_window)
        right_widget = self.__create_super_job_right_widget(self.super_job_creation_window)

        window_layout = QHBoxLayout(self.super_job_creation_window)
        window_layout.addWidget(left_widget)
        window_layout.addWidget(central_widget)
        window_layout.addWidget(right_widget)
        self.super_job_creation_window.open()

    def __create_super_job_left_widget(self, parent):
        left_widget = QWidget(parent)
        left_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.super_job_group_tree_widget = QTreeWidget(left_widget)
        # self.super_job_group_tree_widget.setHeaderHidden(True)
        self.super_job_group_tree_widget.setHeaderLabels(["Group ID", "Height (um)"])
        self.super_job_group_tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.super_job_group_tree_widget.itemSelectionChanged.connect(self.__update_super_job_selected_idxs)
        self.super_job_group_tree_widget.setColumnCount(2)
        button_widget = QWidget(left_widget)
        add_group_button = QPushButton("Add Group", button_widget)
        add_group_button.clicked.connect(self.__add_group_to_super_job)
        remove_group_button = QPushButton("Remove Group", button_widget)
        remove_group_button.clicked.connect(self.__remove_group_from_super_job)
        add_subgroup_button = QPushButton("Add SubGroup", button_widget)
        add_subgroup_button.clicked.connect(self.__add_subgroup_to_super_job)
        remove_subgroup_button = QPushButton("Remove SubGroup", button_widget)
        remove_subgroup_button.clicked.connect(self.__remove_subgroup_from_super_job)
        save_job_button = QPushButton("Save SuperJob", button_widget)
        save_job_button.clicked.connect(self.__save_super_job)
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.super_job_group_tree_widget)
        left_layout.addWidget(button_widget)
        button_layout = QGridLayout(button_widget)
        button_layout.addWidget(add_group_button, 0, 0)
        button_layout.addWidget(remove_group_button, 0, 1)
        button_layout.addWidget(add_subgroup_button, 1, 0)
        button_layout.addWidget(remove_subgroup_button, 1, 1)
        button_layout.addWidget(save_job_button, 2, 0, 1, 2)
        return left_widget

    def __create_super_job_central_widget(self, parent):
        central_widget = QWidget(parent)
        central_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.layer_list_view = QListView(central_widget)
        self.layer_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.layer_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layer_list_model = QStringListModel(central_widget)
        self.layer_list_model.setStringList([])
        self.layer_list_view.setModel(self.layer_list_model)
        add_layers_button = QPushButton("Add Layers", central_widget)
        add_layers_button.clicked.connect(self.__add_layers_to_subgroup)
        remove_layers_button = QPushButton("Remove Layers", central_widget)
        remove_layers_button.clicked.connect(self.__remove_layers_from_subgroup)
        button_widget = QWidget(central_widget)
        button_layout = QGridLayout(button_widget)
        button_layout.addWidget(add_layers_button, 0, 0)
        button_layout.addWidget(remove_layers_button, 0, 1)
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(self.layer_list_view)
        central_layout.addWidget(button_widget)
        return central_widget

    def __create_super_job_right_widget(self, parent):
        right_widget = QWidget(parent)
        self.right_table_view = QTableView(right_widget)
        self.right_table_model = self.MyTableModel(parent=right_widget, data_list={})
        self.right_table_view.setModel(self.right_table_model)
        self.right_table_view.horizontalHeader().setVisible(False)
        self.right_table_view.verticalHeader().setVisible(False)
        self.right_table_view.resizeColumnsToContents()
        self.right_table_model.dataChanged.connect(self.__update_super_job_heights)
        self.save_relative_path_checkbox = QCheckBox("Save Relative Path", right_widget)
        self.save_relative_path_checkbox.setChecked(True)
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(self.right_table_view)
        right_layout.addWidget(self.save_relative_path_checkbox)
        return right_widget

    @Slot()
    def __save_super_job(self):
        file_name = QFileDialog.getSaveFileName(caption='Select Job File Name', dir='../', parent=self,
                                                filter="Files (*.json)")
        if len(file_name[0]) > 0:
            self.super_job.save_job_file(file_name[0], save_relative_paths=self.save_relative_path_checkbox.isChecked())

    @Slot()
    def __update_super_job_heights(self):
        current_group = self.super_job.get_group(self.__current_super_job_group_idx)
        current_subgroup = current_group.get_subgroup(self.__current_super_job_subgroup_idx)
        root_item = self.super_job_group_tree_widget.topLevelItem(self.__current_super_job_group_idx)
        child_item = root_item.child(self.__current_super_job_subgroup_idx)
        child_item.setText(1, str(current_subgroup.get_subgroup_height()))
        root_item.setText(1, str(current_group.get_group_height()))
        child_item.setTextAlignment(1, Qt.AlignRight)
        root_item.setTextAlignment(1, Qt.AlignRight)

    @Slot()
    def __update_super_job_selected_idxs(self):
        if len(self.super_job_group_tree_widget.selectedItems()) < 1:
            self.__current_super_job_group_idx = -1
            self.__current_super_job_subgroup_idx = -1
        else:
            current_item = self.super_job_group_tree_widget.selectedItems()[0]
            if current_item.parent():
                root_item = current_item.parent()
                self.__current_super_job_group_idx = self.super_job_group_tree_widget.indexOfTopLevelItem(root_item)
                self.__current_super_job_subgroup_idx = root_item.indexOfChild(current_item)
            else:
                self.__current_super_job_group_idx = self.super_job_group_tree_widget.indexOfTopLevelItem(current_item)
                self.__current_super_job_subgroup_idx = -1
        self.__update_layer_list_model()
        self.__update_setting_list_model()

    @Slot()
    def __update_layer_list_model(self):
        if self.__current_super_job_subgroup_idx < 0:
            self.layer_list_model.setStringList([])
        else:
            current_group = self.super_job.get_group(self.__current_super_job_group_idx)
            current_subgroup = current_group.get_subgroup(self.__current_super_job_subgroup_idx)
            self.layer_list_model.setStringList(current_subgroup.get_layers())
        return

    @Slot()
    def __update_setting_list_model(self):
        if self.__current_super_job_subgroup_idx < 0:
            self.right_table_model = self.MyTableModel(parent=self.right_table_view, data_list={})
            self.right_table_view.setModel(self.right_table_model)
        else:
            current_group = self.super_job.get_group(self.__current_super_job_group_idx)
            current_subgroup = current_group.get_subgroup(self.__current_super_job_subgroup_idx)
            self.right_table_model = self.MyTableModel(parent=self.right_table_view,data_list=current_subgroup.get_settings())
            self.right_table_view.setModel(self.right_table_model)
            self.right_table_model.dataChanged.connect(self.__update_super_job_heights)
            self.right_table_view.update()
            self.right_table_view.resizeColumnsToContents()
            self.right_table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.right_table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.right_table_view_fixed_width = self.right_table_view.columnWidth(0) + self.right_table_view.columnWidth(1) + self.right_table_view.verticalScrollBar().width()
            self.right_table_view.setMinimumWidth(self.right_table_view_fixed_width)

    @Slot()
    def __add_layers_to_subgroup(self):
        if self.__current_super_job_subgroup_idx < 0:
            return
        else:
            current_group = self.super_job.get_group(self.__current_super_job_group_idx)
            current_subgroup = current_group.get_subgroup(self.__current_super_job_subgroup_idx)
            file_names = QFileDialog.getOpenFileNames(caption='Select images', dir='../',
                                                      filter="Image Files (*.png *.jpg *.bmp)")
            current_subgroup.add_layers(file_names[0])
            self.__update_super_job_heights()
            self.__update_layer_list_model()

    @Slot()
    def __remove_layers_from_subgroup(self):
        if self.__current_super_job_subgroup_idx < 0:
            return
        else:
            current_group = self.super_job.get_group(self.__current_super_job_group_idx)
            current_subgroup = current_group.get_subgroup(self.__current_super_job_subgroup_idx)
            selected_idxs = self.layer_list_view.selectedIndexes()
            idxs = [i.row() for i in selected_idxs]
            current_subgroup.remove_layers(idxs)
            self.__update_super_job_heights()
            self.__update_layer_list_model()

    @Slot()
    def __add_group_to_super_job(self):
        self.super_job.add_group()
        self.__add_group_to_tree(self.super_job.size()-1)

    @Slot()
    def __add_subgroup_to_super_job(self):
        if len(self.super_job_group_tree_widget.selectedItems()) < 1:
            return
        current_item = self.super_job_group_tree_widget.selectedItems()[0]
        if current_item.parent():
            root_item = current_item.parent()
            group_idx = self.super_job_group_tree_widget.indexOfTopLevelItem(root_item)
        else:
            root_item = current_item
            group_idx = self.super_job_group_tree_widget.indexOfTopLevelItem(root_item)
        group = self.super_job.get_group(group_idx)
        group.add_subgroup()
        child_item = QTreeWidgetItem(root_item)
        child_item.setText(0, group.get_subgroup_id(group.size()-1))
        # self.__update_super_job_heights()
        child_item.setText(1, str(group.get_subgroup(group.size()-1).get_subgroup_height()))
        child_item.setTextAlignment(1, Qt.AlignRight)
        self.super_job_group_tree_widget.resizeColumnToContents(0)
        self.super_job_group_tree_widget.resizeColumnToContents(1)

    @Slot()
    def __remove_group_from_super_job(self):
        if len(self.super_job_group_tree_widget.selectedItems()) < 1:
            return
        current_item = self.super_job_group_tree_widget.selectedItems()[0]
        if current_item.parent():
            return
        else:
            root_item = current_item
            group_idx = self.super_job_group_tree_widget.indexOfTopLevelItem(root_item)
        self.super_job.remove_group(group_idx)
        self.super_job_group_tree_widget.clear()
        for idx in range(self.super_job.size()):
            self.__add_group_to_tree(idx)
        top_level_count = self.super_job_group_tree_widget.topLevelItemCount()
        if top_level_count > 0:
            self.super_job_group_tree_widget.topLevelItem(max(0, group_idx-1)).setSelected(True)

    @Slot()
    def __remove_subgroup_from_super_job(self):
        if len(self.super_job_group_tree_widget.selectedItems()) < 1:
            return
        current_item = self.super_job_group_tree_widget.selectedItems()[0]
        if not current_item.parent():
            return
        else:
            root_item = current_item.parent()
            group_idx = self.super_job_group_tree_widget.indexOfTopLevelItem(root_item)
            subgroup_idx = root_item.indexOfChild(current_item)
        group = self.super_job.get_group(group_idx)
        group.remove_subgroup(subgroup_idx)
        self.super_job_group_tree_widget.clear()
        for idx in range(self.super_job.size()):
            self.__add_group_to_tree(idx)
        if group.size() > 0:
            self.super_job_group_tree_widget.topLevelItem(group_idx).child(max(0, subgroup_idx-1)).setSelected(True)
        else:
            self.super_job_group_tree_widget.topLevelItem(group_idx).setSelected(True)

    @Slot()
    def __add_group_to_tree(self, idx):
        group = self.super_job.get_group(idx)
        root_item = QTreeWidgetItem(self.super_job_group_tree_widget)
        root_item.setText(0, self.super_job.get_group_id(idx))
        root_item.setText(1, str(group.get_group_height()))
        root_item.setTextAlignment(1, Qt.AlignRight)
        for child_idx in range(group.size()):
            child_item = QTreeWidgetItem(root_item)
            child_item.setText(0, group.get_subgroup_id(child_idx))
            child_item.setText(1, str(group.get_subgroup(child_idx).get_subgroup_height()))
            child_item.setTextAlignment(1, Qt.AlignRight)
        root_item.setExpanded(True)
        self.super_job_group_tree_widget.resizeColumnToContents(0)
        self.super_job_group_tree_widget.resizeColumnToContents(1)

    class MyTableModel(QAbstractTableModel):
        def __init__(self, parent, data_list, *args):
            QAbstractTableModel.__init__(self, parent, *args)
            self.parent = parent
            self.data_list = data_list

        def rowCount(self, parent):
            return len(self.data_list)

        def columnCount(self, parent):
            return 2

        def data(self, index, role):
            if not index.isValid():
                return None
            elif role != Qt.DisplayRole:
                return None
            return list(self.data_list.items())[index.row()][index.column()]

        def setData(self, index, value, role):
            if role == Qt.EditRole:
                if not index.isValid():
                    return False
                elif index.column() == 0:
                    return False
                else:
                    key = list(self.data_list.items())[index.row()][0]
                    old_value = list(self.data_list.items())[index.row()][1]
                    try:
                        if isinstance(old_value, float):
                            self.data_list[key] = float(value)
                        elif isinstance(old_value, bool):
                            if value == "True" or value == "true":
                                self.data_list[key] = True
                            else:
                                self.data_list[key] = False
                        elif isinstance(old_value, str):
                            if index.row() == 0:
                                if not (value.upper() == "TOP-DOWN" or value.upper() == "BOTTOM-UP"):
                                    return False
                            self.data_list[key] = str(value).upper()
                        elif isinstance(old_value, int):
                            self.data_list[key] = int(value)
                    except ValueError:
                        return False
                    self.dataChanged.emit(index, index)
                    return True
            else:
                return False

        def flags(self, index):
            if not index.isValid() or index.column() == 0:
                return Qt.ItemIsEnabled
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                                Qt.ItemIsEditable)


