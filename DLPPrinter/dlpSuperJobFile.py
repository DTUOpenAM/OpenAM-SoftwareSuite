import numpy as np
from PySide2.QtCore import QFileInfo, QFile, QDir, QIODevice, QJsonDocument

class DLPSuperJobFile:

    def __init__(self):
        self.__groups_list = []
        self.__groups_id = []

    def size(self):
        return len(self.__groups_list)

    def get_group(self, idx):
        return self.__groups_list[idx]

    def get_group_id(self, idx):
        return self.__groups_id[idx]

    def get_groups_ids(self):
        return self.__groups_id

    def add_group(self):
        self.__groups_id.append("Group %i" % len(self.__groups_list))
        self.__groups_list.append(SuperJobGroup())

    def remove_group(self, idx):
        self.__groups_list.pop(idx)
        self.__groups_id = ["Group %i" % idx for idx,_ in enumerate(self.__groups_list)]

    def remove_groups(self, idx_list):
        idx_set = set(idx_list)
        self.__groups_list = [i for j, i in enumerate(self.__groups_list) if j not in idx_set]
        self.__groups_id = ["Group %i" % idx for idx,_ in enumerate(self.__groups_list)]

    def save_job_file(self, filename, save_relative_paths = True):
        file = QFile(filename)
        fileinfo = QFileInfo(file)
        relative_path_dir = QDir(fileinfo.absolutePath())
        json_data = {"groups": []}
        number_of_decimals = 6
        for group_id, group in enumerate(self.__groups_list):
            group_json = {}
            sorted_layers, sorted_height, sorted_amplitude, sorted_exposure, sorted_subgroup_id = group.sort_subgroups_layers()
            sorted_settings = []
            print(sorted_height)
            group_etc_ms = 0
            for idx, sub_id in enumerate(sorted_subgroup_id):
                settings = {}
                current_settings = group.get_subgroup(sub_id).get_settings()
                if idx == 0:
                    for key in saved_keywords:
                        settings[key] = current_settings[key]
                    layer_height = round(sorted_height[idx], number_of_decimals)
                else:
                    previous_settings = group.get_subgroup(sorted_subgroup_id[idx-1]).get_settings()
                    for key in saved_keywords:
                        if current_settings[key] != previous_settings[key]:
                            settings[key] = current_settings[key]
                    layer_height = round(sorted_height[idx]-sorted_height[idx-1], number_of_decimals)
                settings['amplitude'] = sorted_amplitude[idx]
                settings['exposure_time (ms)'] = sorted_exposure[idx]
                settings['layer_thickness (um)'] = layer_height
                rep_delay_ms = current_settings['repositioning_delay (ms)']
                up_delay_ms = abs(current_settings['repositioning_offset (mm)']) / current_settings['feed_rate (mm/min)'] * 60 * 1000
                down_delay_ms = abs(current_settings['repositioning_offset (mm)'] - layer_height) / current_settings['feed_rate (mm/min)'] * 60 * 1000
                settings['layer_etc'] = (layer_height != 0.0) * (up_delay_ms + down_delay_ms) + sorted_exposure[idx] + rep_delay_ms
                group_etc_ms += settings["layer_etc"]
                sorted_settings.append(settings)
            if save_relative_paths:
                sorted_layers = [relative_path_dir.relativeFilePath(l) for l in sorted_layers]
            group_json["layers"] = sorted_layers
            group_json["settings"] = sorted_settings
            group_json["group_etc_ms"] = group_etc_ms
            json_data["groups"].append(group_json)
        if file.open(QIODevice.WriteOnly | QIODevice.Text):
            file.write(QJsonDocument(json_data).toJson())
            file.close()
            print("save file %s" % filename)


