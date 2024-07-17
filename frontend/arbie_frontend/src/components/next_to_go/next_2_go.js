import React , {useState, useEffect} from 'react';
import Next2GoTile from './next_2_go_tile/next_2_go_tile.js'

import './next_2_go.css'

const Next2go = () => {
  const [data,setData] = useState([{'Track_name':'None','Round':0,'Start_time':"idk"}]);

  useEffect(() => {
    fetch('http://127.0.0.1:8080/next_2_go')
    .then(response => response.json())
    .then(res => setData(res))
    .catch(error => console.error(error))
  },[]);

  useEffect(() => {
    console.log(data);
  },data);

  return (
    <div class='next_2_go_container'>
        <div class='next_2_go_header'>
            <div class='header_txt '>
              <p>Next To Jump</p>
            </div>
        </div>
        <div class='next_2_go_content'>
            <div class='next_2_go_content_padding'>
                {data.map((race, index) => (
                  <Next2GoTile key={index} race_data={race} />
                ))}
            </div>
        </div>
    </div>
  );
}

export default Next2go;
