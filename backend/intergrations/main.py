from taskSequencer import taskSchedular
from engine.multiTask import multitask
from datetime import datetime, timedelta

task_schedular = taskSchedular(1)

complete_race_updater = task_schedular.searchFunctions({'type':'arbUpdate'})
date_programable_horse_functions = task_schedular.searchFunctions({'sport':'horses','flex_dates' : True})
non_date_programable_horse_functions = task_schedular.searchFunctions({'sport':'horses','flex_dates' : False})

all_horse_platforms = []
all_horse_platforms.extend(date_programable_horse_functions)
all_horse_platforms.extend(non_date_programable_horse_functions)

all_horses_operation_cur_day = multitask()
for function in all_horse_platforms:
    all_horses_operation_cur_day.add_function(function,timedelta(days=0))
all_horses_operation_cur_day.add_post_task(complete_race_updater[0])
    
limited_horses_operation_nxt_day = multitask()
for function in date_programable_horse_functions:
    limited_horses_operation_nxt_day.add_function(function,timedelta(days=1))
limited_horses_operation_nxt_day.add_post_task(complete_race_updater[0])

task_schedular.enqueue(limited_horses_operation_nxt_day)
task_schedular.enqueue(all_horses_operation_cur_day)

while True:
    task_schedular.step()

print('done')