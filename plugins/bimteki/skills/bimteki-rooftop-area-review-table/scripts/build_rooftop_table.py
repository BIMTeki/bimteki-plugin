#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屋突面積檢討表 儲存格 payload 產生器（2 欄、固定 4 列）。

列：標題（樓層名稱[＋棟別]＋面積檢討）／屋突面積／允建屋突面積／檢討。
值欄全部用「樓層屬性（story-relative）」自動文字綁定，數值由 BIMTeki 依樓層計算，不寫死數字。
三個值的自動文字都是 story 相依（targetType=story、needGUID=true）：
  屋突面積     ← storyArea「算式：室內樓地板面積」（或「算式：屋突」）
  允建屋突面積  ← roofArea「算式：屋突允建面積」（通用、依樓層解析）
  檢討         ← roofArea「算式：屋突檢討式」（通用、依樓層解析）
因為三者都 story 相依，**單一 story-open 樣板**即可涵蓋單棟／多棟分棟／各棟總計所有情形。

綁法（由 config.story_open 決定）：
  story_open=True（建議，單一樣板）：
      儲存格不帶 storyGuid；建表後用 MCP 設樣板層級 table_type="story" + story_guid=""（樓層打開）。
      放置時使用者自選樓層，全部 story 相依自動文字（含允建/檢討）即依放置樓層與其棟別解析。
  story_open=False（逐棟逐屋突層各一張）：
      每格帶該屋突層 storyGuid；同一組 token 換 storyGuid 即得該層值。

用法：python build_rooftop_table.py config.json   （或 < config.json）
輸出（stdout, JSON）：{ cols, rows, room_guid, cells, merges, column_widths }

config 欄位：
  story_open        : bool，樣板層級樓層是否打開（預設 False）。
  story_guid        : story_open=False 時各格綁的屋突層 story guid（必填）。
  block_prefix      : bool，標題是否加「棟別」自動文字（多棟分棟檢討設 True）。
  area_token_display: 屋突面積用 display（預設「算式：室內樓地板面積」）。
  allow_token       : 允建屋突面積 token；預設用「算式：屋突允建面積」；給空字串則該格留空。
  review_token      : 屋突檢討式 token；預設用「算式：屋突檢討式」；給空字串則該格留空。
  tokens            : 覆寫預設 display→token。
  column_widths / value_col_width : 欄寬（預設 [220, 616]）。
  room_guid         : 預設常數。
"""
import json, sys

DEFAULT_TOKENS = {
    "樓層名稱": "${TJL$F25387D152474}",
    "棟別": "${TJL$F5076BDCC0064}",
    "算式：室內樓地板面積": "${TJL$F8FC213D2D115}",
    "算式：屋突允建面積": "${TJL$F622E2DB87002}",   # story 相依（roofArea）
    "算式：屋突檢討式": "${TJL$FCE11626AE7D2}",     # story 相依（roofArea）
    # 「算式：屋突」為 story-relative 的屋突面積替代，token 依專案 catalog 取得後放進 tokens 覆寫。
}
ROOM_GUID_DEFAULT = "4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3"


def tok(tokens, display):
    if display not in tokens:
        raise SystemExit("缺 token：%s（請由 get_project_autotext_catalog 取得放進 config.tokens）" % display)
    return tokens[display]


def build(cfg):
    tokens = dict(DEFAULT_TOKENS)
    tokens.update(cfg.get("tokens") or {})
    room = cfg.get("room_guid", ROOM_GUID_DEFAULT)
    story_open = cfg.get("story_open", False)
    st = None if story_open else cfg["story_guid"]
    cells, merges = [], []

    def put(row, col, **kw):
        c = {"row": row, "col": col}
        c.update(kw)
        cells.append(c)

    def bind():
        # story_open：不帶 story（由樣板層級樓層屬性決定）；否則帶該屋突層 story。
        return {} if story_open else {"storyGuid": st, "roomGuid": room}

    def lab(row, col, text):
        put(row, col, text=text, alignment=1, charwidth=0, newline=0, textsize=2, textbold=False, **bind())

    def empty(row, col):
        put(row, col, text="", alignment=1, charwidth=0, newline=0, textsize=2, textbold=False)

    def val(row, col, token):
        put(row, col, segments=[{"type": "autotext", "token": token}],
            alignment=1, charwidth=0, newline=3, textsize=2, textbold=False, **bind())

    # row0 標題：[棟別]＋樓層名稱＋面積檢討，跨兩欄
    title_segs = []
    if cfg.get("block_prefix"):
        title_segs.append({"type": "autotext", "token": tok(tokens, "棟別")})
    title_segs.append({"type": "autotext", "token": tok(tokens, "樓層名稱")})
    title_segs.append({"type": "text", "value": "面積檢討"})
    put(0, 0, segments=title_segs, alignment=1, charwidth=0, newline=0, textsize=1, textbold=False, **bind())
    put(0, 1, text="", alignment=1, charwidth=0, newline=0, textsize=1, textbold=False)
    merges.append({"row": 0, "col": 0, "colspan": 2, "rowspan": 1})

    # row1 屋突面積＝室內面積（可用 area_token_display 覆寫）
    lab(1, 0, "屋突面積：")
    val(1, 1, tok(tokens, cfg.get("area_token_display", "算式：室內樓地板面積")))

    # row2 允建屋突面積（預設綁 story 相依「算式：屋突允建面積」；config 給空字串則留空）
    lab(2, 0, "允建屋突面積：")
    allow = cfg.get("allow_token", tok(tokens, "算式：屋突允建面積"))
    val(2, 1, allow) if allow else empty(2, 1)

    # row3 檢討（預設綁 story 相依「算式：屋突檢討式」；config 給空字串則留空）
    lab(3, 0, "檢討：")
    review = cfg.get("review_token", tok(tokens, "算式：屋突檢討式"))
    val(3, 1, review) if review else empty(3, 1)

    cw = cfg.get("column_widths") or [220, cfg.get("value_col_width", 616)]
    return {"cols": 2, "rows": 4, "room_guid": room,
            "cells": cells, "merges": merges, "column_widths": cw}


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else json.load(sys.stdin)
    sys.stdout.write(json.dumps(build(cfg), ensure_ascii=False))


if __name__ == "__main__":
    main()
