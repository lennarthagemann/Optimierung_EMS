"""
Setze rho so, das der Strafterm in Korrespondenz zu der Zielfunktion steht.
(Hoffentlich wird so die Konvergenzgeschwindigkeit etwas höher.)
"""

def ph_rhosetter_callback(ph, scenario_tree, scenario):

   root_node = scenario_tree.findRootNode()

   si = scenario._instance

   sm = si._ScenarioTreeSymbolMap
   
   MyRhoFactor = 1.0

   for t in si.steps:
      
      ph.setRhoOneScenario(root_node,
                           scenario,
                           sm.getSymbol(si.p_kauf[t]),
                           si.price[t] * MyRhoFactor)
      ph.setRhoOneScenario(root_node,
                           scenario,
                           sm.getSymbol(si.p_einsp[t]),
                           si.price[t] * MyRhoFactor)