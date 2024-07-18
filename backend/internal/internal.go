package internal

import (
	"arbie/db"

	"github.com/gin-gonic/gin"
)

func Get_Day_Races_Internal(c *gin.Context) {
	db.Get_Day_Races(c)
}

func Get_Next_2_go(c *gin.Context) {
	//t, err := time.Parse(time.RFC3339, "2020-06-27T09:34:01Z") //In place of getting the current date

	db.Get_Next_2_Go_Races(c)
}
