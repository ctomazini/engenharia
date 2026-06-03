"""Papéis de saída calculada (roll-up na obra)."""

# area → Project Item.total_area: deferido (enum reservado para extensão futura)
OUTPUT_ROLE_OPTIONS = "\nvolume\nvalue\npreview\narea"

TITLE_OUTPUT_ROLES = frozenset({"volume"})
VALUE_OUTPUT_ROLES = frozenset({"value"})
PREVIEW_OUTPUT_ROLES = frozenset({"preview"})
# AREA_OUTPUT_ROLES = frozenset({"area"})  # deferido: total_area no Project Item

VALID_OUTPUT_ROLES = frozenset({"", "volume", "value", "preview", "area"})
