import React , {useState, useEffect} from 'react';

import './counter_time.css'

const CounterTime = (props) => {
  const [time,setTime] = useState(-1)

  useEffect(() => {
    let current_time = new Date()
    let start_time = new Date(props.start_time);
    let time_left = start_time - current_time
  },[props.start_time])

  return (
    <div class='counter_time_container'>
      <p>{time}</p>
    </div>
  );
}

export default CounterTime; 