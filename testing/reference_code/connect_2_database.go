package main

import (
	"database/sql"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"
)

type race struct {
	TrackID          int    `json:"track_id"`
	SurfaceCondition string `json:"surface_condition"`
	SurfaceRating    int    `json:"surface_rating"`
	Distance         int    `json:"distance"`
	Round            int    `json:"round"`
	RaceID           int    `json:"race_id"`
}

const (
	host     = "127.0.0.1"
	port     = 5432
	user     = "postgres"
	password = "test"
	dbname   = "races"
)

func get_some_races(c *gin.Context) {
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to connect to the database"})
		return
	}
	defer db.Close()

	rows, err := db.Query("SELECT track_id, surface_confition, surface_rating, distance, round, race_id FROM race;")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to execute query"})
		return
	}
	defer rows.Close()

	all_races := make([]race, 0)
	for rows.Next() {
		var cur_race race
		if err := rows.Scan(&cur_race.TrackID, &cur_race.SurfaceCondition, &cur_race.SurfaceRating, &cur_race.Distance, &cur_race.Round, &cur_race.RaceID); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
			return
		}
		all_races = append(all_races, cur_race)
	}

	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error occurred during row iteration"})
		return
	}

	c.IndentedJSON(http.StatusOK, all_races)
}

func main() {
	router := gin.Default()

	router.GET("/get_races", get_some_races)

	router.Run("localhost:8080")
}
