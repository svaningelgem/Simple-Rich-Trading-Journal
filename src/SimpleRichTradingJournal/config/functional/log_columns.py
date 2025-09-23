import __env__

from .. import config

dataTypeDefinitions = {
    "percentage": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {"function": "params.value == null ? '' :  d3.format('+,.2%')(params.value)"},
        "columnTypes": "rightAligned",
        "appendColumnTypes": True,
    },
    "percentage3": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {"function": "params.value == null ? '' :  d3.format('+,.3%')(params.value)"},
        "columnTypes": "rightAligned",
        "appendColumnTypes": True,
    },
    "prefixed": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {"function": "params.value == null ? '' :  d3.format('+,.2f')(params.value)"},
        "columnTypes": "rightAligned",
        "appendColumnTypes": True,
    },
    "prefixed3": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {"function": "params.value == null ? '' :  d3.format('+,.3f')(params.value)"},
        "columnTypes": "rightAligned",
        "appendColumnTypes": True,
    },
    "grouped": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {"function": "params.value == null ? '' :  d3.format(',.2f')(params.value)"},
        "columnTypes": "rightAligned",
        "appendColumnTypes": True,
    },
    "timedelta": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "columnTypes": "rightAligned",
        "appendColumnTypes": True,
    },
}


_calcCell = {
    "valueFormatter": {"function": "params.value == null ? '' :  d3.format(',.2f')(params.value)"},
    "valueParser": {"function": "calc(params.newValue)"},
}


Name = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.data.cat == ''",
                "style": name_undefined,
            },
            {
                "condition": "params.data.cat == 'd' && params.data.Note",
                "style": name_DEPOSIT_tag | name_has_note,
            },
            {
                "condition": "params.data.cat == 'p' && params.data.Note",
                "style": name_PAYOUT_tag | name_has_note,
            },
            {
                "condition": "params.data.cat == 'i' && params.data.Note",
                "style": name_ITC_tag | name_has_note,
            },
            {
                "condition": "params.data.cat == 'd'",
                "style": name_DEPOSIT_tag,
            },
            {
                "condition": "params.data.cat == 'p'",
                "style": name_PAYOUT_tag,
            },
            {
                "condition": "params.data.cat == 'i'",
                "style": name_ITC_tag,
            },
            {
                "condition": "params.data.cat == 'v' && params.data.Note",
                "style": name_dividend | name_has_note,
            },
            {
                "condition": "params.data.cat == 'v'",
                "style": name_dividend,
            },
            {
                "condition": "params.data.cat == 'to' && params.data.Note && params.data.Dividend",
                "style": name_opentrade | name_has_note | name_has_dividend,
            },
            {
                "condition": "params.data.cat == 'to'  && params.data.Dividend",
                "style": name_opentrade | name_has_dividend,
            },
            {
                "condition": "params.data.cat == 'to' && params.data.Note",
                "style": name_opentrade | name_has_note,
            },
            {
                "condition": "params.data.cat == 'to'",
                "style": name_opentrade,
            },
            {
                "condition": "params.data.Note",
                "style": name_has_note,
            },
            {
                "condition": "params.data.Dividend",
                "style": name_has_dividend,
            },
            {
                "condition": "params.data.cat == 'tf'",
                "style": name_finalized_trade,
            },
        ],
        "defaultStyle": name_undefined,
    },
    "width": config.log().col_widths[0],
    "hide": not config.log().col_widths[0],
}

Name["cellStyle"]["styleConditions"] = [
    {"condition": "params.data.mark == 1 && " + sc["condition"], "style": sc["style"] | name_row_mark}
    for sc in Name["cellStyle"]["styleConditions"]
] + Name["cellStyle"]["styleConditions"]

Symbol = {"cellStyle": {} | symbol, "width": config.log.col_widths[1], "hide": not config.log.col_widths[1]}

ISIN = {"cellStyle": {} | isin, "width": config.log.col_widths[2], "hide": not config.log.col_widths[2]}

