import React , {useState, useEffect, useContext} from 'react';
import { useLoaderData, useParams } from 'react-router-dom';

import TrackImage from '../../../../static_resources/temp_track.jpg'

import './race_header.css'

const RaceHeader = (props) => {
  const [race_title,set_race_title] = useState("");

  useEffect(() => {
    set_race_title(props.track_name)
  },[props.track_name])

  return (
    <div class="race_banner_wpr">
      <div class="race_banner_details deets">
        <h1>{race_title}</h1>
      </div>
      <div class="race_banner_details">
        <img src={TrackImage} alt="Smiley face"/>
      </div>
    </div>
  );
}

export default RaceHeader; 