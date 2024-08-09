import React , {useState, useEffect, useContext} from 'react';
import {useNavigate} from 'react-router-dom';

import SvgManager from '../svg_manager/SvgManager';

import ProfileImage  from '../../static_resources/profile_placeholder.svg'
import MoneyIcon from '../../static_resources/money.svg'
import Bell from '../../static_resources/bell.svg'
import Home from '../../static_resources/home.svg'

import './header.css'

const Header = (props) => {
  const navigate = useNavigate(); 
  
  return (
    <div class='header_wpr'>

      <div class='header_partition home_header'>
        <div class='header_icon_wpr force_width'>
          <div onClick={()=>navigate(`/`)} class='icon_wpr'>
            <SvgManager height={35} width={35} src={Home}/>
          </div>
        </div>
      </div>
      
      <div class='header_partition controls_header'>
        <div class='header_icon_wpr'>
          <div class='icon_wpr'>
            <SvgManager height={35} width={35} src={Bell}/>
          </div>
          <div class='icon_wpr'>
            <SvgManager height={35} width={35} src={MoneyIcon}/>
          </div>
          <div class='icon_wpr'>
            <SvgManager height={35} width={35} src={ProfileImage}/>
          </div>
        </div>
      </div>



    </div>
  );
}

export default Header; 