class SuperJobGroup:

    def __init__(self):
        self.__subgroups_list = []
        self.__subgroups_id = []
        self.add_subgroup()

    def size(self):
        return len(self.__subgroups_list)

    def get_group_height(self):
        height = 0.0
        for subgroup in self.__subgroups_list:
            height = max(height, subgroup.get_subgroup_height())
        return height

    def get_subgroup(self, idx):
        return self.__subgroups_list[idx]

    def get_subgroup_id(self, idx):
        return self.__subgroups_id[idx]

    def add_subgroup(self):
        self.__subgroups_id.append("Subgroup %i" % len(self.__subgroups_list))
        self.__subgroups_list.append(SuperJobSubGroup())

    def remove_subgroup(self, idx):
        self.__subgroups_list.pop(idx)
        self.__subgroups_id = ["Subgroup %i" % idx for idx,_ in enumerate(self.__subgroups_list)]

    def sort_subgroups_layers(self):
        sorted_layers = []
        sorted_heights = []
        sorted_amplitudes = []
        sorted_exposures = []
        sorted_subgroups = []
        for subg_id, subg in enumerate(self.__subgroups_list):
            thickness = subg.get_settings()["layer_thickness (um)"]
            fixed_layer = subg.get_settings()["fixed_layer"]
            incremental_thickness = subg.get_settings()["incremental_thickness"]
            incremental_amplitude = subg.get_settings()["incremental_amplitude"]
            incremental_exposure = subg.get_settings()["incremental_exposure"]
            burn_layers = subg.get_settings()['burn_layers']
            burn_exposure = subg.get_settings()['burn_exposure_time (ms)']
            burn_amplitude = subg.get_settings()['burn_amplitude']

            if not fixed_layer and not incremental_thickness:
                sorted_heights.extend(np.linspace(thickness, subg.size()*thickness, subg.size()).tolist())
            elif fixed_layer:
                sorted_heights.extend(np.linspace(thickness, burn_layers*thickness, burn_layers).tolist())
                sorted_heights.extend([thickness + burn_layers*thickness] * max(0, subg.size()-burn_layers))
            elif incremental_thickness:
                start = subg.get_settings()["starting_incremental_thickness (um)"]
                step = subg.get_settings()["incremental_step_thickness (um)"]
                sorted_heights.extend(np.linspace(thickness, burn_layers*thickness, burn_layers).tolist())
                sorted_heights.extend([burn_layers*thickness + start * (idx+1) + step*(idx+1)*idx/2 for idx in range(max(0,subg.size()-burn_layers))])

            if not incremental_amplitude:
                amplitudes = [burn_amplitude] * burn_layers + [subg.get_settings()["amplitude"]] * max(0, subg.size()-burn_layers)
                sorted_amplitudes.extend(amplitudes)
            else:
                start = subg.get_settings()["starting_incremental_amplitude"]
                step = subg.get_settings()["incremental_step_amplitude"]
                sorted_amplitudes.extend([burn_amplitude] * burn_layers)
                sorted_amplitudes.extend([start + step*idx for idx in range(max(0, subg.size()-burn_layers))])
            if not incremental_exposure:
                exposure = [burn_exposure] * burn_layers + [subg.get_settings()["exposure_time (ms)"]] * max(0, subg.size() - burn_layers)
                sorted_exposures.extend(exposure)
            else:
                start = subg.get_settings()["starting_incremental_exposure (ms)"]
                step = subg.get_settings()["incremental_step_exposure (ms)"]
                sorted_exposures.extend([burn_exposure] * burn_layers)
                sorted_exposures.extend([start + step*idx for idx in range(max(0, subg.size() - burn_layers))])

            sorted_layers.extend(subg.get_layers())
            sorted_subgroups.extend([subg_id] * subg.size())
        sorted_idxs = np.argsort(sorted_heights, kind='stable')
        sorted_layers = [sorted_layers[l] for l in sorted_idxs]
        sorted_heights = [sorted_heights[l] for l in sorted_idxs]
        sorted_amplitudes = [sorted_amplitudes[l] for l in sorted_idxs]
        sorted_exposures = [sorted_exposures[l] for l in sorted_idxs]
        sorted_subgroups = [sorted_subgroups[l] for l in sorted_idxs]
        return sorted_layers, sorted_heights, sorted_amplitudes, sorted_exposures, sorted_subgroups


class SuperJobSubGroup:

    def __init__(self, ):
        self.__layers_list = []
        self.__settings = default_parameters.copy()

    def size(self):
        return len(self.__layers_list)

    def get_subgroup_height(self):
        fixed_layer = self.__settings["fixed_layer"]
        incremental_thickness = self.__settings["incremental_thickness"]
        layer_height = self.__settings["layer_thickness (um)"]
        burn_layers = self.__settings['burn_layers']
        feature_layers = len(self.__layers_list) - burn_layers
        if not fixed_layer and not incremental_thickness:
            return layer_height * len(self.__layers_list)
        elif fixed_layer:
            total_height = min(burn_layers, len(self.__layers_list)) * layer_height + layer_height * (feature_layers > 0)
            return total_height
        elif incremental_thickness:
            start = self.__settings["starting_incremental_thickness (um)"]
            step = self.__settings["incremental_step_thickness (um)"]
            total_height = min(burn_layers, len(self.__layers_list)) * layer_height
            if feature_layers > 0:
                total_height += start * feature_layers + step * feature_layers * (feature_layers - 1) / 2
            return total_height

    def get_settings(self):
        return self.__settings

    def get_layers(self):
        return self.__layers_list

    def add_layers(self, images_paths):
        self.__layers_list.extend(images_paths)

    def remove_layer(self, idx):
        self.__layers_list.pop(idx)

    def remove_layers(self, idx_list):
        idx_set = set(idx_list)
        self.__layers_list = [i for j, i in enumerate(self.__layers_list) if j not in idx_set]


default_parameters = {
    'layer_thickness (um)': 10.0,  # um
    'exposure_time (ms)': 1000,  # ms
    'amplitude': 100,
    'burn_layers': 0,
    'burn_exposure_time (ms)': 5000,  # ms
    'burn_amplitude': 300,
    'incremental_thickness': False,
    'incremental_exposure': False,
    'incremental_amplitude': False,
    'starting_incremental_thickness (um)': 1.0,  # um
    'incremental_step_thickness (um)': 1.0,  # um
    'starting_incremental_exposure (ms)': 1000,  # ms
    'incremental_step_exposure (ms)': 100,  # ms
    'starting_incremental_amplitude': 10,
    'incremental_step_amplitude': 10,
    'fixed_layer': False,
    'grayscale_correction': False,
    'grayscale_alpha': 0.0,
    'grayscale_beta': 0.0,
    'grayscale_gamma': 0.0,
    'horizontal_mirror': True,
    'vertical_mirror': False,
    'repositioning_delay (ms)': 500,  # ms
    'feed_rate (mm/min)': 300,  # mm/min
    'repositioning_offset (mm)': 5
}
saved_keywords = [
    'grayscale_correction',
    'grayscale_alpha',
    'grayscale_beta',
    'grayscale_gamma',
    'horizontal_mirror',
    'vertical_mirror',
    'repositioning_delay (ms)',
    'feed_rate (mm/min)',
    'repositioning_offset (mm)'
]

