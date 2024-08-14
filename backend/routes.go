package main

import (
	"arbie/internal_new"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	/*
		router.GET("/next_2_go", internal.Get_Next_2_go)
		router.GET("/get_day_races/:date", internal.Get_Day_Races_Internal)
		router.GET("/get_race_details/:race_id", internal.Get_Race_View)
		router.GET("/get_related_races/:race_id", internal.Get_Other_Meet_Races)
		router.GET("/get_race_entrants/:race_id", internal.Get_Race_Entrants)
		router.GET("/get_entrant_price_history/:entrant_id", internal.Get_Entrant_Price_History)
	*/

	router.GET("/get_day_races/:timestamp", internal_new.Get_Day_Races)
	router.GET("/next_2_go", internal_new.Get_Next_2_go)
	router.GET("/get_race_details/:race_id", internal_new.Get_Race_View)
	router.GET("/get_related_races/:race_id", internal_new.Get_Other_Meet_Races)
	router.GET("/get_entrant_price_history/:entrant_id", internal_new.Get_Entrant_Price_History)
	router.GET("/get_race_entrants/:race_id", internal_new.Get_Race_Entrants)

	router.Run("localhost:8080")
}
