import __env__

notepaper = {
    "fontSize": "13px",
    "fontFamily": "monospace",
    "color": config.themes.notepaper_fg,
    "backgroundColor": config.themes.notepaper_bg + (config.themes.notepaper_def_transparency if config.notes.paper_default_transparency else ""),
    "border": "1px solid " + config.themes.notepaper_border
}
