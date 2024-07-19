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
	//t, err := time.Parse(time.RFC3339, "2020-06-27T09:34:01Z") //In place of getting the current date
	db.Get_Next_2_Go_Races(c)
}
