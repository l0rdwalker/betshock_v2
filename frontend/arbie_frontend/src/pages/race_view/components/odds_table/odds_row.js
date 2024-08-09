import React , {useState, useEffect, useContext} from 'react';
import { json, useLoaderData, useParams } from 'react-router-dom';

import './odds_row.css'

const OddsRow = (props) => {
    const [entrant_data, set_entrant_data] = useState([]);
    const [index_cache, set_index_cache] = useState([]);

    useEffect(() => {
        var price_data = props.entrant_data;
        var index_cache = props.index_cache;
        var temp_list = Array(price_data.length);

        for (var idx = 0; idx < price_data.length; idx++) {
            temp_list[index_cache[price_data[idx]['Platform']]] = price_data[idx]['Price']
        }

        set_entrant_data(temp_list);
    },[props.entrant_data])

    return (
        <div class='entrant_odds_wpr'>
          {entrant_data.map((entrant, index) => (
            <div class='price_wpr'>
                <p>{entrant}</p>
            </div>
          ))}
        </div>
    );
}

export default OddsRow; 