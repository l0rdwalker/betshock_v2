import React, {createContext, useState, useEffect} from "react";

const TimeContext = createContext();

export const TimeContextProvider = ({children}) => {
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);
        
        return () => clearInterval(interval);
    }, []);

    return (
        <TimeContext.Provider value={currentTime}>
            {children}
        </TimeContext.Provider >
    );
};

export default TimeContext;



