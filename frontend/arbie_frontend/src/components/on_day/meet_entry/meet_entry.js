import React , {useState, useEffect} from 'react';

import RoundSelect from './round_select/round_select';
import Australia from './flags/australia';

import './meet_entry.css'

const MeetEntry = (props) => {
  const [track_name,set_track_name] = useState(props.race_data['Track_name']);
  const [list_test, set_list_test] = useState(props.race_data['Races']);

  return (
    <div class='meet_entry_container'>
      <div class='meet_deets'>

        <div class='meet_deets_flex_container'>
          <div class='meet_name'>
            <p>{track_name}</p>
          </div>
          <div class='meet_flag'>
            <Australia />
          </div>
        </div>

      </div>
      <div class='meet_entry'>

        {list_test.map((race, index) => (
          <RoundSelect key={race[2]} race_data={race} round={index+1}/>
        ))}
        
      </div>
    </div>
  );
}

export default MeetEntry;