Type = {"cellStyle": {} | type, "width": config.log.col_widths[3], "hide": not config.log.col_widths[3]}

Short = {"cellStyle": {} | short, "width": config.log.col_widths[4], "hide": not config.log.col_widths[4]}

Sector = {"cellStyle": {} | sector, "width": config.log.col_widths[5], "hide": not config.log.col_widths[5]}

Category = {"cellStyle": {} | sector, "width": config.log.col_widths[6], "hide": not config.log.col_widths[6]}

Rating = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.value > 8",
                "style": rating | {"backgroundColor": config.themes().rating_scale[8]},
            },
            {
                "condition": "params.value > 7",
                "style": rating | {"backgroundColor": config.themes().rating_scale[7]},
            },
            {
                "condition": "params.value > 6",
                "style": rating | {"backgroundColor": config.themes().rating_scale[6]},
            },
            {
                "condition": "params.value > 5",
                "style": rating | {"backgroundColor": config.themes().rating_scale[5]},
            },
            {
                "condition": "params.value > 4",
                "style": rating | {"backgroundColor": config.themes().rating_scale[4]},
            },
            {
                "condition": "params.value > 3",
                "style": rating | {"backgroundColor": config.themes().rating_scale[3]},
            },
            {
                "condition": "params.value > 2",
                "style": rating | {"backgroundColor": config.themes().rating_scale[2]},
            },
            {
                "condition": "params.value > 1",
                "style": rating | {"backgroundColor": config.themes().rating_scale[1]},
            },
            {
                "condition": "params.value > 0",
                "style": rating | {"backgroundColor": config.themes().rating_scale[0]},
            },
        ],
        "defaultStyle": rating,
    },
    "width": config.log.col_widths[7],
    "hide": not config.log.col_widths[7],
}

N = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.value == 0",
                "style": n_special,
            },
            {
                "condition": "params.value < 0",
                "style": n_ignore,
            },
        ],
        "defaultStyle": n_default,
    },
    "width": config.log.col_widths[8],
    "hide": not config.log.col_widths[8],
}

InvestTime = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.data.cat == 'd' && params.data.InvestAmount == params.data.TakeAmount + params.data.ITC",
                "style": invest_deposit_null,
            },
            {
                "condition": "params.data.cat == ''",
                "style": invest_col | undefined,
            },
            {
                "condition": "params.data.cat == 'd'",
                "style": invest_deposit,
            },
            {
                "condition": "params.data.cat == 'p'",
                "style": invest_payout,
            },
            {
                "condition": "params.data.cat == 'i'",
                "style": invest_itc,
            },
            {
                "condition": "params.data.cat == 'v'",
                "style": invest_dividend,
            },
        ],
        "defaultStyle": invest_col,
    },
    "width": config.log.col_widths[9],
    "hide": not config.log.col_widths[9],
}

InvestAmount = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.data.cat == 'd'",
                "style": invest_amount_deposit,
            },
        ]
        + InvestTime["cellStyle"]["styleConditions"],
        "defaultStyle": invest_col,
    },
    "width": config.log.col_widths[10],
    "hide": not config.log.col_widths[10],
} | _calcCell

InvestCourse = (
    InvestTime
    | {
        "width": config.log.col_widths[11],
        "hide": not config.log.col_widths[11],
    }
    | _calcCell
)

TakeTime = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.data.cat == 'd' && params.data.InvestAmount == params.data.TakeAmount + params.data.ITC",
                "style": take_deposit_null,
            },
            {
                "condition": "params.data.cat == ''",
                "style": take_col | undefined,
            },
            {
                "condition": "params.data.cat == 'd'",
                "style": take_deposit,
            },
            {
                "condition": "params.data.cat == 'p'",
                "style": take_payout,
            },
            {
                "condition": "params.data.cat == 'i'",
                "style": take_itc,
            },
            {
                "condition": "params.data.cat == 'v'",
                "style": take_dividend,
            },
        ],
        "defaultStyle": take_col,
    },
    "width": config.log.col_widths[12],
    "hide": not config.log.col_widths[12],
}

