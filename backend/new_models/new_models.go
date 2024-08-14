package new_models

import "time"

type Price struct {
	Odds        float32   `json:"Odds"`
	Record_Time time.Time `json:"Record_Time"`
}

type Prices struct {
	Platform_Name      string  `json:"Platform_Name"`
	Current_Price      Price   `json:"Current_Price"`
	Price_Fluctuations []Price `json:"Price_Fluctuations"`
}

type Entrant struct {
	Entrant_Id   int      `json:"Entrant_Id"`
	Entrant_Name string   `json:"Entrant_Name"`
	Is_Scratched bool     `json:"Is_Scratched"`
	Odds         []Prices `json:"Odds"`
}

type Race struct {
	Race_Id    int       `json:"Race_Id"`
	Track_Id   int       `json:"Track_Id"`
	Track_Name string    `json:"Track_Name"`
	Round      int       `json:"Round"`
	Start_Time time.Time `json:"Start_Time"`
	Entrants   []Entrant `json:"Entrants"`
}

type Meet struct {
	Track_Id   int       `json:"Race_Id"`
	Track_Name string    `json:"Track_Name"`
	Meet_Date  time.Time `json:"Meet_Date"`
	Races      []Race    `json:"Races"`
}
