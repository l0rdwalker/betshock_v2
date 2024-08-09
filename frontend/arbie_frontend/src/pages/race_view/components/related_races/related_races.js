import React , {useState, useEffect, useContext} from 'react';
import RoundSelect from '../../../../components/on_day/meet_entry/round_select/round_select'

import './related_races.css'

const RelatedRace = (props) => {
  const [other_meet_races, set_other_meet_races] = useState([]);

  useEffect(() => {
    fetch(`http://127.0.0.1:8080/get_related_races/${props.race_id}`)
    .then(data => data.json())
    .then(data => set_other_meet_races(data))
    .catch(err => console.log(err))
  },[props.race_id]);

  useEffect(() => {

    const round_selections = document.getElementsByClassName('other_meet_races');
    console.log(round_selections);
  },[other_meet_races]);

  return (
    <div class='related_races_wpr'>
      {other_meet_races.map((race, index) => (
        <RoundSelect key={race[2]} race_data={race} height={'100%'} round={index+1}/>
      ))}
    </div>
  );
}

export default RelatedRace; 