"""
.. module:: resnet_internal.computers.constants
   :synopsis: ResNet Internal Computer Index Constants.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

CORE = "Core"
HOUSING_ADMINISTRATION = "Housing Administration"
HOUSING_AND_BUSINESS_SERVICES = "Housing and Business Services"
RESIDENTIAL_LIFE_AND_EDUCATION = "Residential Life and Education"

DEPARTMENTS = [
    CORE,
    HOUSING_ADMINISTRATION,
    HOUSING_AND_BUSINESS_SERVICES,
    RESIDENTIAL_LIFE_AND_EDUCATION
]

CORE_SUB_DEPARTMENTS = [
    "Core"
]

HOUSING_ADMINISTRATION_SUB_DEPARTMENTS = [
    "Housing Administration"
]

HOUSING_AND_BUSINESS_SERVICES_SUB_DEPARTMENTS = [
    "Conference and Event Planning",
    "Custodial Services",
    "Housing Services"
]

RESIDENTIAL_LIFE_AND_EDUCATION_SUB_DEPARTMENTS = [
    "Residential Life and Education",
    "Residential Networking Services"
]

ALL_SUB_DEPARTMENTS = CORE_SUB_DEPARTMENTS + HOUSING_ADMINISTRATION_SUB_DEPARTMENTS + HOUSING_AND_BUSINESS_SERVICES_SUB_DEPARTMENTS + RESIDENTIAL_LIFE_AND_EDUCATION_SUB_DEPARTMENTS
