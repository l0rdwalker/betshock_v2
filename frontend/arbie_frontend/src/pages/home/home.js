import React , {useState, useEffect, useContext} from 'react';
import Next2go from '../../components/next_to_go/next_2_go'
import OnDay from '../../components/on_day/on_day'
import './home.css'

const Home = (props) => {
  return (
    <>
        <div class="basic_margin">
          <Next2go />
        </div>
        <div class='basic_margin'>
          <OnDay />
        </div>
    </>
  );
}

export default Home; 