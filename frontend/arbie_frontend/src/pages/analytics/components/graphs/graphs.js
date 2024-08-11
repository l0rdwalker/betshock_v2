import React , {useState, useEffect, useContext} from 'react';
import EntrantChart from '../graph/graph';

import './graphs.css'

const EntrantGraphs = (props) => {
    const [entrants, set_entrants] = useState([]);
    const [non_filtered, set_non_filtered] = useState([]);

    useEffect(() => {
        fetch(`http://127.0.0.1:8080/get_race_entrants/${props.race_id}`)
        .then(data => data.json())
        .then(data => set_non_filtered(data))
        .catch(err => console.log(err))
    },[props.race_id])

    useEffect(() => {
        let non_screated_entrants = [];
        non_filtered.forEach((entrant,idx) => {
            if (entrant['Is_scratched'] == 0) {
                non_screated_entrants.push(entrant);
            }
        })
        set_entrants(non_screated_entrants);
    },[non_filtered]);

    return (
      <div class='entrant_line_graph_wpr'>
		{
            entrants.map((entrant,idx) => (
                <EntrantChart entrant_name={entrant['Entrant_name']} entrant_id={entrant['Entrant_id']}/>
            ))
        }
      </div>
    );
}

export default EntrantGraphs; 