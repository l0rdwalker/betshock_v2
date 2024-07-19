package db

import (
	"database/sql"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"
)

type race struct {
	Track_name string    `json:"Track_name"`
	Round      int       `json:"Round"`
	Start_time time.Time `json:"Start_time"`
}

type on_day_meet struct {
	Track_name string `json:"Track_name"`
	Races      []race `json:"Races"`
}

const (
	host     = "127.0.0.1"
	port     = 5432
	user     = "postgres"
	password = "test"
	dbname   = "arbie_v3.1"
)

func init_connection(c *gin.Context) *sql.DB {
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		fmt.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to connect to the database"})

	}

	return db
}

func close_connection(db *sql.DB, c *gin.Context) {
	db.Close()
}

func exec_query(query string, c *gin.Context) *sql.Rows {
	db := init_connection(c)

	rows, err := db.Query(query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to execute query"})
		close_connection(db, c)
		return nil
	}
	close_connection(db, c)
	return rows
}

func Get_Next_2_Go_Races(c *gin.Context) {
	rows := exec_query("SELECT track_name,round,start_time FROM race JOIN track ON race.track_id = track.track_id WHERE start_time > NOW() ORDER BY start_time ASC;", c)

	all_races := make([]race, 0)
	for rows.Next() {
		var cur_race race
		if err := rows.Scan(&cur_race.Track_name, &cur_race.Round, &cur_race.Start_time); err != nil {
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

func Get_Day_Races(c *gin.Context, date int) {
	timestamp := int64(date)
	seconds := timestamp / 1000
	dateTime := time.Unix(seconds, 0)
	isoFormat := dateTime.Format(time.RFC3339)

	rows := exec_query("SELECT DISTINCT track_name FROM race JOIN track ON race.track_id = track.track_id WHERE DATE(start_time) = DATE('"+isoFormat+"');", c)
	races := make([]on_day_meet, 0)
	if rows != nil {
		for rows.Next() {
			var single_race_name on_day_meet
			if err := rows.Scan(&single_race_name.Track_name); err != nil {
				return
			}

			meet_race := make([]race, 0)
			meet_race_rows := exec_query("SELECT track_name,round,start_time FROM race JOIN track ON race.track_id = track.track_id WHERE DATE(start_time) = DATE('"+isoFormat+"') AND track_name = '"+single_race_name.Track_name+"' ORDER BY round ASC;", c)
			for meet_race_rows.Next() {
				var cur_race race
				if err := meet_race_rows.Scan(&cur_race.Track_name, &cur_race.Round, &cur_race.Start_time); err != nil {
					return
				}
				meet_race = append(meet_race, cur_race)
			}
			single_race_name.Races = meet_race
			races = append(races, single_race_name)
		}
	}
	c.IndentedJSON(http.StatusOK, races)
}
