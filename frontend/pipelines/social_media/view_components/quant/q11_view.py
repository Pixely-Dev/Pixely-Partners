"""
Compatibility shim: re-export the Q11 display function from the qualitative implementation.

Some view modules live under `qual/` (historical). The dashboard imports
`.view_components.quant.q11_view.display_q11_engagement` in the quantitative
section — provide a small shim so that import paths resolve consistently.
"""
try:
	from ..qual.q11_engagement_view import display_q11_engagement  # type: ignore
except Exception:
	# Fallback: define a stub that informs the user the module is missing
	def display_q11_engagement():
		import streamlit as st
		st.info("Q11 (engagement) no disponible en esta instalación.")
