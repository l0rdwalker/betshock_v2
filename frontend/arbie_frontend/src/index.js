import React from 'react';
import ReactDOM from 'react-dom/client';
import Header from './components/header/header';

import {TimeContextProvider} from './components/counter_time_context/current_time_context';
import {BrowserRouter, Routes, Route, Link, NavLink} from 'react-router-dom';

import Home from './pages/home/home';
import RaceView from './pages/race_view/race_view';
import race_entrant_details from './pages/race_view/race_view'

import './index.css';
import './master_style.css'

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <TimeContextProvider>

        <BrowserRouter>
          <Header />
            <div class="test_container">
              <Routes>
                <Route index element={<Home/>}/>

                <Route path="race">
                  <Route 
                    path=":race_id" 
                    element={<RaceView/>}
                  />
                </Route>

              </Routes>
              </div>
        </BrowserRouter>

  </TimeContextProvider>
);
