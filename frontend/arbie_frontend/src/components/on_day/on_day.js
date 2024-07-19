import React , {useState, useEffect, useContext} from 'react';
import MeetEntry from './meet_entry/meet_entry';
import TimeContext from '../counter_time_context/current_time_context';
import SvgManager from '../svg_manager/SvgManager';
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
          <SvgManager color={"var(--secondary-background-color)"} path={"M14.2893 5.70708C13.8988 5.31655 13.2657 5.31655 12.8751 5.70708L7.98768 10.5993C7.20729 11.3805 7.2076 12.6463 7.98837 13.427L12.8787 18.3174C13.2693 18.7079 13.9024 18.7079 14.293 18.3174C14.6835 17.9269 14.6835 17.2937 14.293 16.9032L10.1073 12.7175C9.71678 12.327 9.71678 11.6939 10.1073 11.3033L14.2893 7.12129C14.6799 6.73077 14.6799 6.0976 14.2893 5.70708Z"}/>
        </div>

        <div class='center'>
          <div class='date_wpr'>
            <p class='date_txt'>{selected_date.toLocaleString().split(",")[0]}</p>
          </div>
        </div>

        <div onClick={() => change_date(86400000)} class='btn_container'>
          <SvgManager color={"var(--secondary-background-color)"} path={"M9.71069 18.2929C10.1012 18.6834 10.7344 18.6834 11.1249 18.2929L16.0123 13.4006C16.7927 12.6195 16.7924 11.3537 16.0117 10.5729L11.1213 5.68254C10.7308 5.29202 10.0976 5.29202 9.70708 5.68254C9.31655 6.07307 9.31655 6.70623 9.70708 7.09676L13.8927 11.2824C14.2833 11.6729 14.2833 12.3061 13.8927 12.6966L9.71069 16.8787C9.32016 17.2692 9.32016 17.9023 9.71069 18.2929Z"}/>
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