TakeAmount = (
    {
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": "params.data.cat == 'p'",
                    "style": take_amount_payout,
                },
                {
                    "condition": "params.data.cat == 'v'",
                    "style": take_amount_dividend,
                },
            ]
            + TakeTime["cellStyle"]["styleConditions"],
            "defaultStyle": take_col,
        },
        "width": config.log.col_widths[13],
        "hide": not config.log.col_widths[13],
    }
    | __env__.ui_utils.get_cell_renderer_config()['take_amount']
    | _calcCell
)

TakeCourse = (
    TakeTime
    | {
        "width": config.log.col_widths[14],
        "hide": not config.log.col_widths[14],
    }
    | __env__.ui_utils.get_cell_renderer_config()['take_course']
    | _calcCell
)


Itc = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.data.cat == ''",
                "style": itc_col | undefined,
            },
            {
                "condition": "params.data.cat == 'i'",
                "style": itc_itc,
            },
            {
                "condition": "params.data.cat == 'v'",
                "style": itc_dividend,
            },
            {
                "condition": "params.data.cat == 'p'",
                "style": itc_payout,
            },
            {
                "condition": "params.data.cat == 'd'",
                "style": itc_deposit,
            },
        ],
        "defaultStyle": itc_col,
    },
    "width": config.log.col_widths[15],
    "hide": not config.log.col_widths[15],
} | _calcCell

Performance = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.data.cat == 'i'",
                "style": performance_itc,
            },
            {
                "condition": "params.data.cat == 'p'",
                "style": performance_payout,
            },
            {
                "condition": "params.data.cat == 'd' && params.value > 0",
                "style": performance_pos_deposit,
            },
            {
                "condition": "params.data.cat == 'd' && params.value <= 0",
                "style": performance_neg_deposit,
            },
            {
                "condition": "params.data.cat == 'v'",
                "style": result_dividend,
            },
            {
                "condition": "params.value > 0",
                "style": performance_pos,
            },
        ],
        "defaultStyle": performance_neg,
    },
    "width": config.log.col_widths[16],
    "hide": not config.log.col_widths[16],
} | __env__.ui_utils.get_cell_renderer_config()['performance']

Profit = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.data.cat == 'd' && params.value > 0",
                "style": profit_pos_deposit,
            },
            {
                "condition": "params.data.cat == 'd' && params.value <= 0",
                "style": profit_neg_deposit,
            },
            {
                "condition": "params.value > 0",
                "style": profit_pos,
            },
        ],
        "defaultStyle": profit_neg,
    },
    "width": config.log.col_widths[17],
    "hide": not config.log.col_widths[17],
} | __env__.ui_utils.get_cell_renderer_config()['profit']

Dividend = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.data.cat == 'd'",
                "style": result_deposit,
            },
        ],
        "defaultStyle": result,
    },
    "width": config.log.col_widths[18],
    "hide": not config.log.col_widths[18],
}

Note = {
    "cellStyle": {"white-space": "pre"} | note,
    "width": config.log.col_widths[19],
    "hide": not config.log.col_widths[19],
}

HoldTime = {"cellStyle": holdtime, "width": config.log.col_widths[20], "hide": not config.log.col_widths[20]}

ProfitDay = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.value > 0",
                "style": statistic_pos,
            },
        ],
        "defaultStyle": statistic_neg,
    },
    "width": config.log.col_widths[21],
    "hide": not config.log.col_widths[21],
}

PerformanceDay = ProfitDay | {
    "width": config.log.col_widths[22],
    "hide": not config.log.col_widths[22],
}

ProfitYear = {
    "cellStyle": {
        "styleConditions": [
            {
                "condition": "params.value > 0",
                "style": statistic_pos,
            },
        ],
        "defaultStyle": statistic_neg,
    },
    "width": config.log.col_widths[23],
    "hide": not config.log.col_widths[23],
}

PerformanceYear = ProfitDay | {
    "width": config.log.col_widths[24],
    "hide": not config.log.col_widths[24],
}
