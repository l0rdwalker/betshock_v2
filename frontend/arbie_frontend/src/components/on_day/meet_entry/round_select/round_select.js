import React , {useState, useEffect} from 'react';

import './round_select.css'

import CounterTime from '../../../counter_time/counter_time';

const RoundSelect = () => {

  return (
    <div class='round_select_container'>
      <div class='padded_content'>

        
        <div class='round'>
          <p>R2</p>
        </div>


        <CounterTime/>


      </div>
    </div>
  );
}

export default RoundSelect;
