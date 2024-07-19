import React from 'react';
import ReactDOM from 'react-dom/client';

import Next2go from './components/next_to_go/next_2_go'
import OnDay from './components/on_day/on_day';

import {TimeContextProvider} from './components/counter_time_context/current_time_context';

import './index.css';
import './master_style.css'

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <TimeContextProvider>
    <React.StrictMode>
        <div class="test_container">
          <Next2go />
          <br></br>
          <OnDay />
        </div>
    </React.StrictMode>
  </TimeContextProvider>
);
