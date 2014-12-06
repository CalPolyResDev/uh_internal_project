"""
.. module:: resnet_internal.apps.computers.constants
   :synopsis: ResNet Internal Computer Index Constants.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

CORE = "Core"
HOUSING_ADMINISTRATION = "Housing Administration"
HOUSING_SERVICES = "Housing Services"
RESIDENTIAL_LIFE_AND_EDUCATION = "Residential Life and Education"

DEPARTMENTS = [
    CORE,
    HOUSING_ADMINISTRATION,
    HOUSING_SERVICES,
    RESIDENTIAL_LIFE_AND_EDUCATION
]

CORE_SUB_DEPARTMENTS = [
    "Core"
]

HOUSING_ADMINISTRATION_SUB_DEPARTMENTS = [
    "Housing Administration",
    "Conference and Event Planning"
]

HOUSING_SERVICES_SUB_DEPARTMENTS = [
    "Housing Services",
]

RESIDENTIAL_LIFE_AND_EDUCATION_SUB_DEPARTMENTS = [
    "Residential Life and Education",
    "Residential Networking Services",
    "Custodial Services"
]

ALL_SUB_DEPARTMENTS = CORE_SUB_DEPARTMENTS + HOUSING_ADMINISTRATION_SUB_DEPARTMENTS + HOUSING_SERVICES_SUB_DEPARTMENTS + RESIDENTIAL_LIFE_AND_EDUCATION_SUB_DEPARTMENTS
