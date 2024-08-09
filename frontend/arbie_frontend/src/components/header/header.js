import React , {useState, useEffect, useContext} from 'react';
import SvgManager from '../svg_manager/SvgManager';

import ProfileImage  from '../../static_resources/profile_placeholder.svg'
import MoneyIcon from '../../static_resources/money.svg'
import Bell from '../../static_resources/bell.svg'

import './header.css'

const Header = (props) => {
  return (
    <div class='header_wpr'>
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
  );
}

export default Header; 