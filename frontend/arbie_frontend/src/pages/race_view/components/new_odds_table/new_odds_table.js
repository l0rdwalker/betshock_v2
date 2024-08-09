import React , {useState, useEffect, useContext} from 'react';
import { json, useLoaderData, useParams } from 'react-router-dom';

import OddsTableRow from './odds_table_row/odds_table_row';

import './new_odds_table.css'

const NewOddsTable = (props) => {
  const [platform_offerings, set_platform_offerings] = useState([]);
  const [platform_themes, set_platform_themes] = useState([]);
  const [entrants, set_entrants] = useState([]);

  useEffect(() => {
    const entrants = props.entrants || [];
    
    set_entrants([]);
    set_platform_offerings([]);
    set_entrants([]);

    const unionPlatforms = new Set();
    const platformThemes = new Set();
  
    const scratched_entrants = [];
    const active_entrants = [];

    entrants.forEach(entrant => {
      entrant['Prices'].forEach(platformOffering => {
        unionPlatforms.add(platformOffering['Platform']);
        platformThemes.add(platformOffering['Platform_colour']);
      });

      if (entrant['Is_scratched'] == 1) {
        scratched_entrants.push(entrant);
      } else {
        active_entrants.push(entrant);
      }
    });

    const sorted_entrants = [];
    active_entrants.forEach(entrant => {
      sorted_entrants.push(entrant);
    });
    scratched_entrants.forEach(entrant => {
      sorted_entrants.push(entrant);
    });
  
    const platformsArray = Array.from(unionPlatforms);
    const platformThemesArray = Array.from(platformThemes);

    set_platform_themes(platformThemesArray);
    set_platform_offerings(platformsArray);
    set_entrants(sorted_entrants);
  },[props.entrants]);

  return (
    <div class='table_wpr'>
          
      <table>
        <tr>
          <th></th>
          {
            platform_offerings.map((element,idx) => (
              <th style={{backgroundColor:platform_themes[idx]}} class="platform_name_table">
                <p>{element}</p>
              </th>
            ))
          }
        </tr>

        {
          entrants.map((element,idx) => (
            <OddsTableRow entrant={element} platform_ordering={platform_offerings}/>
          ))
        }
      </table>

    </div>
  );
}

export default NewOddsTable; 