# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 09:53:42 2022

@author: hagem
"""

"""
Vorgehen beim Schreiben eines stochastischen Optimierungproblems:
    1. Deterministisches Modell und seine Komponenten aufstellen
    2. Base-Case DAten für das deterministische Modell entwickeln
    3. Teste, Verifiziere und validiere das deterministische Modell
    4. Modelliere sdtochastischen Prozess
    5. Überlege einen Weg um Szenarien zu generieren
    6. Kreiere die nötigen Daten um die Unsicherheit zu beschreiben
    7. Mit PySP lösen
    
    Dabei gilt:
        -Abstrakte Modell für deterministisches Problem in 'ReferenceModel.py' speichern
        -Stochastische Struktur in 'ScenarioStructure.dat'
        -Szenario-Daten spezifizieren
"""

from pyomo.core import *

#
#Parameter des Modells, bisher deterministisch betrachtet
#

model = AbstractModel()

model.CROPS = Set()

model.TOTAL_ACREAGE = Param(within=PositiveReals)

model.PriceQuota = Param(model.CROPS, within=PositiveReals)

model.SubQuotaSellingPrice = Param(model.CROPS, within=PositiveReals)

def super_quota_selling_price_validate (model, value, i):
    return model.SubQuotaSellingPrice[i] >= model.SuperQuotaSellingPrice[i]

model.SuperQuotaSellingPrice = Param(model.CROPS, validate=super_quota_selling_price_validate)

model.CattleFeedRequirement = Param(model.CROPS, within=NonNegativeReals)

model.PurchasePrice = Param(model.CROPS, within=PositiveReals)

model.PlantingCostPerAcre = Param(model.CROPS, within=PositiveReals)

model.Yield = Param(model.CROPS, within=NonNegativeReals)

#
# Variablen:
#    -DevotedAcreage -> Wie viel Fläche weise ich welchem Gut zu
#    -QuantitySubQuotaSold -> Wie viel verkaufe ich von jedem Gut bis zum Deckel
#    -QuantitySuperQuotaSold -> Wie viel verkaufe ich, obwohl ich die Quote überreize? 
#    -QuantityPurchased -> Wie viel muss ich nachkaufen, um meinen eigenen Bedarf zu decken?
#

model.DevotedAcreage = Var(model.CROPS, bounds=(0.0, model.TOTAL_ACREAGE))

model.QuantitySubQuotaSold = Var(model.CROPS, bounds=(0.0, None))

model.QuantitySuperQuotaSold = Var(model.CROPS, bounds=(0.0, None))

model.QuantityPurchased = Var(model.CROPS, bounds=(0.0, None))

#
# Constraints:
#   -ContrainTotalAcreage -> Es kann nicht mehr bebaut werden als Land vorhanden ist
#   -EnforceCattleFeedRequirement -> Nach Ertrag, Kauf und Verkauf müssen die Tiere ausreichend Futter haben
#   -LimitAmountSold -> Man kann nur so viel verkaufen wie auch erzeugt wurde
#   -EnforceQuotas -> Einhalten der Quoten für die Preisbestimmung
#   -

def ConstrainTotalAcreage_rule(model):
    return summation(model.DevotedAcreage) <= model.TOTAL_ACREAGE
model.ConstrainTotalAcreage = Constraint(rule=ConstrainTotalAcreage_rule)

def EnforceCattleFeedRequirement_rule(model, i):
    return model.CattleFeedRequirement[i] <= (model.Yield[i] * model.DevotedAcreage[i]) + model.QuantityPurchased[i] - model.QuantitySubQuotaSold[i] - model.QuantitySuperQuotaSold[i]
model.EnforceCattleFeedRequirement = Constraint(model.CROPS, rule=EnforceCattleFeedRequirement_rule)

def LimitAmountSold_rule(model, i):
    return model.QuantitySubQuotaSold[i] + model.QuantitySuperQuotaSold[i] - (model.Yield[i] * model.DevotedAcreage[i]) <= 0.0
model.LimitAmountSold = Constraint(model.CROPS, rule=LimitAmountSold_rule)

def EnforceQuotas_rule(model, i):
    return (0.0, model.QuantitySubQuotaSold[i], model.PriceQuota[i])
model.EnforceQuotas = Constraint(model.CROPS, rule=EnforceQuotas_rule)

#
# Stage-specific cost computations
#   -Erste Stufe: Wie viel hat es gekostet eine bestimmte Fläche zu bepflanzen 
#   -Zweite Stufe: Summiere Kosten durch Kaufmenge und Erlöse durch Sub-/Superquotaverkäufe
#
# => Wir minimieren in total_cost die Gesamtkosten aus Erst- und Zweitstufe

def ComputeFirstStageCost_rule(model):
    return summation(model.PlantingCostPerAcre, model.DevotedAcreage)

model.FirstStageCost = Expression(rule=ComputeFirstStageCost_rule)

def ComputeSecondStageCost_rule(model):
    expr = summation(model.PurchasePrice, model.QuantityPurchased)
    expr -= summation(model.SubQuotaSellingPrice, model.QuantitySubQuotaSold)
    expr -= summation(model.SuperQuotaSellingPrice, model.QuantitySuperQuotaSold)
    return expr

model.SecondStageCost = Expression(rule=ComputeSecondStageCost_rule)

def total_cost_rule(model):
    return model.FirstStageCost + model.SecondStageCost
model.Total_Cost_Objective = Objective(rule=total_cost_rule, sense=minimize)