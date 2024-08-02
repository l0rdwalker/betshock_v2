from taskSequencer import taskSchedular
from engine.multiTask import multitask
from engine.betters import betters
from datetime import datetime, timedelta

task_schedular = taskSchedular(3)
database_obj = task_schedular.get_database_obj()

complete_race_updater = task_schedular.searchFunctions({'type':'arbUpdate'})
date_programable_horse_functions = task_schedular.searchFunctions({'sport':'horses','flex_dates' : True})
non_date_programable_horse_functions = task_schedular.searchFunctions({'sport':'horses','flex_dates' : False})

all_horse_platforms = []
all_horse_platforms.extend(date_programable_horse_functions)
all_horse_platforms.extend(non_date_programable_horse_functions)

all_horses_operation_cur_day = multitask(('arbie','horses'),database_obj)
for function in all_horse_platforms:
    all_horses_operation_cur_day.add_function(function,timedelta(days=0))
all_horses_operation_cur_day.add_post_task(complete_race_updater[0])
    
limited_horses_operation_nxt_day = multitask(('arbie','horses'),database_obj)
for function in date_programable_horse_functions:
    limited_horses_operation_nxt_day.add_function(function,timedelta(days=1))
limited_horses_operation_nxt_day.add_post_task(complete_race_updater[0])

task_schedular.enqueue(all_horses_operation_cur_day)
task_schedular.enqueue(limited_horses_operation_nxt_day)

new_bets = betters(('arbie','horses'),all_horse_platforms,database_obj)

while True:
    task_schedular.step()

