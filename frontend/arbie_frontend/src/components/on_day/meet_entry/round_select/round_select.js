import React , {useState, useEffect} from 'react';

import './round_select.css'

import CounterTime from '../../../counter_time/counter_time';

const RoundSelect = (props) => {
  const [round, set_round] = useState(1);

  useEffect(() => {
    set_round(props.round);
  },[props.round])

  const on_day_trigger = (element) => {
    console.log(element);
  }

  return (
    <div class={'round_select_container'}>
      <div class='padded_content'>

        
        <div class='vertical_divide'>
          <div class='title_wpr'>
            <p>R{round}</p>
          </div>
        </div>

        <div class='vertical_divide'>
          <CounterTime trigger_function={() => on_day_trigger(this)} target_time={new Date(props.race_data['Start_time'])}/>
        </div>

      </div>
    </div>
  );
}

export default RoundSelect;
