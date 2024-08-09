import React , {useState, useEffect, useContext} from 'react';
import { useLoaderData, useParams } from 'react-router-dom';

import RaceHeader from './components/race_header/race_header';
import OddsTable from './components/odds_table/odds_table'

import './race_view.css'

const RaceView = (props) => {
  const { race_id } = useParams();
  const [race_data, set_race_data] = useState({});

  useEffect(()=>{
    fetch(`http://127.0.0.1:8080/get_race_details/${race_id}`)
    .then(data => data.json())
    .then(data => set_race_data(data))
    .then(data => console.log(data))
    .catch(err => console.log(err))
  },[race_id])


  useEffect(()=>{
    console.log(race_data);
  },[race_data])

  return (
    <>
      <RaceHeader track_name={`${race_data['Track_name']} R${race_data['Round']}`}/>
      <OddsTable entrants={race_data['Entrants']}/>
    </>
  );
}

export default RaceView; 

//export const race_entrant_details = async ({params}) => {
//  const {race_id} = params;
//  const res = await fetch(`http://127.0.0.1:8080/get_race_details/${race_id}`);
//  return res.json()
//}