from taskSequencer import taskSchedular
from engine.betters import betters
from datetime import datetime, timedelta
from engine.get_market_context import get_market_context

task_schedular = taskSchedular(1)
database_obj = task_schedular.get_database_obj()
router_obj = task_schedular.get_router_obj()

complete_race_updater = task_schedular.searchFunctions({'type':'arbUpdate'})
date_programable_horse_functions = task_schedular.searchFunctions({'sport':'horses','flex_dates' : True})
non_date_programable_horse_functions = task_schedular.searchFunctions({'sport':'horses','flex_dates' : False, 'platform':'racenet'})

all_horse_platforms = []
all_horse_platforms.extend(date_programable_horse_functions)
all_horse_platforms.extend(non_date_programable_horse_functions)

all_horses_operation_cur_day = get_market_context(('arbie','horses'),database_obj,router_obj)
for function in all_horse_platforms:
    all_horses_operation_cur_day.add_function(function,timedelta(days=0))
all_horses_operation_cur_day.set_operation_name("GET-TODAY-RACES")
    
limited_horses_operation_nxt_day = get_market_context(('arbie','horses'),database_obj,router_obj)
for function in date_programable_horse_functions:
    limited_horses_operation_nxt_day.add_function(function,timedelta(days=1))
limited_horses_operation_nxt_day.set_operation_name("GET-TOMMOROW-RACES")

task_schedular.enqueue(all_horses_operation_cur_day)
task_schedular.enqueue(limited_horses_operation_nxt_day)

#new_bets = betters(('arbie','horses'),all_horse_platforms,database_obj,router_obj)
#individual_bets = new_bets.getFunctions()
#for better in individual_bets:
#    task_schedular.enqueue_embedded_runtime(better)

while True:
    task_schedular.init()

