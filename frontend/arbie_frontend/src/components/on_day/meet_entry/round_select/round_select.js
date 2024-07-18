import React , {useState, useEffect} from 'react';

import './round_select.css'

import CounterTime from '../../../counter_time/counter_time';

const RoundSelect = (props) => {
  const [round, set_round] = useState(1);

  useEffect(() => {
    set_round(props.round);
  },[props.round])

  return (
    <div class='round_select_container'>
      <div class='padded_content'>

        
        <div class='vertical_divide'>
          <div class='title_wpr'>
            <p>R{round}</p>
          </div>
        </div>

        <div class='vertical_divide'>
          <CounterTime/>
        </div>


      </div>
    </div>
  );
}

export default RoundSelect;
