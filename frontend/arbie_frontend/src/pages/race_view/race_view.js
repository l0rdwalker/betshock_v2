import React , {useState, useEffect, useContext} from 'react';
import { useLoaderData, useParams } from 'react-router-dom';

import NewOddsTable from './components/new_odds_table/new_odds_table';
import RaceHeader from './components/race_banner/race_view';
import RelatedRace from './components/related_races/related_races';

import './race_view.css'

const RaceView = (props) => {
  const { race_id } = useParams();
  const [race_data, set_race_data] = useState({});

  useEffect(()=>{
    fetch(`http://127.0.0.1:8080/get_race_details/${race_id}`)
    .then(data => data.json())
    .then(data => set_race_data(data))
    .catch(err => console.log(err))
  },[race_id]);

  return (
    <>
      <RelatedRace race_id={race_id} />
      <RaceHeader track_name={`${race_data['Track_name']} R${race_data['Round']}`}/>
      <NewOddsTable entrants={race_data['Entrants']} />
    </>
  );
}

export default RaceView; 
