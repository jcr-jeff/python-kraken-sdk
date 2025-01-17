#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# Github: https://github.com/btschwertfeger
#

import random
from time import sleep, time

import pytest

from kraken.exceptions import KrakenException

from .helper import is_not_error


def test_get_account_balance(spot_auth_user) -> None:
    assert is_not_error(spot_auth_user.get_account_balance())


def test_get_balances(spot_auth_user):
    assert is_not_error(spot_auth_user.get_balances(currency="USD"))


def test_get_trade_balance(spot_auth_user) -> None:
    assert is_not_error(spot_auth_user.get_trade_balance())
    assert is_not_error(spot_auth_user.get_trade_balance(asset="EUR"))


def test_get_open_orders(spot_auth_user) -> None:
    assert is_not_error(spot_auth_user.get_open_orders(trades=True))
    assert is_not_error(spot_auth_user.get_open_orders(trades=False, userref="1234567"))


def test_get_closed_orders(spot_auth_user) -> None:
    assert is_not_error(spot_auth_user.get_closed_orders())
    assert is_not_error(spot_auth_user.get_closed_orders(trades=True, userref="1234"))
    assert is_not_error(
        spot_auth_user.get_closed_orders(trades=True, start="1668431675.4778206")
    )
    assert is_not_error(
        spot_auth_user.get_closed_orders(
            trades=True, start="1668431675.4778206", end="1668455555.4778206", ofs=2
        )
    )
    assert is_not_error(
        spot_auth_user.get_closed_orders(
            trades=True,
            start="1668431675.4778206",
            end="1668455555.4778206",
            ofs=1,
            closetime="open",
        )
    )


def test_get_trades_info(spot_auth_user) -> None:
    for params, method in zip(
        [
            {"txid": "OXBBSK-EUGDR-TDNIEQ"},
            {"txid": "OXBBSK-EUGDR-TDNIEQ", "trades": True},
            {"txid": "OQQYNL-FXCFA-FBFVD7"},
            {"txid": ["OE3B4A-NSIEQ-5L6HW3", "O23GOI-WZDVD-XWGC3R"]},
        ],
        [
            spot_auth_user.get_trades_info,
            spot_auth_user.get_trades_info,
            spot_auth_user.get_trades_info,
            spot_auth_user.get_trades_info,
        ],
    ):
        try:
            assert is_not_error(method(**params))
        except KrakenException.KrakenInvalidOrderError:
            pass
        finally:
            sleep(2)


def test_get_orders_info(spot_auth_user) -> None:
    for params, method in zip(
        [
            {"txid": "OXBBSK-EUGDR-TDNIEQ"},
            {"txid": "OXBBSK-EUGDR-TDNIEQ", "trades": True},
            {"txid": "OQQYNL-FXCFA-FBFVD7", "consolidate_taker": True},
            {"txid": ["OE3B4A-NSIEQ-5L6HW3", "O23GOI-WZDVD-XWGC3R"]},
        ],
        [
            spot_auth_user.get_orders_info,
            spot_auth_user.get_orders_info,
            spot_auth_user.get_orders_info,
            spot_auth_user.get_orders_info,
        ],
    ):
        try:
            assert is_not_error(method(**params))
        except KrakenException.KrakenInvalidOrderError:
            pass
        finally:
            sleep(2)


def test_get_trades_history(spot_auth_user) -> None:
    sleep(3)

    assert is_not_error(spot_auth_user.get_trades_history(type_="all", trades=True))
    assert is_not_error(
        spot_auth_user.get_trades_history(
            type_="closed position",
            start="1677717104",
            end="1677817104",
            ofs="1",
        )
    )


def test_get_open_positions(spot_auth_user) -> None:
    assert isinstance(spot_auth_user.get_open_positions(), list)
    assert isinstance(
        spot_auth_user.get_open_positions(txid="OQQYNL-FXCFA-FBFVD7"), list
    )
    assert isinstance(
        spot_auth_user.get_open_positions(txid="OQQYNL-FXCFA-FBFVD7", docalcs=True),
        list,
    )


def test_get_ledgers_info(spot_auth_user) -> None:
    assert is_not_error(spot_auth_user.get_ledgers_info())
    assert is_not_error(spot_auth_user.get_ledgers_info(type_="deposit"))
    assert is_not_error(
        spot_auth_user.get_ledgers_info(
            asset="EUR", start="1668431675.4778206", end="1668455555.4778206", ofs=2
        )
    )
    assert is_not_error(
        spot_auth_user.get_ledgers_info(
            asset=["EUR", "USD"],
        )
    )
    assert is_not_error(
        spot_auth_user.get_ledgers_info(
            asset="EUR,USD",
        )
    )


def test_get_ledgers(spot_auth_user) -> None:
    assert is_not_error(spot_auth_user.get_ledgers(id_="LNYQGU-SUR5U-UXTOWM"))
    assert is_not_error(
        spot_auth_user.get_ledgers(
            id_=["LNYQGU-SUR5U-UXTOWM", "LTCMN2-5DZHX-6CPRC4"], trades=True
        )
    )


def test_get_trade_volume(spot_auth_user) -> None:
    assert is_not_error(spot_auth_user.get_trade_volume())
    assert is_not_error(spot_auth_user.get_trade_volume(pair="DOT/EUR", fee_info=False))


def test_request_save_export_report(spot_auth_user) -> None:
    try:
        spot_auth_user.request_export_report(
            report="invalid", description="this is an invalid report type"
        )
    except ValueError:
        # invalid report type
        pass

    for report in ("trades", "ledgers"):
        if report == "trades":
            fields = [
                "ordertxid",
                "time",
                "ordertype",
                "price",
                "cost",
                "fee",
                "vol",
                "margin",
                "misc",
                "ledgers",
            ]
        else:
            fields = [
                "refid",
                "time",
                "type",
                "aclass",
                "asset",
                "amount",
                "fee",
                "balance",
            ]

        export_descr = f"{report}-export-{random.randint(0, 10000)}"
        response = spot_auth_user.request_export_report(
            report=report,
            description=export_descr,
            fields=fields,
            format_="CSV",
            starttm="1662100592",
            endtm=int(1000 * time()),
        )
        assert is_not_error(response) and "id" in response
        sleep(2)

        status = spot_auth_user.get_export_report_status(report=report)
        assert isinstance(status, list)
        sleep(5)

        result = spot_auth_user.retrieve_export(id_=response["id"])
        with open(f"{export_descr}.zip", "wb") as file:
            for chunk in result.iter_content(chunk_size=512):
                if chunk:
                    file.write(chunk)

        status = spot_auth_user.get_export_report_status(report=report)
        assert isinstance(status, list)
        for response in status:
            assert "id" in response
            try:
                assert isinstance(
                    spot_auth_user.delete_export_report(
                        id_=response["id"], type_="delete"
                    ),
                    dict,
                )
            except (
                Exception
            ):  # '200 - {"error":["WDatabase:No change"],"result":{"delete":true}}'
                pass
            sleep(2)


def test_export_report_status(spot_auth_user) -> None:
    # just demonstrating invalid report; real test is in `test_request_save_export_report` function
    try:
        spot_auth_user.get_export_report_status(report="invalid")
    except ValueError:
        pass


def test_create_subaccount(spot_auth_user) -> None:
    # creating subaccounts is only availablle for institutional clients
    with pytest.raises(KrakenException.KrakenPermissionDeniedError):
        spot_auth_user.create_subaccount(email="abc@welt.de", username="tomtucker")
