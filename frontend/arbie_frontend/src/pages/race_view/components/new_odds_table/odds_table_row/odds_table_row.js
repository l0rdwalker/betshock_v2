import React , {useState, useEffect, useContext} from 'react';
import { json, useLoaderData, useParams } from 'react-router-dom';

import './odds_table_row.css'

const OddsTableRow = (props) => {
  const [entrant_name, set_entrant_name] = useState("");
  const [price_list, set_price_list] = useState([]);
  const [visibility,set_visibility] = useState('');

  function get_relevent_platform_price(price_data_array,desired_platform) {
    for (let idx = 0; idx < price_data_array.length; idx++) {
      if (price_data_array[idx]['Platform'] == desired_platform) {
        return price_data_array[idx]['Price'];
      }
    }
    return "--";
  }

  useEffect(() => {
    const entrant_name = props.entrant['Entrant_name'];
    const price_options = props.entrant['Prices'];
    const platform_template = props.platform_ordering;

    let prelim_price_list = [];
    for (var idx = 0; idx < platform_template.length; idx++) {
      let price = get_relevent_platform_price(price_options,platform_template[idx]);
      prelim_price_list.push(price);
    }

    set_entrant_name(entrant_name);
    set_price_list(prelim_price_list);

    if (props.entrant['Is_scratched'] == 1) {
      set_visibility('disable')
    } else {
      set_visibility('');
    }

  },[props.entrant,props.platform_ordering]);

  return (
    <tr class={visibility}>
      <td class="entrant_name_table">
        <p>{entrant_name}</p>
      </td>
      
      {
        price_list.map((element,idx) => (
          <td class="price_entry">{element}</td>
        ))
      }
    </tr>
  );
}

export default OddsTableRow; 