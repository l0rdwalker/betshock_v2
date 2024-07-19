import React , {useState, useEffect, useContext} from 'react';
import TimeContext from '../counter_time_context/current_time_context';

import './counter_time.css'

const CounterTime = (props) => {
  const [time,setTime] = useState(props.target_time);
  const [counter,set_counter] = useState(0);
  const [active_status,set_active_status] = useState(true);
  const [count_status_style_class, set_count_status_style_class] = useState("counter_time_container");
 
  const current_time = useContext(TimeContext);

  useEffect(() => {
    let temp = time;
    setTime(temp);
  }, []);
  
  useEffect(() => {
    if (active_status) {
      let time_difference = (time.getTime() - (1000*60*60*10)) - current_time.getTime();

      let secconds = time_difference / 1000;
      let minutes = secconds / 60;
      let hours = minutes / 60;
      let days = hours / 24;

      let display_time = "now";

      set_count_status_style_class("counter_time_container");

      if (days > 1) {
        display_time = Math.round(days).toString() + "d";
      } else if (hours > 1) {
        display_time = Math.round(hours).toString() + "h";
      } else if (minutes > 1) {
        display_time = Math.round(minutes).toString() + "m";
      } else if (secconds > 1) {
        display_time = Math.round(secconds).toString() + "s";
      } else if (time_difference < 0) {
        display_time = "-";
        set_count_status_style_class("counter_time_container inactive");
        set_active_status(false);
        if (props.trigger_function != null) {
          props.trigger_function();
        }
      }
      set_counter(display_time);
    }
  },[current_time]);
  
  return (
    <div class={count_status_style_class}>
      <p>{counter}</p>
    </div>
  );
}

export default CounterTime; 