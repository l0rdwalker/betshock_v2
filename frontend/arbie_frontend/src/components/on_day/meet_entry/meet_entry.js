import React , {useState, useEffect} from 'react';
import './meet_entry.css'

import RoundSelect from './round_select/round_select';
import Australia from './flags/australia';

const MeetEntry = () => {
  const [list_test, set_list_test] = useState([1,1,1,1,1,1,1])

  return (
    <div class='meet_entry_container'>
      <div class='meet_deets'>

        <div class='meet_deets_flex_container'>
          <div class='meet_name'>
            <p>Sunshine</p>
          </div>
          <div class='meet_flag'>
            <Australia />
          </div>
        </div>

      </div>
      <div class='meet_entry'>

        {list_test.map((race, index) => (
          <RoundSelect />
        ))}
        
      </div>
    </div>
  );
}

export default MeetEntry;
