import __env__

from .. import config

size_open_positions = config.statistics.graph_sizes.open_positions
size_all_positions = config.statistics.graph_sizes.all_positions
size_slider_kwargs_performance = dict(
    min=500, max=6000, step=500, value=config.statistics.performance.GraphSize,
)
size_slider_kwargs_pop = dict(
    min=500, max=6000, step=500, value=config.statistics.graph_sizes.pop,
)

color_bg_plot = config.themes.figure_plot
color_bg_paper = config.themes.figure_paper
color_fg_plot = config.themes.figure_font
color_grid_y = config.themes.figure_grid
color_spike_y = config.themes.figure_spike
spike_thickness_y = 1

color_grid_x = color_grid_y
color_spike_x = color_spike_y
spike_thickness_x = spike_thickness_y


