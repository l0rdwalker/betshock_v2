import React , {useState, useEffect, useContext} from 'react';
import MeetEntry from './meet_entry/meet_entry';
import TimeContext from '../counter_time_context/current_time_context';

import SvgManager from '../svg_manager/SvgManager';
import LeftArrow from '../../static_resources/left_arrow.svg'
import RightArrow from '../../static_resources/right_arrow.svg'

import './on_day.css'

const OnDay = () => {
  const [races, set_races] = useState([]);
  const [selected_date, set_selected_date] = useState(useContext(TimeContext));

  useEffect(() => {
    fetch(`http://127.0.0.1:8080/get_day_races/${selected_date.getTime()}`)
    .then(response => response.json())
    .then(res => set_races(res))
    .catch(error => console.error(error))
  },[selected_date]);

  const change_date = (modifier) => {
    const new_date = new Date(selected_date.getTime() + modifier);
    set_races([]);
    set_selected_date(new_date);
  };

  return (
    <div class='on_day_container'>
      <div class='on_day_header'>
        
        <div onClick={() => change_date(-86400000)} class='btn_container'>
          <SvgManager height={25} width={25} color={"var(--secondary-background-color)"} src={LeftArrow}/>
        </div>

        <div class='center'>
          <div class='date_wpr'>
            <p class='date_txt'>{selected_date.toLocaleString().split(",")[0]}</p>
          </div>
        </div>

        <div onClick={() => change_date(86400000)} class='btn_container'>
          <SvgManager height={25} width={25} color={"var(--secondary-background-color)"} src={RightArrow}/>
        </div>

      </div>

      <div class='on_day_body'>
        {races.length == 0 ? <p class='no_data_div'>no data for selected date</p> : races.map((race, index) => (
            <MeetEntry key={race[2]} race_data={race}/>
        ))}
      </div>

    </div>
  );
}

export default OnDay;
