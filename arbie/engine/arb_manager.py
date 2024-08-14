




class arb_manager():
    def __init__(self) -> None:
        pass
    
    def clear_arb(self):
        pass
    
    def set_arb(self):
        pass
    
    def calculate_best_arb(self,race_id):
        pass
        #opened_new_connection = False
        #if self.database.connection_open == False:
        #    self.database.initConnection()
        #    opened_new_connection = True
        #
        #i_p = 0
        #entrant_selections = []
        #entrants = self.database.get_race_entrant_ids(race_id)
        #for entrant in entrants:
        #    if self.database.is_imposed(entrant[0]):
        #        continue
        #    best_odds = 0
        #    best_platform = None
        #    platform_offerings = self.database.get_entrant_platform_offerings(entrant[0])
        #    for platform in platform_offerings:
        #        prices = self.database.get_entrant_odds_by_platform(entrant[0],platform[0])
        #        if not prices == None:
        #            prices = prices[0][0]
        #            if (best_platform == None or prices > best_odds) and not prices == 0:
        #                best_platform = platform[0]
        #                best_odds = prices
        #    if not best_platform == None:
        #        entrant_selections.append({'platform':best_platform,'entrant_id':entrant[0],'horse_name':entrant[1],'odds':best_odds,'i_p':1/best_odds})
        #        i_p += 1/best_odds
        #    else:
        #        i_p += 2
        #if opened_new_connection:
        #    self.database.closeConnection()
        #    
        #if len(entrant_selections) == 0:
        #    return None
        #else:
        #    return {'race_id':race_id,'entrants':entrant_selections,'i_p':i_p}






