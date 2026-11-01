from payroll_africa.setup import (
	_create_cameroon_salary_components,
	_create_chad_salary_components,
	_create_congo_salary_components,
	_create_eg_salary_components,
)


def execute():
	"""Create missing statutory salary components for Cameroon, Chad, Congo, and Equatorial Guinea.

	These components were not created by prior setup runs (the country setup functions
	lacked component creation calls).  The helpers are idempotent via _upsert_salary_component.
	"""
	_create_cameroon_salary_components()
	_create_chad_salary_components()
	_create_congo_salary_components()
	_create_eg_salary_components()
