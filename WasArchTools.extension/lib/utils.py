# -*- coding: utf-8 -*-
"""Utility functions for WasArchTools extension."""

from pyrevit import forms
from pyrevit import script
from Autodesk.Revit.DB import Transaction


def start_transaction(doc, name):
    """Start a new transaction.

    Args:
        doc: The current Revit document
        name: Name of the transaction

    Returns:
        Transaction: The created transaction
    """
    t = Transaction(doc, name)
    t.Start()
    return t


def handle_error(error, title="Error"):
    """Handle and log an error.

    Args:
        error: The error to handle
        title: Title for the error dialog
    """
    logger = script.get_logger()
    logger.error(str(error))
    forms.alert(
        msg=str(error),
        title=title,
        sub_msg="Check log for details"
    )


def get_selected_elements(uidoc):
    """Get currently selected elements.

    Args:
        uidoc: The current Revit UI document

    Returns:
        list: Selected elements
    """
    return [
        uidoc.Document.GetElement(id)
        for id in uidoc.Selection.GetElementIds()
    ] 