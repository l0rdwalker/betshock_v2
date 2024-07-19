import React , {useState, useEffect, useContext} from 'react';
import './SvgManager.css'

const SvgManager = (props) => {

  return (
    <div class="svg_manager">
      <svg viewBox='0 0 25 24'>
        <path fill={props.color} d={props.path}/>
      </svg>
    </div>
  );
}

export default SvgManager;
