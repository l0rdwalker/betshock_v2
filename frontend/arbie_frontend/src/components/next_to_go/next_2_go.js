import React , {useState, useEffect} from 'react';
import Next2GoTile from './next_2_go_tile/next_2_go_tile.js'
import {useNavigate} from 'react-router-dom';

import './next_2_go.css'

const Next2go = (props) => {
  const [data,setData] = useState([]);
  const navigate = useNavigate(); 

  useEffect(() => {
    fetch('http://127.0.0.1:8080/next_2_go')
    .then(response => response.json())
    .then(res => setData(res))
    .catch(error => console.error(error))
  },[]);

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
                  <div onClick={()=>navigate(`/race/${race['Race_id']}`)}>
                    <Next2GoTile key={race[2]} race_data={race} />                  
                  </div>
                ))}
            </div>
        </div>
    </div>
  );
}

export default Next2go;
