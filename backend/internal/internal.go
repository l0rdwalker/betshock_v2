package internal

import (
	"arbie/db"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

func Get_Day_Races_Internal(c *gin.Context) {
	day_time, err := strconv.Atoi(c.Param("date"))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
	}
	db.Get_Day_Races(c, day_time)
}

func Get_Next_2_go(c *gin.Context) {
	db.Get_Next_2_Go_Races(c)
}

func Get_Race_View(c *gin.Context) {
	race_id, err := strconv.Atoi(c.Param("race_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "bad parameter"})
	}

	possible_races := db.Get_Race_Details(c, race_id)
	var race *db.Complete_Race
	if len(possible_races) > 0 {
		race = &possible_races[0]
	} else {
		c.JSON(http.StatusBadRequest, gin.H{"error": "bad parameter"})
		return
	}

	entrants := db.Get_Race_Entrants(c, race_id)
	for idx := range entrants {
		entrants[idx].Prices = db.Get_Platform_Offerings(c, entrants[idx].Entrant_id)
	}

	race.Entrants = entrants
	c.IndentedJSON(http.StatusOK, race)
}

func Get_Other_Meet_Races(c *gin.Context) {
	race_id, err := strconv.Atoi(c.Param("race_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "bad parameter"})
	}
	db.Get_Related_Race_Rounds(c, race_id)
}

func Get_Race_Entrants(c *gin.Context) {
	race_id, err := strconv.Atoi(c.Param("race_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "bad parameter"})
	}
	data := db.Get_Race_Entrants(c, race_id)
	c.IndentedJSON(http.StatusOK, data)
}

func Get_Entrant_Price_History(c *gin.Context) {
	entrant_id, err := strconv.Atoi(c.Param("entrant_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "bad parameter"})
	}
	data := db.Get_Entrant_Timeseries_Prices(c, entrant_id)
	c.IndentedJSON(http.StatusOK, data)
}
