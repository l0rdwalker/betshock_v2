package internal_new

import (
	"arbie/db_new"
	"arbie/new_models"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

func Throw_Error(msg string, c *gin.Context) {
	c.IndentedJSON(http.StatusBadRequest, gin.H{"err": msg})
}

func create_meet_list(race_id_list []int, c *gin.Context) []new_models.Meet {
	meets := make(map[int]new_models.Meet)
	for _, ele := range race_id_list {
		curr_race, err := db_new.Get_Race_By_ID(ele)
		if err != nil {
			Throw_Error("Could parse race by id", c)
		}

		if val, ok := meets[curr_race.Track_Id]; ok {
			val.Races = append(val.Races, curr_race)
			meets[curr_race.Track_Id] = val
		} else {
			curr_meet := new_models.Meet{Track_Id: curr_race.Track_Id, Track_Name: curr_race.Track_Name, Meet_Date: curr_race.Start_Time, Races: make([]new_models.Race, 0)}
			curr_meet.Races = append(curr_meet.Races, curr_race)

			meets[curr_meet.Track_Id] = curr_meet
		}
	}

	listed_meets := make([]new_models.Meet, 0)
	for key := range meets {
		listed_meets = append(listed_meets, meets[key])
	}

	return listed_meets
}

func Get_Day_Races(c *gin.Context) {
	day_time, err := strconv.Atoi(c.Param("timestamp"))
	if err != nil {
		c.IndentedJSON(http.StatusBadRequest, gin.H{"err": "Bad date parameter"})
	}

	dateTime := time.Unix(int64(day_time), 0)
	isoFormat := dateTime.Format(time.RFC3339)

	day_race_ids, err := db_new.Get_RaceIDs_On_Day(isoFormat)
	if err != nil {
		Throw_Error("Couldn't load race_ids", c)
	}

	on_day_meets := create_meet_list(day_race_ids, c)
	c.IndentedJSON(http.StatusOK, on_day_meets)

}

func Get_Next_2_go(c *gin.Context) {
	next_2_go_raceIds, err := db_new.Get_Next_2_Go_RaceIds()
	if err != nil {
		Throw_Error("Couldn't get race_ids", c)
	}

	next_2_go_races := make([]new_models.Race, 0)
	for _, race_id := range next_2_go_raceIds {
		curr_race, err := db_new.Get_Race_By_ID(race_id)
		if err != nil {
			Throw_Error("Couldn't load race by id", c)
		}
		next_2_go_races = append(next_2_go_races, curr_race)
	}

	c.IndentedJSON(http.StatusOK, next_2_go_races)
}

func Get_Race_View(c *gin.Context) {
	race_id, err := strconv.Atoi(c.Param("race_id"))
	if err != nil {
		Throw_Error("Cannot identify race.", c)
	}

	race, err := db_new.Get_Race_By_ID(race_id)
	if err != nil {
		Throw_Error("Cannot identify race.", c)
	}

	entrant_ids, err := db_new.Get_EntrantIDs_By_RaceID(race_id)
	if err != nil {
		Throw_Error("Cannot identify entrants.", c)
	}

	for _, entrant_id := range entrant_ids {
		entrant, err := db_new.Get_Entrant_By_ID(entrant_id)
		if err != nil {
			Throw_Error("Couldn't find entrant details.", c)
		}
		Odds, err := db_new.Get_Price_By_EntrantID(entrant_id)
		if err != nil {
			Throw_Error("Couldn't identidy platform odds", c)
		}
		entrant.Odds = Odds
		race.Entrants = append(race.Entrants, entrant)
	}

	c.IndentedJSON(http.StatusOK, race)
}

func Get_Other_Meet_Races(c *gin.Context) {
	race_id, err := strconv.Atoi(c.Param("race_id"))
	if err != nil {
		Throw_Error("Bad paramter", c)
	}

	related_race_ids, err := db_new.Get_Related_RaceIds(race_id)
	if err != nil {
		Throw_Error("Couldn't find race ids.", c)
	}

	races := make([]new_models.Race, 0)
	for _, race_id := range related_race_ids {
		curr_race, err := db_new.Get_Race_By_ID(race_id)
		if err != nil {
			Throw_Error("Cannot find race by its id", c)
		}
		races = append(races, curr_race)
	}

	c.IndentedJSON(http.StatusOK, races)
}

func Get_Race_Entrants(c *gin.Context) {
	race_id, err := strconv.Atoi(c.Param("race_id"))
	if err != nil {
		Throw_Error("Bad parameter", c)
	}

	entrant_ids, err := db_new.Get_EntrantIDs_By_RaceID(race_id)
	if err != nil {
		Throw_Error("Bad race_id", c)
	}

	entrants := make([]new_models.Entrant, 0)
	for _, entrant_id := range entrant_ids {
		entrant, err := db_new.Get_Entrant_By_ID(entrant_id)
		if err != nil {
			Throw_Error("Bad entrant_id", c)
		}
		entrants = append(entrants, entrant)
	}

	c.IndentedJSON(http.StatusOK, entrants)
}

func Get_Entrant_Price_History(c *gin.Context) {
	entrant_id, err := strconv.Atoi(c.Param("entrant_id"))
	if err != nil {
		Throw_Error("Bad parameter", c)
	}

	entrant, err := db_new.Get_Entrant_By_ID(entrant_id)
	if err != nil {
		Throw_Error("Couldn't identify entrant", c)
	}

	entrant_prices, err := db_new.Get_Price_By_EntrantID(entrant_id)
	if err != nil {
		Throw_Error("Couldn't identidy entrant prices", c)
	}

	entrant.Odds = entrant_prices
	c.IndentedJSON(http.StatusOK, entrant)
}
