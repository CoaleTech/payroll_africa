"""Patch: correct Algeria CNAS employer contribution rate from 26% to 25%.

Source: CLEISS (Centre des Liaisons Européennes et Internationales de Sécurité
Sociale) Algeria contribution schedule, effective 1 January 2024.
Breakdown (employer only): social insurance 11.5% + work injury 1.25% +
retirement 11% + early-retirement 0.25% + unemployment 1% = 25%.
The FNPOS 0.5% is a separate "Fonds des Oeuvres Sociales" column and is NOT
an employer contribution; excluding it gives the correct employer total of 25%.

The previous patch (fix_algeria_cnas_employer_rate) corrected 25.5 → 26, which
was still wrong. This patch corrects 26 → 25.

Only updates when the value is still at the stale 26 default.
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Algeria Payroll Settings"):
        return

    current = frappe.db.get_single_value("Algeria Payroll Settings", "cnas_employer_rate")
    if current is None or float(current or 0) == 26:
        frappe.db.set_single_value("Algeria Payroll Settings", "cnas_employer_rate", 25)
        frappe.db.commit()
