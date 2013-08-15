"""
.. module:: rmsconnector.constants
   :synopsis: RMS Connector Building and Community Constants

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

SIERRA_MADRE = "Sierra Madre"
YOSEMITE = "Yosemite"
SOUTH_MOUNTAIN = "South Mountain"
NORTH_MOUNTAIN = "North Mountain"
CERRO_VISTA = "Cerro Vista"
POLY_CANYON_VILLAGE = "Poly Canyon Village"

COMMUNITIES = [
    SIERRA_MADRE,
    YOSEMITE,
    SOUTH_MOUNTAIN,
    NORTH_MOUNTAIN,
    CERRO_VISTA,
    POLY_CANYON_VILLAGE
]

SIERRA_MADRE_BUILDINGS = [
    "Tower 0",
    "Tower 1",
    "Tower 2",
    "Tower 3",
    "Tower 4",
    "Tower 5"
]

YOSEMITE_BUILDINGS = SIERRA_MADRE_BUILDINGS + [
    "Tower 6",
    "Tower 7",
    "Tower 8",
    "Tower 9"
]

SOUTH_MOUNTAIN_BUILDINGS = [
    "Fremont",
    "Muir",
    "Santa Lucia",
    "Sequoia",
    "Tenaya",
    "Trinity"
]

NORTH_MOUNTAIN_BUILDINGS = [
    "Diablo",
    "Lassen",
    "Palomar",
    "Shasta",
    "Whitney"
]

CERRO_VISTA_BUILDINGS = [
    "Bishop",
    "Cabrillo",
    "Hollister",
    "Islay",
    "Morro",
    "Romauldo",
    "San Luis"
]

POLY_CANYON_VILLAGE_BUILDINGS = [
    "Aliso",
    "Buena Vista",
    "Corralitos",
    "Dover",
    "Estrella",
    "Foxen",
    "Gypsum",
    "Huasna",
    "Inyo"
]

ALL_BUILDINGS = YOSEMITE_BUILDINGS + SOUTH_MOUNTAIN_BUILDINGS + NORTH_MOUNTAIN_BUILDINGS + CERRO_VISTA_BUILDINGS + POLY_CANYON_VILLAGE_BUILDINGS

CSD_DOMAINS = [
    SIERRA_MADRE,
    YOSEMITE,
    "Fremont",
    "Muir",
    "Santa Lucia / North Mountain",
    "Sequoia",
    "Tenaya",
    "Trinity",
    CERRO_VISTA,
    "Poly Canyon Village 1",
    "Poly Canyon Village 2",
    "Poly Canyon Village 3"
]
