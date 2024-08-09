import React , {useState, useEffect, useContext} from 'react';
import './SvgManager.css'

const SvgManager = (props) => {
  return (
    <div class="svg_manager">
      <img style={{height:props.height,width:props.width}} src={props.src}/>
    </div>
  );
}

export default SvgManager;
