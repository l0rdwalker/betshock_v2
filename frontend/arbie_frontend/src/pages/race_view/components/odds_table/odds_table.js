import React , {useState, useEffect, useContext} from 'react';
import { json, useLoaderData, useParams } from 'react-router-dom';

import TrackImage from '../../../../static_resources/temp_track.jpg'

import './odds_table.css'
import OddsRow from './odds_row';

const OddsTable = (props) => {
  const [entrants,set_entrants] = useState([]);
  const [platform_list,set_platform_list] = useState([]);
  const [platform_content_idx,set_platform_content_idx] = useState({});

  useEffect(() => {
    let entrants = props.entrants;
    if (entrants != undefined) {

      let platforms = {};
      for (var entrant_idx = 0; entrant_idx < entrants.length; entrant_idx++) {
        for (var price_idx = 0; price_idx < entrants[entrant_idx]['Prices'].length; price_idx++) {
          platforms[entrants[entrant_idx]['Prices'][price_idx]['Platform']] = 0;
        }
      }

      var idx = 0; 
      var index_reference = {}
      var platform_array = [];
      for (const [key, value] of Object.entries(platforms)) {
        platform_array.push(key);
        index_reference[key] = idx;
        idx += 1
      }

      set_platform_content_idx(index_reference);
      set_platform_list(platform_array);
      set_entrants(entrants);
    }
  },[props.entrants]);

  return (
    <div class='table_wpr'>
          
      <div class='table_header'>
        <div class='table_left_side'>
        </div>
        <div class='table_right_side'>
          {platform_list.map((platform_name, index) => (
            <div class='platform_name_container'>
              <p>{platform_name}</p>
            </div>
          ))}
        </div>
      </div>

      <div class='table_body'>
        <div class='table_left_side'>
          {entrants.map((entrant, index) => (
            <div class='entrant_name_container'>
              <p>{entrant['Entrant_name']}</p>
            </div>
          ))}
        </div>
        <div class='table_right_side odds_data'>
          {entrants.map((entrant, index) => (
            <OddsRow entrant_data={entrant['Prices']} index_cache={platform_content_idx}/>
          ))}
        </div>
      </div>

    </div>
  );
}

export default OddsTable; 