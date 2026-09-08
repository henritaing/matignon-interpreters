WINDOW_SECONDS = 120
DROP_TAIL = True  # tail shorter than WINDOW_SECONDS is discarded

THEMES = {
    "international_et_défense",
    "sécurité_intérieure_et_justice",
    "social_et_santé",
    "education_recherche_jeunesse",
    "environnement_territoires_et_infrastructures",
    "institutions_et_fonction_publique",
    "économie_travail_et_finances_publiques",
    "autre",
    "indéterminé",
}

VALID_SHARES = {">75%", "50-75%", "<50%"}

# Windows with fewer than this many transcript characters are labelled
# indéterminé locally, without spending an API call.
MIN_CHARS = 120

MAX_RETRIES = 3
